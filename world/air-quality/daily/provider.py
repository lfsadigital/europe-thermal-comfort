"""CAMS concentrations to provider-compatible hourly US AQI.
Threshold facts and conversion factors verified against Open-Meteo commit
03d62919c419f1eccad8dcbbcf7f92a2dd7069b4. No daily AQI health claim.
"""
import numpy as np
VARIABLES=['pm2_5','pm10','nitrogen_dioxide','ozone','sulphur_dioxide','carbon_monoxide']
def position(x,thresholds):
 x=np.asarray(x,dtype=np.float32);out=np.full(x.shape,np.nan,dtype=np.float32)
 for i in range(1,len(thresholds)):
  a,b=thresholds[i-1:i+1]
  if not np.isfinite(a) or not np.isfinite(b):continue
  mask=(x>=a)&((x<b) if i<len(thresholds)-1 else True)
  out[mask]=(i-1)+(x[mask]-a)/(b-a)
 return out

def scale(x):return np.where(x<=4,x*50,np.where(x<=5,x*100-200,x*200-700)).astype('f4')
def trailing(values,hours):
 # The provider uses the preceding hours, excluding the current timestamp.
 w=np.lib.stride_tricks.sliding_window_view(values,hours,axis=1)
 return w[:,:-1,:].sum(axis=2,dtype=np.float32)/hours

def hourly(data):
 length=data['pm2_5'].shape[1]-24;parts=[]
 for name in VARIABLES:
  a=np.asarray(data[name],dtype='f4');a=np.where(a>=0,a,np.nan);v=a[:,24:];r24=trailing(a,24) if name in ['pm2_5','pm10','sulphur_dioxide'] else None
  if name=='pm2_5':p=position(r24,[0,9,35.5,55.5,125.5,225.5,325.5])
  elif name=='pm10':p=position(r24,[0,55,155,255,355,425,605])
  elif name=='nitrogen_dioxide':p=position(v/1.88,[0,54,100,360,650,1250,2050])
  elif name=='ozone':
   a1=position(v/1.96,[np.nan,np.nan,125,165,205,405,605]);m=trailing(a,8)[:,-length:]/1.96;a2=np.where(m>=200,5,position(m,[0,55,70,85,105,200,np.nan]));p=np.fmax(a1,a2)
  elif name=='sulphur_dioxide':
   x=v/2.62;p1=np.where(x>=305,4,position(x,[0,35,75,185,305,np.nan,np.nan]));p2=position(r24/2.62,[np.nan,np.nan,np.nan,np.nan,305,605,1005]);p=np.where(np.isnan(p1),p2,p1)
  else:p=position(trailing(a,8)[:,-length:]/1.15/1000,[0,4.5,9.5,12.5,15.5,30.5,50.5])
  parts.append(scale(p))
 # Missing pollutant inputs stay unknown rather than imply cleaner air.
 return np.maximum.reduce(parts)

def daily(values):
 a=np.asarray(values,dtype='f8');assert a.shape[-1]==24
 valid=np.isfinite(a)&(a>=0);w=np.lib.stride_tricks.sliding_window_view(a,3,axis=-1)
 good=np.isfinite(w).all(axis=-1)&(w>=0).all(axis=-1)
 means=np.where(good,w.mean(axis=-1),-np.inf)
 top=means.max(axis=-1);return np.where((valid.sum(axis=-1)>=22)&np.isfinite(top),top,np.nan)
