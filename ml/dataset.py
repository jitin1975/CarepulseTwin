import numpy as np
FEATURES=['heart_rate','spo2','systolic_bp','diastolic_bp','temperature','respiratory_rate']
MEANS=np.array([75,97,120,78,36.8,16],dtype=np.float32)
STDS=np.array([12,1.5,12,9,.35,3.5],dtype=np.float32)
def make_dataset(n=5000,seq_len=30,seed=42):
    rng=np.random.default_rng(seed); X=rng.normal(size=(n,seq_len,6)).astype(np.float32)*STDS+MEANS; y=np.zeros(n,dtype=np.int64)
    for i in range(n):
        if rng.random()<.45:
            y[i]=1; t=np.linspace(0,1,seq_len)
            X[i,:,1]-=rng.uniform(4,10)*t; X[i,:,5]+=rng.uniform(5,12)*t
            X[i,:,0]+=rng.uniform(15,35)*t; X[i,:,4]+=rng.uniform(.2,.7)*t
    return X,y
