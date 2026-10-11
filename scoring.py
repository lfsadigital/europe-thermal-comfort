"""Luiz's daily maximum temperature preference rule."""
import numpy as np

def daily_score(temperature):
    t=np.asarray(temperature,dtype=np.float64)
    return 100-np.maximum(20-t,0)-np.maximum(t-25,0)
