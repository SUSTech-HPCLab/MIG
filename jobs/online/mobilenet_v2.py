import torch
import time


def mobilenet():
    return torch.hub.load('pytorch/vision:v0.10.0', 'mobilenet_v2', pretrained=True).eval()

