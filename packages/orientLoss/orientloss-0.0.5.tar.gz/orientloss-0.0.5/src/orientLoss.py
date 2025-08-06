import torch
import math


def orientLoss(input,target,dim=1,meanOut=True,angleSmooth=1,normSmooth=1,dimScalingOrd=1,eps=1e-8):
    m=angleSmooth/2
    n=normSmooth-m
    diff=input-target #注意这里顺序不要写反
    numel=diff.numel()
    diffNorm=torch.linalg.norm(diff,ord=2,dim=dim,keepdim=False)
    numel/=diffNorm.numel()
    t=target.broadcast_to(diff.size())
    targetNorm=torch.linalg.norm(t,ord=2,dim=dim,keepdim=False)
    k=diffNorm*targetNorm
    dot=(diff*t).sum(dim=dim,keepdim=False)
    loss1=(k+eps)**n
    loss2=(k-dot+eps)**m
    loss=loss1*loss2-(eps**(m+n))
    #loss[~torch.isfinite(loss)]=0
    
    if meanOut:
        return loss.mean()
    else:
        return loss
       




