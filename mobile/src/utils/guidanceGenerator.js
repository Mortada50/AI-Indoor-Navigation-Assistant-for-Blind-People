// Ported from backend/modules/guidance_generator.py

const CLASS_MAP = {
  "cpu": "وحدة المعالجة المركزية",
  "door": "باب",
  "keyboard": "لوحة مفاتيح",
  "monitor": "شاشة",
  "mouse": "فأرة",
  "blackboard": "سبورة",
  "chair": "كرسي",
  "laptop": "حاسوب محمول",
  "stairs": "درج",
  "table": "طاولة",
  "window": "نافذة"
};

const POSITION_MAP = {
  "left": "على اليسار",
  "center": "أمامك",
  "right": "على اليمين"
};

const PROXIMITY_MAP = {
  "near": "قريب",
  "medium": "متوسط القرب",
  "far": "بعيد نسبيًا"
};

const SCENE_MAP = {
  "classroom": "قاعة دراسية",
  "computer laboratory": "معمل حاسوب",
  "unknown indoor space": "بيئة داخلية غير محددة"
};

const PRIORITY_CLASSES = { "door": 1, "stairs": 2 };

function translateClass(className) {
  if (!className) return "";
  const normName = className.toLowerCase().trim();
  return CLASS_MAP[normName] || className;
}

export function generateGuidance(detections = [], sceneInference = null) {
  const validDetections = detections.filter(det => 
    det.class_name && 
    det.spatial?.horizontal_position && 
    det.distance?.proximity
  );

  const messages = [];
  const summaryParts = [];

  let sceneName = null;
  if (sceneInference && sceneInference.scene) {
    const rawScene = sceneInference.scene.toLowerCase();
    if (rawScene && rawScene !== "unknown indoor space") {
      sceneName = SCENE_MAP[rawScene] || rawScene;
      summaryParts.push(`أنت في ${sceneName}.`);
    }
  }

  if (validDetections.length === 0) {
    const msg = "لم يتم اكتشاف أجسام واضحة أمامك حاليًا.";
    if (summaryParts.length === 0) {
      summaryParts.push(msg);
    }
    return {
      summary: summaryParts.join(" ").trim(),
      messages: [],
      scene: sceneName || "بيئة داخلية غير محددة"
    };
  }

  // Deduplication and Aggregation
  const groupedObjects = {};
  for (const det of validDetections) {
    const cName = det.class_name.toLowerCase().trim();
    const hPos = det.spatial.horizontal_position;
    const prox = det.distance.proximity;
    
    const key = `${cName}|${hPos}|${prox}`;
    if (!groupedObjects[key]) {
      groupedObjects[key] = { count: 0, original: det, keyParts: { cName, hPos, prox } };
    }
    groupedObjects[key].count += 1;
  }

  // Sorting / Priority Ordering
  const sortedGroups = Object.values(groupedObjects).sort((a, b) => {
    const pScoreA = PRIORITY_CLASSES[a.keyParts.cName] || 99;
    const pScoreB = PRIORITY_CLASSES[b.keyParts.cName] || 99;
    
    if (pScoreA !== pScoreB) return pScoreA - pScoreB;

    const proxScoreA = a.keyParts.prox === "near" ? 1 : (a.keyParts.prox === "medium" ? 2 : 3);
    const proxScoreB = b.keyParts.prox === "near" ? 1 : (b.keyParts.prox === "medium" ? 2 : 3);

    if (proxScoreA !== proxScoreB) return proxScoreA - proxScoreB;

    const posScoreA = a.keyParts.hPos === "center" ? 1 : 2;
    const posScoreB = b.keyParts.hPos === "center" ? 1 : 2;

    return posScoreA - posScoreB;
  });

  // Sentence Generation
  for (const group of sortedGroups) {
    const { cName, hPos, prox } = group.keyParts;
    const count = group.count;
    
    let arName = translateClass(cName);
    if (count > 1) {
      arName = `${count} من ${arName}`;
    }
      
    const arPos = POSITION_MAP[hPos] || hPos;
    const arProx = PROXIMITY_MAP[prox] || prox;
    
    let msg = "";
    if (hPos === "center") {
      msg = `يوجد ${arName} ${arPos}، وهو ${arProx}.`;
    } else {
      msg = `يوجد ${arName} ${arProx} ${arPos}.`;
    }
      
    messages.push(msg);
  }

  // Build final summary string
  if (messages.length <= 3) {
    summaryParts.push(messages.join(" "));
  } else {
    summaryParts.push(messages.slice(0, 2).join(" "));
    summaryParts.push(`بالإضافة إلى ${messages.length - 2} عناصر أخرى في البيئة المحيطة.`);
  }

  return {
    summary: summaryParts.join(" ").trim(),
    messages: messages,
    scene: sceneName || SCENE_MAP["unknown indoor space"]
  };
}
