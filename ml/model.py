import torch
from torch import nn
class CarePulseLSTM(nn.Module):
    def __init__(self,input_size=6,hidden_size=64,layers=2):
        super().__init__(); self.lstm=nn.LSTM(input_size,hidden_size,layers,batch_first=True,dropout=.15); self.head=nn.Sequential(nn.LayerNorm(hidden_size),nn.Linear(hidden_size,32),nn.ReLU(),nn.Linear(32,1))
    def forward(self,x): return self.head(self.lstm(x)[0][:,-1,:]).squeeze(-1)
