# SPDX-License-Identifier: AGPL-3.0-only
# Solar method adapted from Open-Meteo; see AGPL-3.0.txt.
"""ERA5 radiation-derived sunshine, matching Open-Meteo's published method.
NREL SPA lookup values (delta_t=60); Float32 solar geometry; hourly preceding sums.
See sources.json for pinned provenance. Duration is not astronomical daylight.
"""
import json
from pathlib import Path
import numpy as np
LOOKUP=json.loads(Path(__file__).with_name('solar-lookup.json').read_text())
TABLE=np.asarray(LOOKUP['values'],dtype='f4');F=np.float32;PI=F(np.pi)
def positions(seconds):
 x=np.asarray(seconds,dtype='i8')-LOOKUP['start'];i=x//LOOKUP['step'];f=((x%LOOKUP['step'])/LOOKUP['step']).astype('f4')[:,None]
 a,b,c,d=[TABLE[(i+offset)%len(TABLE)] for offset in [-1,0,1,2]]
 p=-a/F(2)+F(3)*b/F(2)-F(3)*c/F(2)+d/F(2)
 q=a-F(5)*b/F(2)+F(2)*c-d/F(2);r=-a/F(2)+c/F(2)
 out=p*f*f*f+q*f*f+r*f+b
 return out[:,0],out[:,1]/F(60)
def sunshine(radiation,latitude,longitudes,seconds):
 radiation=np.asarray(radiation,dtype='f4');seconds=np.asarray(seconds,dtype='i8');dec,eq=positions(seconds)
 radians=lambda x:np.asarray(x,dtype='f4')*PI/F(180)
 hour=(seconds%86400).astype('f4')/F(3600);polar=radians(F(90)-F(latitude));colat=radians(F(90)-dec)
 angle=radians(F(-15)*(hour-F(12)+eq));previous=radians(F(-15)*(hour-F(1)-F(12)+eq))
 longitude=radians(longitudes)[:,None];longitude=np.where(longitude<angle-PI,longitude+F(2)*PI,longitude);longitude=np.where(longitude>angle+PI,longitude-F(2)*PI,longitude)
 constant=np.cos(polar)*np.cos(colat);amplitude=np.sin(polar)*np.sin(colat)
 with np.errstate(divide='ignore',invalid='ignore'):
  ratio=-constant/amplitude;limit=np.where((ratio>1)|(ratio<-1),PI,np.arccos(np.clip(ratio,-1,1)))
  sunrise=longitude+limit;sunset=longitude-limit;left=np.minimum(sunrise,previous);right=np.maximum(sunset,angle)
  duration=F(3600)*np.abs((left-right)/(previous-angle))
  integral_left=amplitude*np.sin(left-longitude)+left*constant;integral_right=amplitude*np.sin(right-longitude)+right*constant;delta=left-right
  elevation=(integral_left-integral_right)/np.where(delta<0,np.minimum(F(-.001),delta),np.maximum(F(.001),delta))
  normal=np.where(elevation<=F(.0001),radiation,radiation/elevation)
  result=np.minimum(np.maximum(normal-F(60),0)/F(120)*duration,duration)
 result=np.where((radiation<=0)|(previous<sunset)|(angle>sunrise),F(0),result)
 return np.where(np.isnan(radiation),np.nan,result).astype('f4')
