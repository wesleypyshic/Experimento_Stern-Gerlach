from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import plotly.graph_objects as go
from S_G import auto_spin, P, simular_filtro, simular_experimento

st.set_page_config(page_title="Laboratório Stern-Gerlach", page_icon="🧲", layout="wide")

st.markdown(
    """
    <style>
    @media (max-width: 768px) { 
        /* Esconde a barra de ferramentas dos gráficos Plotly no celular */
        .modebar-container, .modebar {
            display: none !important;
        }
        /* Reduz margens laterais para ganhar espaço útil */
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 1.5rem !important;
        }
        /* Diminui o título principal e subtítulos */
        h1 { font-size: 1.5rem !important; }
        h2, h3 { font-size: 1.15rem !important; }

        /* Evita que as abas se sobreponham */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem !important;
            flex-wrap: wrap !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem !important;
            padding: 0.35rem 0.5rem !important;
        }

        /* Ajusta o tamanho das métricas (Saída + / Saída -) */
        [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }

        /* Permite rolar equações LaTeX largas para o lado em vez de encavalar */
        .katex-display {
            overflow-x: auto !important;
            overflow-y: hidden !important;
            padding-bottom: 4px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Estado inicial ---
defaults = {
    "modo": "1. Quantização (1 Filtro)",
    "n_atomos": 1000,
    "theta1": 0,
    "feixe1": "+",
    "theta2": 90,
    "feixe2": "+",
    "theta3": 0,
    "comparar_classico": True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def carregar_cenario(modo, t1=0, f1="+", t2=90, f2="+", t3=0, n=1000):
    st.session_state.modo = modo
    st.session_state.theta1 = t1
    st.session_state.feixe1 = f1
    st.session_state.theta2 = t2
    st.session_state.feixe2 = f2
    st.session_state.theta3 = t3
    st.session_state.n_atomos = n


# --- Cabeçalho ---
col_tit, col_btn = st.columns([4, 1])
with col_tit:
    st.title("🧲 Laboratório Virtual de Stern-Gerlach")
    st.caption("Simulador interativo de quantização do spin, superposição e colapso de estado.")
with col_btn:
    st.write("")
    st.button("🔄 Novo disparo", use_container_width=True, help="Repete o sorteio quântico com os mesmos ângulos")

# --- Barra lateral limpa e progressiva ---
st.sidebar.header("1. Escolha o Experimento")
modo = st.sidebar.radio(
    "Nível de estudo:",
    [
        "1. Quantização (1 Filtro)",
        "2. Projeção (2 Filtros)",
        "3. Colapso de Estado (3 Filtros)",
    ],
    key="modo",
)

st.sidebar.divider()
st.sidebar.header("2. Ajustes da Bancada")
n_atomos = st.sidebar.slider("Átomos emitidos pela fonte (N₀)", 20, 5000, step=20, key="n_atomos")

if modo == "1. Quantização (1 Filtro)":
    theta1 = st.sidebar.slider("Ângulo do Ímã 1 (°)", 0, 180, key="theta1")

elif modo == "2. Projeção (2 Filtros)":
    st.sidebar.markdown("**Filtro 1 (Preparador)**")
    theta1 = st.sidebar.slider("Ângulo do Filtro 1 (°)", 0, 180, key="theta1")
    feixe1 = st.sidebar.radio("Feixe que passa no Filtro 1", ["+", "-"], horizontal=True, key="feixe1")
    st.sidebar.markdown("**Filtro 2 (Medidor)**")
    theta2 = st.sidebar.slider("Ângulo do Filtro 2 (°)", 0, 180, key="theta2")

else:
    st.sidebar.markdown("**Filtro 1 (Preparador)**")
    theta1 = st.sidebar.slider("Ângulo do Filtro 1 (°)", 0, 180, key="theta1")
    feixe1 = st.sidebar.radio("Feixe que passa no Filtro 1", ["+", "-"], horizontal=True, key="feixe1")
    st.sidebar.markdown("**Filtro 2 (Intermediário)**")
    theta2 = st.sidebar.slider("Ângulo do Filtro 2 (°)", 0, 180, key="theta2")
    feixe2 = st.sidebar.radio("Feixe que passa no Filtro 2", ["+", "-"], horizontal=True, key="feixe2")
    st.sidebar.markdown("**Filtro 3 (Analisador Final)**")
    theta3 = st.sidebar.slider("Ângulo do Filtro 3 (°)", 0, 180, key="theta3")

st.sidebar.divider()
st.sidebar.caption("💡 Dica: reduza N₀ para 40 átomos e clique em 'Novo disparo' para observar o ruído estatístico quântico.")

st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.45;">
        <strong style="color: #e2e8f0;">Prof. Wesley Sales de Souza</strong><br>
        Licenciatura em Física<br>
        DEFIS – IFMA<br>
        <em>Grupo de Magnetismo e Física Computacional (GMFC)</em>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Motor Físico (usando o núcleo validado em S_G.py) ---
modo_id = 1 if modo.startswith("1.") else (2 if modo.startswith("2.") else 3)

sim = simular_experimento(
    n0=n_atomos,
    modo_id=modo_id,
    theta1=st.session_state.theta1,
    feixe1=st.session_state.feixe1,
    theta2=st.session_state.theta2,
    feixe2=st.session_state.feixe2,
    theta3=st.session_state.theta3,
)

p_final_mais = sim["p_final_mais"]
p_final_menos = sim["p_final_menos"]
p_total_mais = sim["p_total_mais"]
p_total_menos = sim["p_total_menos"]
n_entrada_final = sim["n_entrada_final"]
n_final_mais = sim["n_final_mais"]
n_final_menos = sim["n_final_menos"]
theta_anteparo = sim["theta_anteparo"]
nome_final = sim["nome_final"]
estado1 = sim["estado1"]
estado_entrada = sim["estado_entrada"]
delta_theta = sim["delta_theta"]
sigma_f = sim["sigma_f"]

if modo_id >= 2:
    n_ent_2 = sim["n_ent_2"]
    n_bloq_f1 = sim["n_bloq_1"]
    p_passou_f1 = sim["p1_sel"]
if modo_id == 3:
    estado2 = sim["estado2"]
    n_bloq_f2 = sim["n_bloq_2"]
    p_passou_f2 = sim["p2_sel"]

pct_mais = sim["f_mais"] * 100
pct_menos = sim["f_menos"] * 100


# --- Função para desenhar a bancada (SVG compacto via components.html) ---
def desenhar_bancada():
    w_mais = max(1.5, (n_final_mais / max(1, n_atomos)) * 7)
    w_menos = max(1.5, (n_final_menos / max(1, n_atomos)) * 7)

    if modo == "1. Quantização (1 Filtro)":
        corpo = f"""
        <rect x="90" y="55" width="90" height="50" rx="8" fill="#3a2323" stroke="#EF553B" stroke-width="2"/>
        <text x="135" y="78" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Forno Ag</text>
        <text x="135" y="95" fill="#fca5a5" font-size="11" text-anchor="middle">Não polarizado</text>

        <line x1="180" y1="80" x2="320" y2="80" stroke="#94a3b8" stroke-width="4" stroke-dasharray="6,4"/>
        <text x="250" y="68" fill="#cbd5e1" font-size="12" text-anchor="middle">N₀ = {n_atomos}</text>

        <rect x="320" y="40" width="140" height="80" rx="10" fill="#1e293b" stroke="#f59e0b" stroke-width="2.5"/>
        <text x="390" y="72" fill="#fff" font-size="14" text-anchor="middle" font-weight="bold">Ímã SG (Filtro 1)</text>
        <text x="390" y="96" fill="#fcd34d" font-size="13" text-anchor="middle">θ₁ = {theta1}°</text>

        <line x1="460" y1="68" x2="660" y2="38" stroke="#00CC96" stroke-width="{w_mais:.1f}"/>
        <text x="560" y="38" fill="#00CC96" font-size="13" text-anchor="middle" font-weight="bold">Saída (+) : {n_final_mais}</text>

        <line x1="460" y1="92" x2="660" y2="122" stroke="#EF553B" stroke-width="{w_menos:.1f}"/>
        <text x="560" y="135" fill="#EF553B" font-size="13" text-anchor="middle" font-weight="bold">Saída (-) : {n_final_menos}</text>

        <rect x="665" y="20" width="16" height="120" rx="4" fill="#e2e8f0"/>
        <text x="725" y="84" fill="#e2e8f0" font-size="13" text-anchor="middle" font-weight="bold">Anteparo</text>
        """
    elif modo == "2. Projeção (2 Filtros)":
        w_f1 = max(1.5, (n_ent_2 / max(1, n_atomos)) * 6.5)
        corpo = f"""
        <rect x="35" y="55" width="82" height="50" rx="8" fill="#3a2323" stroke="#EF553B" stroke-width="2"/>
        <text x="76" y="84" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Forno</text>

        <line x1="117" y1="80" x2="195" y2="80" stroke="#94a3b8" stroke-width="3.5" stroke-dasharray="5,4"/>
        <text x="156" y="68" fill="#cbd5e1" font-size="11" text-anchor="middle">N₀={n_atomos}</text>

        <rect x="195" y="40" width="125" height="80" rx="10" fill="#1e293b" stroke="#60a5fa" stroke-width="2"/>
        <text x="257" y="72" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Filtro 1 (Prep.)</text>
        <text x="257" y="95" fill="#93c5fd" font-size="12" text-anchor="middle">θ₁ = {theta1}° | só ({feixe1})</text>

        <line x1="320" y1="68" x2="455" y2="68" stroke="#38bdf8" stroke-width="{w_f1:.1f}"/>
        <text x="387" y="56" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="bold">{n_ent_2} em |χ₁⟩</text>

        <line x1="320" y1="95" x2="370" y2="128" stroke="#EF553B" stroke-width="2" stroke-dasharray="4,3"/>
        <rect x="370" y="118" width="8" height="22" rx="2" fill="#EF553B"/>
        <text x="385" y="134" fill="#fca5a5" font-size="11">{n_bloq_f1} bloq.</text>

        <rect x="455" y="40" width="125" height="80" rx="10" fill="#1e293b" stroke="#f59e0b" stroke-width="2.5"/>
        <text x="517" y="72" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Filtro 2 (Med.)</text>
        <text x="517" y="95" fill="#fcd34d" font-size="12" text-anchor="middle">θ₂ = {theta2}°</text>

        <line x1="580" y1="68" x2="725" y2="38" stroke="#00CC96" stroke-width="{w_mais:.1f}"/>
        <text x="652" y="38" fill="#00CC96" font-size="12" text-anchor="middle" font-weight="bold">+ ({n_final_mais})</text>

        <line x1="580" y1="92" x2="725" y2="122" stroke="#EF553B" stroke-width="{w_menos:.1f}"/>
        <text x="652" y="136" fill="#EF553B" font-size="12" text-anchor="middle" font-weight="bold">- ({n_final_menos})</text>

        <rect x="730" y="20" width="15" height="120" rx="4" fill="#e2e8f0"/>
        <text x="790" y="84" fill="#e2e8f0" font-size="13" text-anchor="middle" font-weight="bold">Anteparo</text>
        """
    else:
        w_f1 = max(1.5, (n_ent_2 / max(1, n_atomos)) * 6)
        w_mid = max(1.5, (n_entrada_final / max(1, n_atomos)) * 6)
        corpo = f"""
        <rect x="10" y="55" width="60" height="50" rx="8" fill="#3a2323" stroke="#EF553B" stroke-width="2"/>
        <text x="40" y="84" fill="#fff" font-size="12" text-anchor="middle" font-weight="bold">Forno</text>

        <line x1="70" y1="80" x2="125" y2="80" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4,3"/>
        <text x="97" y="68" fill="#cbd5e1" font-size="10" text-anchor="middle">N₀={n_atomos}</text>

        <rect x="125" y="42" width="108" height="76" rx="8" fill="#1e293b" stroke="#60a5fa" stroke-width="2"/>
        <text x="179" y="72" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Filtro 1</text>
        <text x="179" y="94" fill="#93c5fd" font-size="12" text-anchor="middle">θ₁={theta1}° ({feixe1})</text>

        <line x1="233" y1="68" x2="328" y2="68" stroke="#38bdf8" stroke-width="{w_f1:.1f}"/>
        <text x="280" y="56" fill="#38bdf8" font-size="11" text-anchor="middle" font-weight="bold">{n_ent_2} passam</text>

        <line x1="233" y1="95" x2="268" y2="128" stroke="#EF553B" stroke-width="2" stroke-dasharray="4,3"/>
        <rect x="268" y="118" width="7" height="20" rx="2" fill="#EF553B"/>
        <text x="280" y="133" fill="#fca5a5" font-size="10">{n_bloq_f1} bloq.</text>

        <rect x="328" y="42" width="108" height="76" rx="8" fill="#1e293b" stroke="#a78bfa" stroke-width="2"/>
        <text x="382" y="72" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Filtro 2</text>
        <text x="382" y="94" fill="#c4b5fd" font-size="12" text-anchor="middle">θ₂={theta2}° ({feixe2})</text>

        <line x1="436" y1="68" x2="545" y2="68" stroke="#a78bfa" stroke-width="{w_mid:.1f}"/>
        <text x="490" y="56" fill="#c4b5fd" font-size="11" text-anchor="middle" font-weight="bold">{n_entrada_final} passam</text>

        <line x1="436" y1="95" x2="482" y2="128" stroke="#EF553B" stroke-width="2" stroke-dasharray="4,3"/>
        <rect x="482" y="118" width="7" height="20" rx="2" fill="#EF553B"/>
        <text x="495" y="133" fill="#fca5a5" font-size="10">{n_bloq_f2} bloq.</text>

        <rect x="545" y="42" width="108" height="76" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="2.5"/>
        <text x="599" y="72" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Filtro 3</text>
        <text x="599" y="94" fill="#fcd34d" font-size="12" text-anchor="middle">θ₃={theta3}°</text>

        <line x1="653" y1="68" x2="765" y2="38" stroke="#00CC96" stroke-width="{w_mais:.1f}"/>
        <text x="710" y="38" fill="#00CC96" font-size="12" text-anchor="middle" font-weight="bold">+ ({n_final_mais})</text>

        <line x1="653" y1="92" x2="765" y2="122" stroke="#EF553B" stroke-width="{w_menos:.1f}"/>
        <text x="710" y="136" fill="#EF553B" font-size="12" text-anchor="middle" font-weight="bold">- ({n_final_menos})</text>

        <rect x="768" y="20" width="14" height="120" rx="4" fill="#e2e8f0"/>
        <text x="818" y="84" fill="#e2e8f0" font-size="12" text-anchor="middle" font-weight="bold">Tela</text>
        """

    html = f"""
    <div style="font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0;">
      <svg viewBox="0 0 860 160" width="100%" height="160" style="background:#161922; border-radius:12px; border:1px solid #2d3240;">
        {corpo}
      </svg>
    </div>
    """
    components.html(html, height=164)


# --- Funções para os Gráficos ---
def grafico_quantico(altura=380):
    rad = np.radians(theta_anteparo)
    cx, cz = np.sin(rad), np.cos(rad)

    x_mais = np.random.normal(cx, 0.14, n_final_mais)
    z_mais = np.random.normal(cz, 0.14, n_final_mais)
    x_menos = np.random.normal(-cx, 0.14, n_final_menos)
    z_menos = np.random.normal(-cz, 0.14, n_final_menos)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[-1.7 * cx, 1.7 * cx], y=[-1.7 * cz, 1.7 * cz],
        mode="lines", name="Eixo do Ímã (B)",
        line=dict(color="rgba(255, 255, 255, 0.3)", width=2, dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=x_mais, y=z_mais, mode="markers", name="Spin (+ℏ/2)",
        marker=dict(color="#00CC96", size=5, opacity=0.7)
    ))
    fig.add_trace(go.Scatter(
        x=x_menos, y=z_menos, mode="markers", name="Spin (-ℏ/2)",
        marker=dict(color="#EF553B", size=5, opacity=0.7)
    ))
    fig.update_layout(
        title=f"⚛️ Anteparo Quântico — {nome_final} (θ = {theta_anteparo}°)",
        xaxis=dict(title="Eixo x", range=[-2, 2], zeroline=True, gridcolor="#262a36"),
        yaxis=dict(title="Eixo z", range=[-2, 2], zeroline=True, gridcolor="#262a36", scaleanchor="x", scaleratio=1),
        height=altura,
        margin=dict(l=20, r=20, t=45, b=80),
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#12151e",
    )
    return fig


def grafico_classico(altura=350):
    rad = np.radians(theta_anteparo)
    cx, cz = np.sin(rad), np.cos(rad)
    px, pz = cz, -cx

    u = np.random.uniform(-1.0, 1.0, n_atomos)
    ruido_t = np.random.normal(0, 0.12, n_atomos)
    xc = u * cx + ruido_t * px
    zc = u * cz + ruido_t * pz

    texto_classico = (
        "**Física Clássica (1 Filtro):** Os átomos saem do forno com dipolos magnéticos apontando em todas as direções 3D. "
        "Como $\\mu_n = \\mu \\cos\\alpha$ varia continuamente entre $-\\mu$ e $+\\mu$, deveria surgir uma **faixa contínua** — sem separação em dois feixes."
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[-1.7 * cx, 1.7 * cx], y=[-1.7 * cz, 1.7 * cz],
        mode="lines", name="Eixo do Ímã (B)",
        line=dict(color="rgba(255, 255, 255, 0.3)", width=2, dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=xc, y=zc, mode="markers", name="Dipolo clássico (contínuo)",
        marker=dict(color="#F59E0B", size=5, opacity=0.65)
    ))
    fig.update_layout(
        title=f"🏛️ Previsão Clássica — {nome_final} (θ = {theta_anteparo}°)",
        xaxis=dict(title="Eixo x", range=[-2, 2], zeroline=True, gridcolor="#262a36"),
        yaxis=dict(title="Eixo z", range=[-2, 2], zeroline=True, gridcolor="#262a36", scaleanchor="x", scaleratio=1),
        height=altura,
        margin=dict(l=20, r=20, t=45, b=80),
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#12151e",
    )
    return fig, texto_classico


def grafico_barras():
    fig_bar = go.Figure(data=[
        go.Bar(
            name="Experimental",
            x=["Saída (+)", "Saída (-)"],
            y=[pct_mais, pct_menos],
            marker_color=["#00CC96", "#EF553B"],
        ),
        go.Bar(
            name="Teórico",
            x=["Saída (+)", "Saída (-)"],
            y=[p_final_mais * 100, p_final_menos * 100],
            marker_color=["rgba(0,204,150,0.3)", "rgba(239,85,59,0.3)"],
        ),
    ])
    fig_bar.update_layout(
        barmode="group",
        yaxis=dict(title="Fração (%)", range=[0, 105]),
        height=200,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig_bar


def exibir_explicacao_quantica():
    if modo == "1. Quantização (1 Filtro)":
        st.info(
            "**Realidade Quântica:** O momento angular intrínseco (spin) é **quantizado**. "
            "Independentemente do ângulo do ímã, o anteparo registra apenas **dois pontos discretos** ($+\\hbar/2$ e $-\\hbar/2$)."
        )
    elif modo == "3. Colapso de Estado (3 Filtros)" and n_entrada_final == 0:
        st.warning(
            "**Bloqueio total no Filtro 2:** 0 átomos chegaram ao Filtro 3 porque o estado selecionado no Filtro 2 "
            "é ortogonal ao estado preparado no Filtro 1."
        )
    elif modo == "3. Colapso de Estado (3 Filtros)" and theta1 == theta3 and abs(theta2 - theta1) == 90:
        st.success(
            "**Colapso de Estado ($z \\to x \\to z$):** Medir no eixo perpendicular ($90^\\circ$) no Filtro 2 destrói a informação "
            "anterior e faz a componente descartada **reaparecer** com 50% de chance no Filtro 3!"
        )
    elif abs(p_final_mais - 1.0) < 1e-6 or abs(p_final_menos - 1.0) < 1e-6:
        st.info(
            "**Autoestado puro:** Os átomos entram alinhados (ou antialinhados) com o eixo do ímã final. "
            "100% saem em apenas um canal."
        )
    elif abs(p_final_mais - 0.5) < 1e-3:
        st.info(
            "**Superposição máxima (50% / 50%):** O eixo de medição está perpendicular ($90^\\circ$) ao estado de entrada. "
            "Cada átomo escolhe aleatoriamente entre $+\\hbar/2$ e $-\\hbar/2$."
        )
    else:
        st.info(
            f"**Projeção oblíqua ($\\Delta\\theta = {delta_theta:.0f}^\\circ$):** A probabilidade segue "
            f"$P_+ = \\cos^2({delta_theta:.0f}^\\circ / 2) = {p_final_mais:.3f}$."
        )


# ==========================================================
# ABAS PRINCIPAIS
# ==========================================================
aba_exp, aba_aparato, aba_alg, aba_guia = st.tabs([
    "🧪 Bancada do Experimento",
    "🎬 Aparato Físico (3D)",
    "📐 Formalismo & Curva Teórica",
    "🎯 Roteiro de Desafios"
])

# --- ABA 1: BANCADA VISUAL ---
with aba_exp:
    desenhar_bancada()

    mostrar_comparacao = False
    if modo == "1. Quantização (1 Filtro)":
        mostrar_comparacao = st.toggle(
            "⚖️ Comparar lado a lado com a Previsão Clássica",
            key="comparar_classico"
        )

    if mostrar_comparacao:
        col_cl, col_qt = st.columns(2)

        with col_cl:
            fig_cl, txt_cl = grafico_classico(altura=350)
            st.plotly_chart(fig_cl, use_container_width=True)
            st.warning(txt_cl)

        with col_qt:
            st.plotly_chart(grafico_quantico(altura=350), use_container_width=True)
            exibir_explicacao_quantica()

        st.divider()
        col_m, col_b = st.columns([1, 2])
        with col_m:
            st.metric("Saída (+) [+ℏ/2]", f"{n_final_mais} átomos", f"{pct_mais:.1f}%", delta_color="off")
            st.metric("Saída (-) [-ℏ/2]", f"{n_final_menos} átomos", f"{pct_menos:.1f}%", delta_color="off")
        with col_b:
            st.plotly_chart(grafico_barras(), use_container_width=True)

    else:
        col_tela, col_info = st.columns([1.15, 1])

        with col_tela:
            st.plotly_chart(grafico_quantico(altura=380), use_container_width=True)

        with col_info:
            st.caption(f"Fluxo no {nome_final}: **N_entrada = {n_entrada_final}** de **N₀ = {n_atomos}** emitidos pela fonte (σ_f = {sigma_f*100:.2f}%).")
            c1, c2 = st.columns(2)
            c1.metric("Saída (+) [+ℏ/2]", f"{n_final_mais} átomos", f"{pct_mais:.1f}% (teor. {p_final_mais*100:.1f}%)", delta_color="off")
            c2.metric("Saída (-) [-ℏ/2]", f"{n_final_menos} átomos", f"{pct_menos:.1f}% (teor. {p_final_menos*100:.1f}%)", delta_color="off")
            st.plotly_chart(grafico_barras(), use_container_width=True)
            exibir_explicacao_quantica()

# --- ABA 2: APARATO FÍSICO (GIF + DIAGRAMAS 3D) ---
with aba_aparato:
    pasta_app = Path(__file__).parent

    if modo == "1. Quantização (1 Filtro)":
        col_gif, col_txt = st.columns([1, 1.2])
        with col_gif:
            gifs = list(pasta_app.glob("*.gif"))
            if gifs:
                st.image(str(gifs[0]), caption="Montagem física: fonte, ímã não uniforme e tela.", use_container_width=True)
            else:
                st.error(f"Nenhum arquivo .gif encontrado em: {pasta_app}")
        with col_txt:
            st.subheader("Como funciona o aparelho real")
            st.markdown("""
1. **Fonte de átomos:** aquece átomos de prata, emitindo um feixe com spins em direções aleatórias.
2. **Campo magnético não uniforme (N–S):** o gradiente de campo entre os polos aplica uma força proporcional à componente do spin ao longo do eixo do ímã.
3. **Tela de detecção:** em vez de formar uma faixa contínua (previsão clássica), o feixe se divide em apenas **dois pontos discretos** ($+\\hbar/2$ e $-\\hbar/2$).
            """)

    elif modo == "2. Projeção (2 Filtros)":
        if theta1 == theta2:
            nome_img = "f2_alinhado.png"
            legenda = "Aparatos alinhados (B₁ ∥ B₂): o feixe selecionado em F₂ não volta a se dividir em P₂."
        elif abs(theta2 - 90) <= 15:
            nome_img = "f2_horizontal_x.png"
            legenda = "Segundo aparato girado para o eixo x̂ (plano amarelo): separação horizontal em N₁ e N₂."
        else:
            nome_img = "f2_inclinado_z.png"
            legenda = "Filtros com orientação relativa oblíqua (plano verde → plano azul): o feixe volta a se dividir em P₂."

        caminho_img = pasta_app / nome_img
        _, col_centro, _ = st.columns([0.5, 3, 0.5])
        with col_centro:
            if caminho_img.exists():
                st.image(str(caminho_img), caption=legenda, use_container_width=True)
            else:
                st.warning(f"Salve a imagem '{nome_img}' na pasta: {pasta_app}")

    else:
        candidatos_f3 = list(pasta_app.glob("f3_colapso.*"))
        _, col_centro, _ = st.columns([0.3, 3.4, 0.3])
        with col_centro:
            if candidatos_f3:
                st.image(
                    str(candidatos_f3[0]),
                    caption="Cascata z → x → z: após filtrar apenas N₁ em P₁ e medir no plano horizontal (x̂) em P₂, o componente N₂ reaparece em P₃.",
                    use_container_width=True,
                )
            else:
                st.warning(f"Salve a imagem 'f3_colapso.png' (ou .jpg) na pasta: {pasta_app}")

# --- ABA 3: FORMALISMO & CURVA TEÓRICA ---
with aba_alg:
    if modo == "1. Quantização (1 Filtro)":
        st.subheader("Por que 50% / 50% em qualquer ângulo?")
        st.write(
            "Os átomos saem do forno térmico com orientações de spin completamente aleatórias (uma **mistura estatística** "
            "descrita por $\\hat{\\rho} = \\hat{I}/2$, não um estado puro). Ao atravessar o campo magnético não uniforme "
            "orientado em $\\hat{n}_1$, cada átomo colapsa para um dos dois autoestados do operador $\\hat{S}_{n_1} = \\vec{S} \\cdot \\hat{n}_1$:"
        )
        m1_v, m2_v = auto_spin(theta1)
        st.latex(
            rf"|+\hat{{n}}_1\rangle = \begin{{pmatrix}} {m1_v[0].real+0.0:.3f} \\ {m1_v[1].real+0.0:.3f} \end{{pmatrix}}, \qquad "
            rf"|-\hat{{n}}_1\rangle = \begin{{pmatrix}} {m2_v[0].real+0.0:.3f} \\ {m2_v[1].real+0.0:.3f} \end{{pmatrix}}"
        )
        st.write("Passe para o modo **2. Projeção (2 Filtros)** ou **3. Colapso de Estado (3 Filtros)** na barra lateral para ver os cálculos de Dirac e a curva $\\cos^2(\\Delta\\theta/2)$.")
    else:
        col_dirac, col_curva = st.columns([1.1, 1])

        with col_dirac:
            st.subheader("Formalismo de Dirac")
            st.write(f"**1. Estado preparado pelo Filtro 1 ({feixe1}, {theta1}°) — $P_1 = {p_passou_f1:.3f}$:**")
            st.latex(
                rf"|\chi_1\rangle = \begin{{pmatrix}} {estado1[0].real + 0.0:.3f} \\ {estado1[1].real + 0.0:.3f} \end{{pmatrix}}"
            )

            if modo == "3. Colapso de Estado (3 Filtros)":
                st.write(f"**2. Colapso no Filtro 2 ({feixe2}, {theta2}°):**")
                st.latex(
                    rf"P(b|a) = |\langle {feixe2}\hat{{n}}_2 | \chi_1 \rangle|^2 = {p_passou_f2:.3f} "
                    rf"\quad \Longrightarrow \quad "
                    rf"|\chi_2\rangle = \begin{{pmatrix}} {estado2[0].real + 0.0:.3f} \\ {estado2[1].real + 0.0:.3f} \end{{pmatrix}}"
                )
                st.write(f"**3. Probabilidades condicionais no Filtro 3 ({theta3}°):**")
                st.latex(
                    rf"P(+|b) = |\langle +\hat{{n}}_3 | \chi_2 \rangle|^2 = {p_final_mais:.3f} "
                    rf"\qquad "
                    rf"P(-|b) = |\langle -\hat{{n}}_3 | \chi_2 \rangle|^2 = {p_final_menos:.3f}"
                )
                st.write("**4. Probabilidades totais desde a fonte (Regra da Cadeia):**")
                st.latex(
                    rf"P_{{\text{{total}}(+)}} = P(a)\,P(b|a)\,P(+|b) = {p_total_mais:.3f} "
                    rf"\qquad "
                    rf"P_{{\text{{total}}(-)}} = P(a)\,P(b|a)\,P(-|b) = {p_total_menos:.3f}"
                )
            else:
                st.write(f"**2. Probabilidades condicionais no Filtro 2 ({theta2}°):**")
                st.latex(
                    rf"P(+|a) = |\langle +\hat{{n}}_2 | \chi_1 \rangle|^2 = {p_final_mais:.3f} "
                    rf"\qquad "
                    rf"P(-|a) = |\langle -\hat{{n}}_2 | \chi_1 \rangle|^2 = {p_final_menos:.3f}"
                )
                st.write("**3. Probabilidades totais desde a fonte:**")
                st.latex(
                    rf"P_{{\text{{total}}(+)}} = P(a)\,P(+|a) = {p_total_mais:.3f} "
                    rf"\qquad "
                    rf"P_{{\text{{total}}(-)}} = P(a)\,P(-|a) = {p_total_menos:.3f}"
                )

            mais_f, _ = auto_spin(theta_anteparo)
            a0, a1 = mais_f[0].real + 0.0, mais_f[1].real + 0.0
            b0, b1 = estado_entrada[0].real + 0.0, estado_entrada[1].real + 0.0
            amp = a0 * b0 + a1 * b1

            with st.expander("🔍 Abrir conta do produto interno passo a passo"):
                st.latex(
                    rf"\langle +\hat{{n}} | \chi \rangle = "
                    rf"\begin{{pmatrix}} {a0:.3f} & {a1:.3f} \end{{pmatrix}}"
                    rf"\begin{{pmatrix}} {b0:.3f} \\ {b1:.3f} \end{{pmatrix}}"
                    rf"= ({a0:.3f})({b0:.3f}) + ({a1:.3f})({b1:.3f}) = {amp:.3f}"
                )
                st.latex(rf"P_+ = |{amp:.3f}|^2 = {amp**2:.3f}")

        with col_curva:
            st.subheader("Lei Quântica vs. Seu Experimento")
            angulos = np.linspace(0, 180, 181)
            curva_p = np.cos(np.radians(angulos) / 2) ** 2

            fig_c = go.Figure()
            fig_c.add_trace(go.Scatter(
                x=angulos, y=curva_p * 100, mode="lines",
                name="Teoria: cos²(Δθ/2)", line=dict(color="#60a5fa", width=3)
            ))
            if n_entrada_final > 0:
                fig_c.add_trace(go.Scatter(
                    x=[delta_theta], y=[pct_mais], mode="markers",
                    name="Seu experimento",
                    marker=dict(color="#f59e0b", size=14, symbol="star", line=dict(color="#fff", width=1.5))
                ))

            fig_c.update_layout(
                xaxis=dict(title="Ângulo relativo Δθ (°)", range=[-5, 185], gridcolor="#262a36"),
                yaxis=dict(title="Probabilidade de Saída (+) [%]", range=[-5, 108], gridcolor="#262a36"),
                height=360,
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", y=1.12, x=0.5, xanchor="center"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#12151e",
            )
            st.plotly_chart(fig_c, use_container_width=True)
            st.caption(
                "Note que na óptica clássica (Lei de Malus) a curva é $\\cos^2(\\Delta\\theta)$ e zera em $90^\\circ$. "
                "Para o spin-1/2, o fator $1/2$ faz a probabilidade zerar apenas em $180^\\circ$!"
            )

# --- ABA 4: ROTEIRO DE DESAFIOS ---
with aba_guia:
    st.subheader("Roteiro de Investigação (Prever → Testar → Explicar)")
    st.write("Use estes 3 desafios para conduzir a aula ou testar sua intuição quântica.")

    with st.container(border=True):
        st.markdown("### Desafio 1: O Choque da Quantização")
        st.write(
            "Um feixe térmico de átomos de prata sai do forno com spins em todas as direções possíveis "
            "e entra em um ímã vertical ($0^\\circ$). **O que aparece no anteparo?**"
        )
        st.button(
            "▶️ Carregar Desafio 1 na Bancada",
            on_click=carregar_cenario,
            args=("1. Quantização (1 Filtro)", 0, "+", 90, "+", 0, 1000)
        )
        with st.expander("Ver explicação"):
            st.write(
                "Em vez da linha contínua prevista pela física clássica, aparecem apenas duas manchas. "
                "A componente do momento angular intrínseco (spin) ao longo de qualquer eixo só pode assumir valores discretos ($\\pm \\hbar/2$)."
            )

    with st.container(border=True):
        st.markdown("### Desafio 2: Por que 90° não zera o feixe?")
        st.write(
            "Na óptica clássica, dois polarizadores cruzados a $90^\\circ$ bloqueiam 100% da luz. "
            "Se prepararmos átomos em $|+\\hat{z}\\rangle$ ($0^\\circ$) e medirmos em $90^\\circ$ ($\\hat{x}$), quantos passam?"
        )
        st.button(
            "▶️ Carregar Desafio 2 na Bancada",
            on_click=carregar_cenario,
            args=("2. Projeção (2 Filtros)", 0, "+", 90, "+", 0, 1000)
        )
        with st.expander("Ver explicação"):
            st.write(
                "Passam **50% em (+)** e **50% em (-)**! No espaço de Hilbert de spin-1/2, estados ortogonais estão separados por $180^\\circ$ "
                "no espaço real (e não $90^\\circ$). É por isso que a fórmula leva $\\theta/2$: $\\cos^2(90^\\circ/2) = \\cos^2(45^\\circ) = 0{,}5$."
            )

    with st.container(border=True):
        st.markdown("### Desafio 3: O Paradoxo do 3º Filtro ($z \\to x \\to z$)")
        st.write(
            "O Filtro 1 ($0^\\circ$) seleciona apenas $|+\\hat{z}\\rangle$ e descarta todos os $|-\\hat{z}\\rangle$. "
            "Se colocarmos um Filtro 2 em $90^\\circ$ (selecionando $+\\hat{x}$) antes de medir em $0^\\circ$ novamente, "
            "**algum átomo pode voltar a sair como $|-\\hat{z}\\rangle$?**"
        )
        c_d3a, c_d3b = st.columns(2)
        c_d3a.button(
            "▶️ Testar COM Filtro 2 em 90° (z → x → z)",
            on_click=carregar_cenario,
            args=("3. Colapso de Estado (3 Filtros)", 0, "+", 90, "+", 0, 1000),
            use_container_width=True
        )
        c_d3b.button(
            "▶️ Comparar com Filtro 2 em 0° (z → z → z)",
            on_click=carregar_cenario,
            args=("3. Colapso de Estado (3 Filtros)", 0, "+", 0, "+", 0, 1000),
            use_container_width=True
        )
        with st.expander("Ver explicação"):
            st.write(
                "Sim! Como os operadores $\\hat{S}_z$ e $\\hat{S}_x$ **não comutam**, o átomo não pode ter valores bem definidos "
                "de $S_z$ e $S_x$ ao mesmo tempo. Medir $S_x$ no Filtro 2 colapsa o estado para $|+\\hat{x}\\rangle = \\frac{1}{\\sqrt{2}}(|+\\hat{z}\\rangle + |-\\hat{z}\\rangle)$, "
                "fazendo a componente $|-\\hat{z}\\rangle$ reaparecer no Filtro 3."
            )

st.divider()
st.markdown(
    """
    <div style="text-align: center; font-size: 0.85rem; color: #94a3b8;">
        Desenvolvido por <strong style="color: #e2e8f0;">Prof. Wesley Sales de Souza</strong> •
        Licenciatura em Física • DEFIS – IFMA •
        Grupo de Magnetismo e Física Computacional (GMFC)
    </div>
    """,
    unsafe_allow_html=True,
)