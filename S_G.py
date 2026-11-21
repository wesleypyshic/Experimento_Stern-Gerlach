import numpy as np
import streamlit as st


def auto_spin(theta_g):
    theta = np.radians(theta_g)
    mais = np.array([np.cos(theta/2) , np.sin(theta/2)])
    menos = np.array([ -np.sin(theta/2),np.cos(theta/2)])
    return mais, menos

def P(estado, theta_g):
    if estado is None:
        return 1/2, 1/2
    mais, menos = auto_spin(theta_g)
    amp_mais = np.vdot(mais, estado)
    p_mais = np.abs(amp_mais)**2
    amp_menos = np.vdot(menos, estado)
    p_menos =np.abs(amp_menos)**2
    return p_mais, p_menos

z_mais, z_menos = auto_spin(0)
print(P(z_mais,60))

def simular_filtro(n_atomos, p_mais):
    p_mais = np.clip(p_mais, 0.0, 1.0)
    n_mais = np.random.binomial(n_atomos, p_mais)
    n_menos = n_atomos - n_mais
    return n_mais, n_menos

z_mais, z_menos = auto_spin(0)
p_mais, p_menos = P(z_mais, 60)
print(simular_filtro(1000, p_mais))
