import argparse, json
from pathlib import Path
import numpy as np, torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_score, recall_score, precision_recall_curve, confusion_matrix
from ml.model import CarePulseLSTM

def probs(model,X):
    model.eval(); out=[]
    with torch.no_grad():
        for i in range(0,len(X),2048): out.append(torch.sigmoid(model(torch.tensor(X[i:i+2048],dtype=torch.float32))).numpy())
    return np.concatenate(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data',required=True); ap.add_argument('--out',required=True); ap.add_argument('--epochs',type=int,default=6); ap.add_argument('--batch-size',type=int,default=256); a=ap.parse_args()
    d=np.load(a.data,allow_pickle=True); X,y=d['X_train'],d['y_train']; Xv,yv=d['X_val'],d['y_val']; Xt,yt=d['X_test'],d['y_test']
    # Balanced training subset for the highly imbalanced deterioration target.
    rng=np.random.default_rng(11); pos=np.where(y==1)[0]; neg=np.where(y==0)[0]; neg=rng.choice(neg,size=min(len(neg),len(pos)*2),replace=False); idx=np.concatenate([pos,neg]); rng.shuffle(idx)
    model=CarePulseLSTM(n=X.shape[-1]); loader=DataLoader(TensorDataset(torch.tensor(X[idx]),torch.tensor(y[idx],dtype=torch.float32)),batch_size=a.batch_size,shuffle=True); opt=torch.optim.Adam(model.parameters(),lr=1e-3); crit=nn.BCEWithLogitsLoss()
    best_auc=-1; best_state=None; best_threshold=.5
    for ep in range(1,a.epochs+1):
        model.train()
        for xb,yb in loader:
            opt.zero_grad(); loss=crit(model(xb),yb); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
        pv=probs(model,Xv); auc=roc_auc_score(yv,pv); apv=average_precision_score(yv,pv); pr,re,th=precision_recall_curve(yv,pv); f=2*pr*re/(pr+re+1e-9); i=int(np.nanargmax(f)); threshold=float(th[i]) if i<len(th) else .5
        print(f'epoch={ep} val_auc={auc:.4f} val_pr_auc={apv:.4f} val_f1={f[i]:.4f} threshold={threshold:.4f}')
        if auc>best_auc: best_auc=auc; best_state={k:v.detach().clone() for k,v in model.state_dict().items()}; best_threshold=threshold
    model.load_state_dict(best_state); pt=probs(model,Xt); pred=(pt>=best_threshold).astype(int)
    metrics={'roc_auc':float(roc_auc_score(yt,pt)),'pr_auc':float(average_precision_score(yt,pt)),'threshold':float(best_threshold),'f1':float(f1_score(yt,pred)),'precision':float(precision_score(yt,pred)),'recall':float(recall_score(yt,pred)),'confusion_matrix':confusion_matrix(yt,pred).tolist(),'n_test':int(len(yt)),'positive_test':int(yt.sum()),'target':'Any qualifying vital abnormality in the following 6 hours'}
    print('TEST',json.dumps(metrics,indent=2)); Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    torch.save({'state_dict':model.state_dict(),'mean':d['mean'],'std':d['std'],'seq_len':int(X.shape[1]),'feature_names':d['features'].tolist(),'threshold':best_threshold,'target':metrics['target']},a.out)
    Path(a.out).with_suffix('.metrics.json').write_text(json.dumps(metrics,indent=2))
if __name__=='__main__': main()
