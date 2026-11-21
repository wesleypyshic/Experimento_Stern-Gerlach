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

#...animacao...#

with aba_exp:
    desenhar_bancada()

    if modo == "1. Quantização (1 Filtro)":
        with st.expander("🎬 Como funciona o aparelho físico de Stern-Gerlach", expanded=True):
            col_gif, col_txt = st.columns([1.1, 1.4])
            with col_gif:
                st.image(
                    "sg_animacao.gif",
                    caption="Montagem física: fonte, ímã não uniforme e tela.",
                    use_container_width=True,
                )
            with col_txt:
                st.markdown("""
                **Entendendo a bancada real:**

                1. **Fonte de átomos:** aquece átomos de prata, emitindo um feixe com spins em direções completamente aleatórias.
                2. **Campo magnético não uniforme (N–S):** o gradiente de campo entre os polos aplica uma força vertical proporcional à componente do spin no eixo **z**.
                3. **Tela de detecção:** em vez de formar uma faixa contínua (previsão clássica), o feixe se divide em apenas **dois pontos discretos** ($+\\hbar/2$ e $-\\hbar/2$).

                *Depois de observar a animação, você pode recolher esta caixa clicando no título acima para focar nos gráficos.*
                """)