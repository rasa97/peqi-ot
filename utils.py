from random import random
import numpy as np
from functools import partial
from cqc.pythonLib import CQCConnection

def call(func, name, cqc=None):
    if cqc is None:
        with CQCConnection(name, appID=0) as cqc:
            return func(cqc=cqc)
    else:
        return func(cqc=cqc)

    
def prepare_func(func, *args, **kwargs):
    f = partial(func, *args, **kwargs)
    return f

def generate_full_rank_matrix(k,n):
    m = np.eye(k,n,dtype=np.uint8)
    for j in range(0, k):
        for i in range(n-k, n):
            if random() < 0.5:
                m[j][i] = 1

    return m
