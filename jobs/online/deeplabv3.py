import torch
import time 

def  deeplabv3():
    return torch.hub.load('pytorch/vision:v0.10.0', 'deeplabv3_resnet50', pretrained=True)



