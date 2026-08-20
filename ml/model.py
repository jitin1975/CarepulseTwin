import torch
from torch import nn
class CarePulseLSTM(nn.Module):
    def __init__(self,n=6,h=48,layers=1):
        super().__init__(); self.lstm=nn.LSTM(n,h,layers,batch_first=True); self.head=nn.Sequential(nn.LayerNorm(h),nn.Linear(h,24),nn.ReLU(),nn.Linear(24,1))
    def forward(self,x):
        y,_=self.lstm(x); return self.head(y[:,-1]).squeeze(-1)
