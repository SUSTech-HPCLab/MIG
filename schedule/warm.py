import torch
import time
def average_without_min_max(numbers):
    if len(numbers) <= 2:
        raise ValueError("List should contain at least 3 elements")

    max_val = max(numbers)
    min_val = min(numbers)
    
    numbers.remove(max_val)
    numbers.remove(min_val)
    
    return sum(numbers) / len(numbers)

def unet():
    return torch.hub.load('mateuszbuda/brain-segmentation-pytorch', 'unet',
    in_channels=3, out_channels=1, init_features=32, pretrained=True)

model = unet
model = model().cuda(0).eval()

input =  torch.randn(32, 3, 256, 256).cuda(0)

torch.cuda.synchronize()
time_list = []
with torch.no_grad():
    for i in range(0, 5):
        start = time.time()
        output= model(input).cpu()
        time_list.append(time.time() - start)

