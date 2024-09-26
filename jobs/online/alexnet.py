

import torch
import time

def alexnet():
    return torch.hub.load('pytorch/vision:v0.10.0', 'alexnet', pretrained=True)
