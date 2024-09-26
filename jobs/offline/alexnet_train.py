
import torch.nn as nn


class AlexNet(nn.Module):
    def __init__(self, width_mult=1):
        super(AlexNet, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.MaxPool2d(kernel_size=2, stride=2),  
            nn.ReLU(inplace=True),
        )

        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.ReLU(inplace=True),
        )

        self.layer3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
        )

        self.layer4 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
        )
        self.layer5 = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.ReLU(inplace=True),
        )

        self.fc1 = nn.Linear(256 * 3 * 3, 1024)
        self.fc2 = nn.Linear(1024, 512)
        self.fc3 = nn.Linear(512, 10)

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.layer5(x)
        # print(x.shape)
        x = x.view(-1, 256 * 3 * 3)
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)

        return x


# !/usr/bin/python3
# -*- coding:utf-8 -*-
# Author:WeiFeng Liu
# @Time: 2021/11/4 下午12:59

import time
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torchvision import datasets
from torch.utils.data import DataLoader
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 设置超参数
epochs = 20
batch_size = 256
lr = 0.01

transform = transforms.Compose([
    transforms.Resize([32,32]),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    # transforms.Normalize(mean=[.5,.5,.5],std=[.5,.5,.5]),
    ])


cifar_train = datasets.CIFAR10('/home/zbw/MIG/MIG_Schedule/jobs/offline/data/cifar', True, transform=transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ]), download=True)

train_loader = DataLoader(cifar_train,
                          batch_size=batch_size,
                          shuffle = True,)



def alxnet_train():

    net = AlexNet().cuda(device)
    loss_func = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(),lr=lr,momentum=0.9)

    train_loss = []
    for epoch in range(epochs):
       
        sum_loss = 0
        for batch_idx,(x,y) in enumerate(train_loader):
            x = x.to(device)
            y = y.to(device)
            pred = net(x)

            optimizer.zero_grad()
            loss = loss_func(pred,y)
            loss.backward()
            optimizer.step()
            sum_loss += loss.item()
            train_loss.append(loss.item())




