import torch
import torchvision
import ultralytics
from ultralytics import YOLO

print('--- PyTorch Verification ---')
print(f'torch version: {torch.__version__}')
print(f'torchvision version: {torchvision.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')

print('\n--- Ultralytics Verification ---')
print(f'ultralytics version: {ultralytics.__version__}')
print('YOLO class imported successfully.')
