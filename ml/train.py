import argparse
from pathlib import Path
import numpy as np, torch
from torch.utils.data import TensorDataset,DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score,f1_score
from ml.dataset import make_dataset,MEANS,STDS
from ml.model import CarePulseLSTM
def main():
 p=argparse.ArgumentParser(); p.add_argument('--epochs',type=int,default=10); p.add_argument('--out',default='ml/artifacts/carepulse_lstm.pt'); a=p.parse_args()
 X,y=make_dataset(); X=(X-MEANS)/STDS; Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=7,stratify=y)
 dev='cuda' if torch.cuda.is_available() else 'cpu'; m=CarePulseLSTM().to(dev); dl=DataLoader(TensorDataset(torch.tensor(Xtr),torch.tensor(ytr).float()),batch_size=128,shuffle=True); opt=torch.optim.Adam(m.parameters(),lr=2e-3); lossfn=torch.nn.BCEWithLogitsLoss()
 for ep in range(a.epochs):
  total=0;m.train()
  for xb,yb in dl:
   xb,yb=xb.to(dev),yb.to(dev);opt.zero_grad();loss=lossfn(m(xb),yb);loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1.0);opt.step();total+=loss.item()*len(xb)
  print(f'epoch={ep+1} loss={total/len(Xtr):.4f}')
 m.eval()
 with torch.no_grad(): p=torch.sigmoid(m(torch.tensor(Xte,device=dev))).cpu().numpy()
 print(f'ROC-AUC: {roc_auc_score(yte,p):.4f}'); print(f'F1: {f1_score(yte,p>=.5):.4f}')
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);torch.save({'state_dict':m.state_dict(),'means':MEANS,'stds':STDS},out);print('saved',out)
if __name__=='__main__': main()
