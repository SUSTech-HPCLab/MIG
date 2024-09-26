from alexnet import alexnet
from bert import BertModel
from deeplabv3 import deeplabv3
from inception_ve import inception_v3
from mobilenet_v2 import mobilenet
from resnet import resnet50,resnet101,resnet152
from unet import unet
from vgg_splited import vgg16,vgg19
import time
import argparse
import numpy as np
import torch

model_list = {
    "resnet50": resnet50,
    "resnet101": resnet101,
    "resnet152": resnet152,
    "vgg19": vgg19,
    "vgg16": vgg16,
    "inception_v3": inception_v3,
    'unet': unet,
    'deeplabv3':deeplabv3,
    'mobilenet_v2': mobilenet,
    # 'open_unmix':open_unmix,
    'alexnet': alexnet,
    'bert': BertModel,
}

input_list = {
    "resnet50": [3, 244, 244],
    "resnet101": [3, 244, 244],
    "resnet152": [3, 244, 244],
    "vgg19": [3, 244, 244],
    "vgg16": [3, 244, 244],
    "inception_v3": [3, 299, 299],
    "unet": [3,256,256],
    'deeplabv3': [3,256,256],
    'mobilenet_v2': [3,244,244],
    # 'open_unmix': [2,100000],
    'alexnet': [3,244,244],
    'bert': [1024,768],
}
    
def get_input(model_name, k):
    input = input_list.get(model_name)
    if model_name == 'bert':
        input = torch.LongTensor(np.random.rand(k, 1024, 768)).half().cuda(0)
        masks =  torch.LongTensor(np.zeros((k, 1, 1, 1024))).half().cuda(0)
        return input,masks
    if len(input) == 3:
        return torch.randn(k, input[0], input[1], input[2]).cuda(0)
    else:
        return torch.randn(k, input[0], input[1]).cuda(0)
    
def average_without_min_max(numbers):
    if len(numbers) <= 2:
        raise ValueError("List should contain at least 3 elements")

    max_val = max(numbers)
    min_val = min(numbers)
    
    numbers.remove(max_val)
    numbers.remove(min_val)
    
    return sum(numbers) / len(numbers)
    
parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
parser.add_argument("--batch", type=int, default=32)
parser.add_argument("--epoch", type=int, default=32)
parser.add_argument("--config", type=str, required=False)
args = parser.parse_args()

epoch = args.epoch
model_name = args.model
batch_size = args.batch
config = args.config

if model_name == 'bert':  
    model = model_list.get(model_name)
    model = model().half().cuda(0).eval()
else:
    model = model_list.get(model_name)
    model = model().cuda(0).eval()


if model_name == 'bert':
    input,masks = get_input(model_name, batch_size)
else:
    input = get_input(model_name, batch_size)

torch.cuda.synchronize()
time_list = []
with torch.no_grad():
    for i in range(0, epoch):
        start = time.time()

        if model_name == 'bert':
            output= model.run(input,masks,0,12).cpu()
        elif model_name == 'deeplabv3':
            output= model(input)['out'].cpu()
        else:
            output=model(input).cpu()

        time_list.append(time.time() - start)


    





    
