from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import plotly.graph_objects as go
from S_G import auto_spin, P, simular_experimento

st.set_page_config(page_title="Laboratório Stern-Gerlach", page_icon="🧲", layout="wide")

st.markdown(
    """
    <style>
    @media (max-width: 768px) { 
        .modebar-container, .modebar {
            display: none !important;
        }
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 1.5rem !important;
        }
        h1 { font-size: 1.45rem !important; }
        h2, h3 { font-size: 1.12rem !important; }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem !important;
            flex-wrap: wrap !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem !important;
            padding: 0.35rem 0.5rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.78rem !important;
        }

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
    "usar_seed": False,
    "seed_valor": 42,
    "disparo_id": 0,
    "sim_assinatura": None,
    "sim_resultado": None,
    "sim_coords": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def acionar_novo_disparo():
    if st.session_state.usar_seed:
        st.session_state.seed_valor += 1
    else:
        st.session_state.disparo_id += 1


def carregar_cenario(modo, t1=0, f1="+", t2=90, f2="+", t3=0, n=1000):
    st.session_state.modo = modo
    st.session_state.theta1 = t1
    st.session_state.feixe1 = f1
    st.session_state.theta2 = t2
    st.session_state.feixe2 = f2
    st.session_state.theta3 = t3
    st.session_state.n_atomos = n
    st.session_state.disparo_id += 1


# --- Cabeçalho ---
col_tit, col_btn = st.columns([4, 1])
with col_tit:
    st.title("🧲 Laboratório Virtual de Stern-Gerlach")
    st.caption("Simulação interativa de quantização do spin-1/2, preparação de estados e medição quântica.")
with col_btn:
    st.write("")
    st.button(
        "🔄 Novo disparo",
        on_click=acionar_novo_disparo,
        use_container_width=True,
        help="Executa uma nova realização estatística com os mesmos parâmetros físicos",
    )

# --- Barra lateral organizada por estágio experimental ---
st.sidebar.header("Modalidade Experimental")
modo = st.sidebar.radio(
    "Configuração do aparato:",
    [
        "1. Quantização (1 Filtro)",
        "2. Projeção (2 Filtros)",
        "3. Colapso de Estado (3 Filtros)",
    ],
    key="modo",
)

st.sidebar.divider()

with st.sidebar.expander("⚙️ Configuração da Fonte", expanded=True):
    n_atomos = st.slider("Átomos emitidos (N₀)", 20, 5000, step=20, key="n_atomos")
    st.caption("Feixe térmico não polarizado (ρ̂ = Î/2).")

if modo == "1. Quantização (1 Filtro)":
    with st.sidebar.expander("🧲 Filtro 1 — Analisador", expanded=True):
        theta1 = st.slider("Orientação θ₁ (°)", 0, 180, key="theta1")

elif modo == "2. Projeção (2 Filtros)":
    with st.sidebar.expander("🧲 Filtro 1 — Preparador", expanded=True):
        theta1 = st.slider("Orientação θ₁ (°)", 0, 180, key="theta1")
        feixe1 = st.radio("Canal transmitido (F1)", ["+", "-"], horizontal=True, key="feixe1")
    with st.sidebar.expander("🧲 Filtro 2 — Analisador", expanded=True):
        theta2 = st.slider("Orientação θ₂ (°)", 0, 180, key="theta2")

else:
    with st.sidebar.expander("🧲 Filtro 1 — Preparador", expanded=True):
        theta1 = st.slider("Orientação θ₁ (°)", 0, 180, key="theta1")
        feixe1 = st.radio("Canal transmitido (F1)", ["+", "-"], horizontal=True, key="feixe1")
    with st.sidebar.expander("🧲 Filtro 2 — Intermediário", expanded=True):
        theta2 = st.slider("Orientação θ₂ (°)", 0, 180, key="theta2")
        feixe2 = st.radio("Canal transmitido (F2)", ["+", "-"], horizontal=True, key="feixe2")
    with st.sidebar.expander("🧲 Filtro 3 — Analisador Final", expanded=True):
        theta3 = st.slider("Orientação θ₃ (°)", 0, 180, key="theta3")

with st.sidebar.expander("🎲 Controle Estatístico (Semente)", expanded=False):
    st.checkbox(
        "Fixar semente aleatória",
        key="usar_seed",
        help="Permite reproduzir exatamente a mesma realização estatística",
    )
    if st.session_state.usar_seed:
        st.number_input("Valor da semente", min_value=0, max_value=999999, step=1, key="seed_valor")
        st.caption("Com semente fixa, 'Novo disparo' incrementa a semente em +1.")

st.sidebar.divider()
st.sidebar.caption("💡 Reduza N₀ (ex.: 40 átomos) e execute novos disparos para observar flutuações estatísticas em amostras finitas.")

st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.45;">
        <strong style="color: #e2e8f0;">Wesley Sales de Souza</strong><br>
        Licenciatura em Física<br>
        DEFIS – IFMA<br>
        <em>Grupo de Magnetismo e Física Computacional (GMFC)</em>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Motor Físico Persistente ---
modo_id = 1 if modo.startswith("1.") else (2 if modo.startswith("2.") else 3)

assinatura_atual = (
    modo_id,
    n_atomos,
    st.session_state.theta1,
    st.session_state.feixe1,
    st.session_state.theta2,
    st.session_state.feixe2,
    st.session_state.theta3,
    st.session_state.usar_seed,
    st.session_state.seed_valor if st.session_state.usar_seed else None,
    st.session_state.disparo_id,
)

if st.session_state.sim_assinatura != assinatura_atual or st.session_state.sim_resultado is None:
    rng = (
        np.random.default_rng(int(st.session_state.seed_valor))
        if st.session_state.usar_seed
        else np.random.default_rng()
    )

    sim_novo = simular_experimento(
        n0=n_atomos,
        modo_id=modo_id,
        theta1=st.session_state.theta1,
        feixe1=st.session_state.feixe1,
        theta2=st.session_state.theta2,
        feixe2=st.session_state.feixe2,
        theta3=st.session_state.theta3,
        rng=rng,
    )

    rad = np.radians(sim_novo["theta_anteparo"])
    cx, cz = np.sin(rad), np.cos(rad)
    px, pz = cz, -cx

    u_cl = rng.uniform(-1.0, 1.0, n_atomos)
    ruido_t = rng.normal(0, 0.12, n_atomos)

    coords_novas = {
        "cx": cx,
        "cz": cz,
        "x_mais": rng.normal(cx, 0.14, sim_novo["n_final_mais"]),
        "z_mais": rng.normal(cz, 0.14, sim_novo["n_final_mais"]),
        "x_menos": rng.normal(-cx, 0.14, sim_novo["n_final_menos"]),
        "z_menos": rng.normal(-cz, 0.14, sim_novo["n_final_menos"]),
        "xc": u_cl * cx + ruido_t * px,
        "zc": u_cl * cz + ruido_t * pz,
    }

    st.session_state.sim_assinatura = assinatura_atual
    st.session_state.sim_resultado = sim_novo
    st.session_state.sim_coords = coords_novas

sim = st.session_state.sim_resultado
coords = st.session_state.sim_coords

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
desvio_mais = sim["desvio_mais"]
desvio_menos = sim["desvio_menos"]

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


# --- Bancada SVG Responsiva ---
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
        <text x="390" y="96" fill="#fcd34d" font-size="13" text-anchor="middle">θ₁ = {st.session_state.theta1}°</text>

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
        <text x="257" y="95" fill="#93c5fd" font-size="12" text-anchor="middle">θ₁ = {st.session_state.theta1}° | só ({st.session_state.feixe1})</text>

        <line x1="320" y1="68" x2="455" y2="68" stroke="#38bdf8" stroke-width="{w_f1:.1f}"/>
        <text x="387" y="56" fill="#38bdf8" font-size="12" text-anchor="middle" font-weight="bold">{n_ent_2} em |χ₁⟩</text>

        <line x1="320" y1="95" x2="370" y2="128" stroke="#EF553B" stroke-width="2" stroke-dasharray="4,3"/>
        <rect x="370" y="118" width="8" height="22" rx="2" fill="#EF553B"/>
        <text x="385" y="134" fill="#fca5a5" font-size="11">{n_bloq_f1} bloq.</text>

        <rect x="455" y="40" width="125" height="80" rx="10" fill="#1e293b" stroke="#f59e0b" stroke-width="2.5"/>
        <text x="517" y="72" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Filtro 2 (Med.)</text>
        <text x="517" y="95" fill="#fcd34d" font-size="12" text-anchor="middle">θ₂ = {st.session_state.theta2}°</text>

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
        <text x="179" y="94" fill="#93c5fd" font-size="12" text-anchor="middle">θ₁={st.session_state.theta1}° ({st.session_state.feixe1})</text>

        <line x1="233" y1="68" x2="328" y2="68" stroke="#38bdf8" stroke-width="{w_f1:.1f}"/>
        <text x="280" y="56" fill="#38bdf8" font-size="11" text-anchor="middle" font-weight="bold">{n_ent_2} passam</text>

        <line x1="233" y1="95" x2="268" y2="128" stroke="#EF553B" stroke-width="2" stroke-dasharray="4,3"/>
        <rect x="268" y="118" width="7" height="20" rx="2" fill="#EF553B"/>
        <text x="280" y="133" fill="#fca5a5" font-size="10">{n_bloq_f1} bloq.</text>

        <rect x="328" y="42" width="108" height="76" rx="8" fill="#1e293b" stroke="#a78bfa" stroke-width="2"/>
        <text x="382" y="72" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Filtro 2</text>
        <text x="382" y="94" fill="#c4b5fd" font-size="12" text-anchor="middle">θ₂={st.session_state.theta2}° ({st.session_state.feixe2})</text>

        <line x1="436" y1="68" x2="545" y2="68" stroke="#a78bfa" stroke-width="{w_mid:.1f}"/>
        <text x="490" y="56" fill="#c4b5fd" font-size="11" text-anchor="middle" font-weight="bold">{n_entrada_final} passam</text>

        <line x1="436" y1="95" x2="482" y2="128" stroke="#EF553B" stroke-width="2" stroke-dasharray="4,3"/>
        <rect x="482" y="118" width="7" height="20" rx="2" fill="#EF553B"/>
        <text x="495" y="133" fill="#fca5a5" font-size="10">{n_bloq_f2} bloq.</text>

        <rect x="545" y="42" width="108" height="76" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="2.5"/>
        <text x="599" y="72" fill="#fff" font-size="13" text-anchor="middle" font-weight="bold">Filtro 3</text>
        <text x="599" y="94" fill="#fcd34d" font-size="12" text-anchor="middle">θ₃={st.session_state.theta3}°</text>

        <line x1="653" y1="68" x2="765" y2="38" stroke="#00CC96" stroke-width="{w_mais:.1f}"/>
        <text x="710" y="38" fill="#00CC96" font-size="12" text-anchor="middle" font-weight="bold">+ ({n_final_mais})</text>

        <line x1="653" y1="92" x2="765" y2="122" stroke="#EF553B" stroke-width="{w_menos:.1f}"/>
        <text x="710" y="136" fill="#EF553B" font-size="12" text-anchor="middle" font-weight="bold">- ({n_final_menos})</text>

        <rect x="768" y="20" width="14" height="120" rx="4" fill="#e2e8f0"/>
        <text x="818" y="84" fill="#e2e8f0" font-size="12" text-anchor="middle" font-weight="bold">Tela</text>
        """

    html = f"""
    <style>
      .bancada-wrap {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; }}
      .bancada-svg {{ width: 100%; height: 155px; display: block; background:#161922; border-radius:12px; border:1px solid #2d3240; }}
      @media (max-width: 768px) {{
        .bancada-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
        .bancada-svg {{ min-width: 680px; height: 145px; }}
      }}
    </style>
    <div class="bancada-wrap">
      <svg class="bancada-svg" viewBox="0 0 860 160">
        {corpo}
      </svg>
    </div>
    """
    components.html(html, height=166)
    st.caption("Diagrama esquemático do fluxo de partículas (N_+ + N_- = N_entrada em cada analisador).")


# --- Gráficos ---
def grafico_quantico(altura=380):
    cx, cz = coords["cx"], coords["cz"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[-1.7 * cx, 1.7 * cx], y=[-1.7 * cz, 1.7 * cz],
        mode="lines", name="Eixo do Ímã (B)",
        line=dict(color="rgba(255, 255, 255, 0.3)", width=2, dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=coords["x_mais"], y=coords["z_mais"], mode="markers", name="Spin (+ℏ/2)",
        marker=dict(color="#00CC96", size=5, opacity=0.7)
    ))
    fig.add_trace(go.Scatter(
        x=coords["x_menos"], y=coords["z_menos"], mode="markers", name="Spin (-ℏ/2)",
        marker=dict(color="#EF553B", size=5, opacity=0.7)
    ))
    fig.update_layout(
        title=dict(text=f"⚛️ Anteparo Quântico (esquemático) — {nome_final} (θ = {theta_anteparo}°)", font=dict(size=14)),
        xaxis=dict(title="Eixo x", range=[-2, 2], zeroline=True, gridcolor="#262a36"),
        yaxis=dict(title="Eixo z", range=[-2, 2], zeroline=True, gridcolor="#262a36", scaleanchor="x", scaleratio=1),
        height=altura,
        margin=dict(l=15, r=15, t=50, b=90),
        legend=dict(orientation="h", yanchor="top", y=-0.26, xanchor="center", x=0.5, font=dict(size=11)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#12151e",
    )
    return fig


def grafico_classico(altura=350):
    cx, cz = coords["cx"], coords["cz"]

    texto_classico = (
        "**Modelo Clássico (idealização didática):** Assumindo dipolos magnéticos clássicos orientados isotropicamente em 3D, "
        "a componente $\\mu_n = \\mu \\cos\\alpha$ varia continuamente em $[-\\mu, +\\mu]$. Sob um gradiente de campo $\\partial B_n / \\partial n$, "
        "a deflexão deveria formar uma **faixa contínua** sobre o anteparo."
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[-1.7 * cx, 1.7 * cx], y=[-1.7 * cz, 1.7 * cz],
        mode="lines", name="Eixo do Ímã (B)",
        line=dict(color="rgba(255, 255, 255, 0.3)", width=2, dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=coords["xc"], y=coords["zc"], mode="markers", name="Dipolo clássico (contínuo)",
        marker=dict(color="#F59E0B", size=5, opacity=0.65)
    ))
    fig.update_layout(
        title=dict(text=f"🏛️ Previsão Clássica (esquemática) — {nome_final} (θ = {theta_anteparo}°)", font=dict(size=14)),
        xaxis=dict(title="Eixo x", range=[-2, 2], zeroline=True, gridcolor="#262a36"),
        yaxis=dict(title="Eixo z", range=[-2, 2], zeroline=True, gridcolor="#262a36", scaleanchor="x", scaleratio=1),
        height=altura,
        margin=dict(l=15, r=15, t=50, b=90),
        legend=dict(orientation="h", yanchor="top", y=-0.26, xanchor="center", x=0.5, font=dict(size=11)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#12151e",
    )
    return fig, texto_classico


def grafico_barras():
    fig_bar = go.Figure(data=[
        go.Bar(
            name="Frequência observada",
            x=["Saída (+)", "Saída (-)"],
            y=[pct_mais, pct_menos],
            marker_color=["#00CC96", "#EF553B"],
        ),
        go.Bar(
            name="Probabilidade teórica",
            x=["Saída (+)", "Saída (-)"],
            y=[p_final_mais * 100, p_final_menos * 100],
            marker_color=["rgba(0,204,150,0.3)", "rgba(239,85,59,0.3)"],
        ),
    ])
    fig_bar.update_layout(
        barmode="group",
        yaxis=dict(title="Fração (%)", range=[0, 108]),
        height=210,
        margin=dict(l=10, r=10, t=25, b=10),
        legend=dict(orientation="h", y=1.18, x=0.5, xanchor="center", font=dict(size=11)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig_bar


def exibir_explicacao_quantica():
    if modo == "1. Quantização (1 Filtro)":
        st.info(
            "**Quantização espacial do spin:** O momento angular intrínseco é quantizado. "
            "Para qualquer orientação do gradiente magnético, a medição de $\\hat{S}_n$ retorna apenas dois autovalores discretos: $+\\hbar/2$ e $-\\hbar/2$."
        )
    elif modo == "3. Colapso de Estado (3 Filtros)" and n_entrada_final == 0:
        st.warning(
            "**Bloqueio total no Filtro 2:** Nenhuma partícula alcançou o Filtro 3 porque o canal selecionado em F2 "
            "corresponde a um autoestado ortogonal ao estado preparado em F1."
        )
    elif (
        modo == "3. Colapso de Estado (3 Filtros)"
        and st.session_state.theta1 == st.session_state.theta3
        and abs(st.session_state.theta2 - st.session_state.theta1) == 90
    ):
        st.success(
            "**Reaparição por medição intermediária ($z \\to x \\to z$):** Como $[\\hat{S}_z, \\hat{S}_x] \\neq 0$, "
            "a seleção em $90^\\circ$ no Filtro 2 projeta o sistema em uma superposição de $|+z\\rangle$ e $|-z\\rangle$, restaurando a probabilidade de $50\\%$ para a componente anteriormente bloqueada."
        )
    elif abs(p_final_mais - 1.0) < 1e-6 or abs(p_final_menos - 1.0) < 1e-6:
        st.info(
            "**Autoestado do observável medido:** O estado incidente coincide com um autoestado do analisador final; "
            "a medição é determinística ($P = 1$ em um único canal)."
        )
    elif abs(p_final_mais - 0.5) < 1e-3:
        st.info(
            "**Superposição simétrica ($50\\% / 50\\%$):** O eixo do analisador é ortogonal ($90^\\circ$) ao eixo de preparação. "
            "As amplitudes de probabilidade têm igual módulo ($1/\\sqrt{2}$)."
        )
    else:
        st.info(
            f"**Projeção oblíqua ($\\Delta\\theta = {delta_theta:.0f}^\\circ$):** A probabilidade condicional segue "
            f"$P_+ = \\cos^2({delta_theta:.0f}^\\circ / 2) = {p_final_mais:.3f}$."
        )


def rotulo_eixo(theta: float) -> str:
    if theta == 0:
        return "z"
    if theta == 90:
        return "x"
    return rf"\hat{{n}}({theta:.0f}^\circ)"


def expansao_dirac(theta: float, sinal: str = "+") -> str:
    """Retorna a expansão em notação de Dirac na base {|+z>, |-z>}."""
    if theta == 0:
        return r"|+z\rangle" if sinal == "+" else r"|-z\rangle"
    if theta == 90:
        op = "+" if sinal == "+" else "-"
        return rf"\frac{{1}}{{\sqrt{{2}}}}\left(|+z\rangle {op} |-z\rangle\right)"
    if theta == 180:
        return r"|-z\rangle" if sinal == "+" else r"-|+z\rangle"

    v_mais, v_menos = auto_spin(theta)
    v = v_mais if sinal == "+" else v_menos
    c0, c1 = v[0].real + 0.0, v[1].real + 0.0
    sinal_c1 = "+" if c1 >= 0 else "-"
    return rf"{c0:.3f}|+z\rangle {sinal_c1} {abs(c1):.3f}|-z\rangle"


def renderizar_analise_teorica_configuracao():
    """Exibe o desenvolvimento matemático dinâmico sincronizado com a bancada."""
    with st.expander("📐 Desenvolvimento Matemático da Configuração Atual", expanded=True):
        eixo_f = rotulo_eixo(theta_anteparo)

        if modo_id == 1:
            t1 = st.session_state.theta1
            st.markdown(f"**1. Estado de entrada (fonte não polarizada) e 2–3. Operador medido ($\\theta_1 = {t1}^\\circ$):**")
            st.latex(
                rf"\hat{{\rho}} = \frac{{\hat{{I}}}}{{2}} = \frac{{1}}{{2}}\left(|+z\rangle\langle +z| + |-z\rangle\langle -z|\right), "
                rf"\qquad \hat{{S}}_{{{eixo_f}}} = \frac{{\hbar}}{{2}}|+{eixo_f}\rangle\langle +{eixo_f}| - \frac{{\hbar}}{{2}}|-{eixo_f}\rangle\langle -{eixo_f}|"
            )
            st.markdown("**4. Autoestados da base de medição:**")
            st.latex(
                rf"|+{eixo_f}\rangle = {expansao_dirac(t1, '+')}, \qquad "
                rf"|-{eixo_f}\rangle = {expansao_dirac(t1, '-')}"
            )
            st.markdown("**5–6. Probabilidades teóricas via matriz densidade:**")
            st.latex(
                rf"P(+{eixo_f}) = \operatorname{{Tr}}(\hat{{\rho}}\hat{{P}}_+) = \frac{{1}}{{2}} = 0.500, \qquad "
                rf"P(-{eixo_f}) = \operatorname{{Tr}}(\hat{{\rho}}\hat{{P}}_-) = \frac{{1}}{{2}} = 0.500"
            )
            st.markdown(
                f"**7. Estado após a medição:** cada átomo detectado no canal $(+)$ ou $(-)$ colapsa para "
                f"$|+{eixo_f}\\rangle$ ou $|-{eixo_f}\\rangle$, respectivamente."
            )

        else:
            theta_in = st.session_state.theta1 if modo_id == 2 else st.session_state.theta2
            feixe_in = st.session_state.feixe1 if modo_id == 2 else st.session_state.feixe2
            eixo_in = rotulo_eixo(theta_in)
            ket_in = rf"|{feixe_in}{eixo_in}\rangle"

            mais_f, menos_f = auto_spin(theta_anteparo)
            amp_mais = complex(np.vdot(mais_f, estado_entrada)).real + 0.0
            amp_menos = complex(np.vdot(menos_f, estado_entrada)).real + 0.0

            st.markdown(f"**1. Estado de entrada no {nome_final}:**")
            st.latex(rf"|\psi_{{\mathrm{{in}}}}\rangle = {ket_in} = {expansao_dirac(theta_in, feixe_in)}")

            st.markdown(f"**2–4. Base de medição, operador $\\hat{{S}}_{{{eixo_f}}}$ e autoestados ($\\theta = {theta_anteparo}^\\circ$):**")
            st.latex(
                rf"|+{eixo_f}\rangle = {expansao_dirac(theta_anteparo, '+')}, \qquad "
                rf"|-{eixo_f}\rangle = {expansao_dirac(theta_anteparo, '-')}"
            )

            st.markdown("**5. Amplitudes de probabilidade (produto interno):**")
            st.latex(
                rf"\langle +{eixo_f}|\psi_{{\mathrm{{in}}}}\rangle = {amp_mais:.3f}, \qquad "
                rf"\langle -{eixo_f}|\psi_{{\mathrm{{in}}}}\rangle = {amp_menos:.3f}"
            )

            st.markdown("**6. Probabilidades teóricas (Regra de Born e Regra da Cadeia):**")
            st.latex(
                rf"P(+{eixo_f} | \psi_{{\mathrm{{in}}}}) = |\langle +{eixo_f}|\psi_{{\mathrm{{in}}}}\rangle|^2 = \cos^2\!\left(\frac{{{delta_theta:.0f}^\circ}}{{2}}\right) = {p_final_mais:.3f}, \qquad "
                rf"P(-{eixo_f} | \psi_{{\mathrm{{in}}}}) = \sin^2\!\left(\frac{{{delta_theta:.0f}^\circ}}{{2}}\right) = {p_final_menos:.3f}"
            )
            st.latex(
                rf"P_{{\mathrm{{total}}(+)}} = {p_total_mais:.3f} \;({p_total_mais*100:.1f}\%), \qquad "
                rf"P_{{\mathrm{{total}}(-)}} = {p_total_menos:.3f} \;({p_total_menos*100:.1f}\%)"
            )

            st.markdown("**7. Atualização do estado pós-medição (projetores $\\hat{P}_\\pm$):**")
            st.latex(
                rf"|\psi'\rangle = \frac{{\hat{{P}}_\pm |\psi_{{\mathrm{{in}}}}\rangle}}{{\sqrt{{\langle\psi_{{\mathrm{{in}}}}|\hat{{P}}_\pm|\psi_{{\mathrm{{in}}}}\rangle}}}} = |\pm {eixo_f}\rangle"
            )

        st.markdown("**8. Comparação com a realização estatística atual:**")
        if n_entrada_final > 0:
            st.markdown(
                f"- **Canal $(+)$:** observado $f_+ = {pct_mais:.1f}\\%$ ($N_+ = {n_final_mais}/{n_entrada_final}$) vs. teórico $P_+ = {p_final_mais*100:.1f}\\%$ "
                f"| desvio $= {desvio_mais*100:+.1f}\\%$ | incerteza esperada $\\sigma_f = \\pm{sigma_f*100:.2f}\\%$.\n"
                f"- **Canal $(-)$:** observado $f_- = {pct_menos:.1f}\\%$ ($N_- = {n_final_menos}/{n_entrada_final}$) vs. teórico $P_- = {p_final_menos*100:.1f}\\%$ "
                f"| desvio $= {desvio_menos*100:+.1f}\\%$."
            )
        else:
            st.markdown("Nenhuma partícula atingiu o analisador final ($N_{\\mathrm{entrada}} = 0$); não há amostra estatística para comparação.")


def renderizar_formalismo_teorico():
    st.subheader("Formalismo Quântico em Notação de Dirac")
    st.caption(
        "Desenvolvimento progressivo da descrição matemática do spin-1/2 no experimento de Stern–Gerlach. "
        "As representações matriciais são utilizadas apenas como suporte computacional."
    )

    with st.expander("1. Introdução ao Experimento de Stern–Gerlach", expanded=False):
        st.markdown(
            "Um feixe colimado de átomos de prata (com momento angular orbital $L=0$ e um elétron de valência de spin $s=1/2$) "
            "atravessa uma região com campo magnético não uniforme $\\vec{B}$. A força sobre um dipolo magnético $\\vec{\\mu}$ ao longo "
            "do eixo $\\hat{n}$ do gradiente é dada por:"
        )
        st.latex(r"F_n = \mu_n \frac{\partial B_n}{\partial n}, \qquad \vec{\mu} = \frac{g_s q}{2m}\vec{S}")
        st.markdown(
            "Enquanto o modelo clássico prevê uma distribuição contínua de projeções $\\mu_n \\in [-\\mu, +\\mu]$, o experimento revela "
            "**apenas dois feixes discretos**, evidenciando que a componente do spin ao longo de qualquer eixo $\\hat{n}$ só assume os autovalores $\\pm \\hbar/2$."
        )

    with st.expander("2. Estados de Spin-1/2, Bases, Ortonormalidade e Completeza", expanded=False):
        st.markdown(
            "O espaço de Hilbert de uma partícula de spin-1/2 é bidimensional ($\\mathcal{H} = \\mathbb{C}^2$). "
            "A base padrão é formada pelos autoestados de $\\hat{S}_z$:"
        )
        st.latex(r"|+z\rangle, \qquad |-z\rangle")
        st.markdown("Estes estados satisfazem as relações de **ortonormalidade** e **completeza (resolução da identidade)**:")
        st.latex(r"\langle +z|+z\rangle = 1, \qquad \langle -z|-z\rangle = 1, \qquad \langle +z|-z\rangle = 0")
        st.latex(r"|+z\rangle\langle +z| + |-z\rangle\langle -z| = \hat{I}")
        st.markdown(
            "Um mesmo estado quântico pode ser expresso em qualquer outra base ortonormal. Por exemplo, os autoestados de $\\hat{S}_x$ "
            "são combinações lineares (superposições coerentes) dos autoestados de $\\hat{S}_z$:"
        )
        st.latex(
            r"|+x\rangle = \frac{1}{\sqrt{2}}\left(|+z\rangle + |-z\rangle\right), \qquad "
            r"|-x\rangle = \frac{1}{\sqrt{2}}\left(|+z\rangle - |-z\rangle\right)"
        )
        st.markdown(
            "Para qualquer direção arbitrária $\\hat{n}$, os autoestados $|+\\hat{n}\\rangle$ e $|-\\hat{n}\\rangle$ também formam uma base ortonormal completa: "
            "$\\langle +\\hat{n}|-\\hat{n}\\rangle = 0$ e $|+\\hat{n}\\rangle\\langle +\\hat{n}| + |-\\hat{n}\\rangle\\langle -\\hat{n}| = \\hat{I}$."
        )

    with st.expander("3. Operadores de Spin, Observáveis e Representação Espectral", expanded=False):
        st.markdown(
            "Cada orientação do analisador de Stern–Gerlach define o observável físico que está sendo medido. "
            "Os operadores cartesianos de spin relacionam-se às matrizes de Pauli $\\sigma_i$ ($i \\in \\{x, y, z\\}$) por:"
        )
        st.latex(r"\hat{S}_i = \frac{\hbar}{2}\sigma_i")
        st.markdown("Suas equações de autovalor são:")
        st.latex(r"\hat{S}_z |\pm z\rangle = \pm \frac{\hbar}{2} |\pm z\rangle, \qquad \hat{S}_x |\pm x\rangle = \pm \frac{\hbar}{2} |\pm x\rangle")
        st.markdown("Em notação de Dirac, qualquer operador de spin admite a **representação espectral**:")
        st.latex(r"\hat{S}_z = \frac{\hbar}{2}|+z\rangle\langle +z| - \frac{\hbar}{2}|-z\rangle\langle -z|")
        st.latex(r"\hat{S}_n = \vec{S}\cdot\hat{n} = \frac{\hbar}{2}|+\hat{n}\rangle\langle +\hat{n}| - \frac{\hbar}{2}|-\hat{n}\rangle\langle -\hat{n}|")
        st.markdown("Como $[\\hat{S}_x, \\hat{S}_z] = -i\\hbar\\hat{S}_y \\neq 0$, os observáveis $\\hat{S}_x$ e $\\hat{S}_z$ são **incompatíveis** e não possuem uma base comum de autoestados.")

    with st.expander("4. Regra de Born e Amplitudes de Probabilidade", expanded=False):
        st.markdown(
            "Dado um sistema preparado no estado puro normalizado $|\\psi\\rangle$, a **amplitude de probabilidade** de obter o resultado associado "
            "ao autoestado $|a\\rangle$ é o produto interno complexo $\\langle a|\\psi\\rangle$. Pela **regra de Born**, a probabilidade física é o módulo quadrado dessa amplitude:"
        )
        st.latex(r"P(a) = |\langle a|\psi\rangle|^2")
        st.markdown("**Exemplo completo:** preparando $|\\psi\\rangle = |+z\\rangle$ e medindo $\\hat{S}_x$, temos:")
        st.latex(
            r"\langle +x|+z\rangle = \frac{1}{\sqrt{2}}\left(\langle +z| + \langle -z|\right)|+z\rangle "
            r"= \frac{1}{\sqrt{2}}\left(\underbrace{\langle +z|+z\rangle}_{1} + \underbrace{\langle -z|+z\rangle}_{0}\right) = \frac{1}{\sqrt{2}}"
        )
        st.latex(r"P(+x|+z) = \left|\frac{1}{\sqrt{2}}\right|^2 = \frac{1}{2}, \qquad P(-x|+z) = \left|\frac{1}{\sqrt{2}}\right|^2 = \frac{1}{2}")
        st.markdown(
            "A **amplitude** pode ser negativa ou complexa e carrega informação de fase (essencial para interferência); "
            "já a **probabilidade** é sempre real, não negativa e satisfaz $P(+) + P(-) = 1$."
        )

    with st.expander("5. Projetores e Processo de Medição (Colapso de Estado)", expanded=False):
        st.markdown("Associamos a cada canal de saída de um analisador na direção $\\hat{n}$ um **operador projetor**:")
        st.latex(r"\hat{P}_+ = |+\hat{n}\rangle\langle +\hat{n}|, \qquad \hat{P}_- = |-\hat{n}\rangle\langle -\hat{n}|")
        st.markdown("Estes operadores satisfazem idempotência, ortogonalidade e completeza:")
        st.latex(r"\hat{P}_+^2 = \hat{P}_+, \qquad \hat{P}_-^2 = \hat{P}_-, \qquad \hat{P}_+\hat{P}_- = 0, \qquad \hat{P}_+ + \hat{P}_- = \hat{I}")
        st.markdown("As probabilidades podem ser escritas diretamente como valores esperados dos projetores:")
        st.latex(r"P(\pm) = \langle\psi|\hat{P}_\pm|\psi\rangle")
        st.markdown("Quando um feixe atravessa o analisador e apenas o canal $(+)$ é selecionado, o estado pós-medição é atualizado (colapso projetivo) para:")
        st.latex(r"|\psi'\rangle = \frac{\hat{P}_+|\psi\rangle}{\sqrt{\langle\psi|\hat{P}_+|\psi\rangle}}")
        st.markdown("Na simulação, bloquear um dos canais em F1 ou F2 corresponde exatamente à aplicação desse postulado de projeção.")

    with st.expander("6. Estados Puros, Estados Mistos e Matriz Densidade", expanded=False):
        st.markdown(
            "Átomos emitidos por um forno térmico não estão em um estado puro único: formam um **ensemble estatístico** com orientações aleatórias. "
            "Descrevemos esse feixe não polarizado pela **matriz densidade**:"
        )
        st.latex(r"\hat{\rho} = \frac{1}{2}\left(|+z\rangle\langle +z| + |-z\rangle\langle -z|\right) = \frac{\hat{I}}{2}")
        st.markdown(
            "Um erro comum é confundir o feixe não polarizado com a superposição coerente $|+x\\rangle = \\frac{1}{\\sqrt{2}}(|+z\\rangle + |-z\\rangle)$. "
            "No estado puro $|+x\\rangle$, uma medição em $x$ dá $P(+x) = 1$; já no estado misto $\\hat{\\rho} = \\hat{I}/2$, **qualquer** direção $\\hat{n}$ produz $50\\% / 50\\%$:"
        )
        st.latex(r"P(\pm) = \operatorname{Tr}\!\left(\hat{\rho}\,\hat{P}_\pm\right) = \frac{1}{2}\operatorname{Tr}(\hat{P}_\pm) = \frac{1}{2}")
        st.markdown("Na simulação, a fonte emite $N_0$ átomos nesse estado misto; o Filtro 1 atua como preparador, convertendo o feixe transmitido em um estado puro.")

    with st.expander("7. Sequências de Analisadores e a Cascata z → x → z", expanded=False):
        st.markdown("Para uma sequência de três analisadores com canais selecionados $(a, b, c)$, a probabilidade total de um átomo emitido pela fonte alcançar o canal final segue a regra da cadeia:")
        st.latex(r"P(a, b, c) = P(a)\,P(b|a)\,P(c|a, b)")
        st.markdown("Considere a sequência clássica:")
        st.latex(r"|+z\rangle \;\longrightarrow\; \text{analisador em } x \text{ (seleciona } +x\text{)} \;\longrightarrow\; \text{analisador em } z")
        st.markdown("Ao selecionar $|+x\\rangle = \\frac{1}{\\sqrt{2}}(|+z\\rangle + |-z\\rangle)$ no Filtro 2, a medição final em $z$ fornece:")
        st.latex(r"P(+z|+x) = |\langle +z|+x\rangle|^2 = \frac{1}{2}, \qquad P(-z|+x) = |\langle -z|+x\rangle|^2 = \frac{1}{2}")
        st.markdown(
            "A componente $|-z\\rangle$, completamente descartada pelo Filtro 1, **reaparece** porque a medição intermediária em $x$ "
            "altera irreversivelmente o estado quântico (diferentemente da passagem livre pelo espaço sem medição)."
        )

    with st.expander("8. Generalização para Direções Tridimensionais e Esfera de Bloch", expanded=False):
        st.markdown(
            "Para uma direção arbitrária $\\hat{n} = (\\sin\\theta\\cos\\phi,\\, \\sin\\theta\\sin\\phi,\\, \\cos\\theta)$ "
            "parametrizada pelos ângulos polar $\\theta \\in [0, \\pi]$ e azimutal $\\phi \\in [0, 2\\pi)$, os autoestados de $\\hat{S}_n$ são:"
        )
        st.latex(
            r"|+\hat{n}\rangle = \cos\frac{\theta}{2}|+z\rangle + e^{i\phi}\sin\frac{\theta}{2}|-z\rangle, \qquad "
            r"|-\hat{n}\rangle = -e^{-i\phi}\sin\frac{\theta}{2}|+z\rangle + \cos\frac{\theta}{2}|-z\rangle"
        )
        st.markdown(
            "Geometricamente, cada estado puro de spin-1/2 corresponde a um ponto na superfície da **esfera de Bloch**. "
            "Estados ortogonais ocupam pontos antípodas ($180^\\circ$). Se um estado $|+\\hat{n}_1\\rangle$ é medido na direção $\\hat{n}_2$ "
            "com ângulo $\\gamma$ entre os eixos ($\\cos\\gamma = \\hat{n}_1 \\cdot \\hat{n}_2$), as probabilidades de transição dependem apenas de $\\gamma$:"
        )
        st.latex(r"P(+\hat{n}_2 | +\hat{n}_1) = \cos^2\!\left(\frac{\gamma}{2}\right), \qquad P(-\hat{n}_2 | +\hat{n}_1) = \sin^2\!\left(\frac{\gamma}{2}\right)")


# ==========================================================
# ABAS PRINCIPAIS
# ==========================================================
aba_exp, aba_aparato, aba_alg, aba_guia = st.tabs([
    "🧪 Bancada do Experimento",
    "🎬 Aparato Físico (3D)",
    "📐 Formalismo Quântico",
    "🎯 Roteiro de Investigação"
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
            fig_cl, txt_cl = grafico_classico(altura=360)
            st.plotly_chart(fig_cl, use_container_width=True)
            st.warning(txt_cl)

        with col_qt:
            st.plotly_chart(grafico_quantico(altura=360), use_container_width=True)
            exibir_explicacao_quantica()

        st.divider()
        col_m, col_b = st.columns([1, 2])
        with col_m:
            st.metric("Saída (+) [+ℏ/2]", f"{n_final_mais} átomos", f"{pct_mais:.1f}% (desvio {desvio_mais*100:+.1f}%)", delta_color="off")
            st.metric("Saída (-) [-ℏ/2]", f"{n_final_menos} átomos", f"{pct_menos:.1f}% (desvio {desvio_menos*100:+.1f}%)", delta_color="off")
            st.caption(f"N₀ = {n_atomos} | σ_f = ±{sigma_f*100:.2f}%")
        with col_b:
            st.plotly_chart(grafico_barras(), use_container_width=True)

    else:
        col_tela, col_info = st.columns([1.15, 1])

        with col_tela:
            st.plotly_chart(grafico_quantico(altura=390), use_container_width=True)

        with col_info:
            st.caption(
                f"Fluxo no {nome_final}: **N_entrada = {n_entrada_final}** de **N₀ = {n_atomos}** emitidos "
                f"| Incerteza estatística: **σ_f = ±{sigma_f*100:.2f}%**"
            )
            c1, c2 = st.columns(2)
            c1.metric(
                "Saída (+) [+ℏ/2]",
                f"{n_final_mais} átomos",
                f"{pct_mais:.1f}% (teor. {p_final_mais*100:.1f}% | {desvio_mais*100:+.1f}%)",
                delta_color="off",
            )
            c2.metric(
                "Saída (-) [-ℏ/2]",
                f"{n_final_menos} átomos",
                f"{pct_menos:.1f}% (teor. {p_final_menos*100:.1f}% | {desvio_menos*100:+.1f}%)",
                delta_color="off",
            )
            st.plotly_chart(grafico_barras(), use_container_width=True)
            exibir_explicacao_quantica()

    st.divider()
    renderizar_analise_teorica_configuracao()

# --- ABA 2: APARATO FÍSICO (GIF + DIAGRAMAS 3D) ---
with aba_aparato:
    pasta_app = Path(__file__).parent

    if modo == "1. Quantização (1 Filtro)":
        col_gif, col_txt = st.columns([1, 1.2])
        with col_gif:
            gifs = list(pasta_app.glob("*.gif"))
            if gifs:
                st.image(str(gifs[0]), caption="Montagem física: fonte térmica, ímã com gradiente de campo e anteparo.", use_container_width=True)
            else:
                st.error(f"Nenhum arquivo .gif encontrado em: {pasta_app}")
        with col_txt:
            st.subheader("Funcionamento do Aparato Físico")
            st.markdown("""
1. **Fonte de átomos:** um forno aquece átomos de prata, emitindo um feixe colimado não polarizado ($\\hat{\\rho} = \\hat{I}/2$).
2. **Campo magnético não uniforme (N–S):** o gradiente $\\partial B_n / \\partial n$ exerce uma força proporcional à componente do momento magnético de spin ao longo do eixo do analisador.
3. **Anteparo de detecção:** em contraste com a faixa contínua prevista pelo modelo clássico, o feixe se divide em apenas **duas regiões discretas**, correspondentes aos autovalores $+\\hbar/2$ e $-\\hbar/2$.
            """)

    elif modo == "2. Projeção (2 Filtros)":
        if st.session_state.theta1 == st.session_state.theta2:
            nome_img = "f2_alinhado.png"
            legenda = "Analisadores alinhados (B₁ ∥ B₂): o estado preparado em F1 é autoestado de F2 e não sofre nova divisão."
        elif abs(st.session_state.theta2 - 90) <= 15:
            nome_img = "f2_horizontal_x.png"
            legenda = "Segundo analisador orientado em x̂ (90°): o feixe divide-se simetricamente em dois canais horizontais."
        else:
            nome_img = "f2_inclinado_z.png"
            legenda = "Analisadores em orientação oblíqua: o estado preparado projeta-se nos dois autoestados do segundo analisador."

        caminho_img = pasta_app / nome_img
        _, col_centro, _ = st.columns([0.5, 3, 0.5])
        with col_centro:
            if caminho_img.exists():
                st.image(str(caminho_img), caption=legenda, use_container_width=True)
            else:
                st.warning(f"Imagem '{nome_img}' não encontrada em: {pasta_app}")

    else:
        candidatos_f3 = list(pasta_app.glob("f3_colapso.*"))
        _, col_centro, _ = st.columns([0.3, 3.4, 0.3])
        with col_centro:
            if candidatos_f3:
                st.image(
                    str(candidatos_f3[0]),
                    caption="Cascata z → x → z: após selecionar |+z⟩ em F1 e medir em x̂ em F2, a componente |-z⟩ reaparece em F3.",
                    use_container_width=True,
                )
            else:
                st.warning(f"Imagem 'f3_colapso.png' não encontrada em: {pasta_app}")

# --- ABA 3: FORMALISMO QUÂNTICO ---
with aba_alg:
    renderizar_formalismo_teorico()
    st.divider()

    if modo == "1. Quantização (1 Filtro)":
        t1 = st.session_state.theta1
        st.subheader("Cálculo para a Configuração Atual (1 Filtro)")
        st.write(
            f"Com $\\theta_1 = {t1}^\\circ$, a fonte não polarizada ($\\hat{{\\rho}} = \\hat{{I}}/2$) fornece "
            f"$P(+\\hat{{n}}_1) = \\operatorname{{Tr}}(\\hat{{\\rho}}\\hat{{P}}_+) = 0.500$ e "
            f"$P(-\\hat{{n}}_1) = \\operatorname{{Tr}}(\\hat{{\\rho}}\\hat{{P}}_-) = 0.500$. "
            "Na base de $\\hat{S}_z$, os autoestados do analisador são:"
        )
        m1_v, m2_v = auto_spin(t1)
        st.latex(
            rf"|+\hat{{n}}_1\rangle = \begin{{pmatrix}} {m1_v[0].real+0.0:.3f} \\ {m1_v[1].real+0.0:.3f} \end{{pmatrix}}, \qquad "
            rf"|-\hat{{n}}_1\rangle = \begin{{pmatrix}} {m2_v[0].real+0.0:.3f} \\ {m2_v[1].real+0.0:.3f} \end{{pmatrix}}"
        )
    else:
        col_dirac, col_curva = st.columns([1.1, 1])

        with col_dirac:
            st.subheader("Cálculo para a Configuração Atual")
            st.write(f"**1. Estado preparado pelo Filtro 1 ({st.session_state.feixe1}, {st.session_state.theta1}°) — $P(a) = {p_passou_f1:.3f}$:**")
            st.latex(
                rf"|\chi_1\rangle = \begin{{pmatrix}} {estado1[0].real + 0.0:.3f} \\ {estado1[1].real + 0.0:.3f} \end{{pmatrix}}"
            )

            if modo == "3. Colapso de Estado (3 Filtros)":
                st.write(f"**2. Projeção no Filtro 2 ({st.session_state.feixe2}, {st.session_state.theta2}°):**")
                st.latex(
                    rf"P(b|a) = |\langle {st.session_state.feixe2}\hat{{n}}_2 | \chi_1 \rangle|^2 = {p_passou_f2:.3f} "
                    rf"\quad \Longrightarrow \quad "
                    rf"|\chi_2\rangle = \begin{{pmatrix}} {estado2[0].real + 0.0:.3f} \\ {estado2[1].real + 0.0:.3f} \end{{pmatrix}}"
                )
                st.write(f"**3. Probabilidades condicionais no Filtro 3 ({st.session_state.theta3}°):**")
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
                st.write(f"**2. Probabilidades condicionais no Filtro 2 ({st.session_state.theta2}°):**")
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

            with st.expander("🔍 Produto interno passo a passo (representação matricial)"):
                st.latex(
                    rf"\langle +\hat{{n}} | \chi \rangle = "
                    rf"\begin{{pmatrix}} {a0:.3f} & {a1:.3f} \end{{pmatrix}}"
                    rf"\begin{{pmatrix}} {b0:.3f} \\ {b1:.3f} \end{{pmatrix}}"
                    rf"= ({a0:.3f})({b0:.3f}) + ({a1:.3f})({b1:.3f}) = {amp:.3f}"
                )
                st.latex(rf"P_+ = |{amp:.3f}|^2 = {amp**2:.3f}")

        with col_curva:
            st.subheader("Lei Quântica vs. Frequência Observada")
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
                    name="Simulação atual",
                    marker=dict(color="#f59e0b", size=14, symbol="star", line=dict(color="#fff", width=1.5))
                ))

            fig_c.update_layout(
                xaxis=dict(title="Ângulo relativo Δθ (°)", range=[-5, 185], gridcolor="#262a36"),
                yaxis=dict(title="Probabilidade condicional (+) [%]", range=[-5, 108], gridcolor="#262a36"),
                height=360,
                margin=dict(l=15, r=15, t=25, b=20),
                legend=dict(orientation="h", y=1.14, x=0.5, xanchor="center", font=dict(size=11)),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#12151e",
            )
            st.plotly_chart(fig_c, use_container_width=True)
            st.caption(
                "Diferentemente da polarização óptica clássica (Lei de Malus, $\\cos^2\\Delta\\theta$), "
                "para partículas de spin-1/2 o fator $1/2$ implica ortogonalidade apenas em $\\Delta\\theta = 180^\\circ$."
            )

# --- ABA 4: ROTEIRO DE INVESTIGAÇÃO ---
with aba_guia:
    st.subheader("Roteiro de Investigação Experimental")
    st.write(
        "Explore os cenários abaixo seguindo a sequência **previsão teórica → simulação → interpretação física** "
        "para verificar experimentalmente os postulados da Mecânica Quântica para sistemas de spin-1/2."
    )

    with st.container(border=True):
        st.markdown("### Experimento 1: Quantização Espacial do Spin")
        st.write(
            "Um feixe térmico não polarizado ($\\hat{\\rho} = \\hat{I}/2$) incide sobre um analisador orientado em $0^\\circ$ ($\\hat{z}$). "
            "Observe a diferença entre a distribuição contínua prevista pelo modelo clássico e os dois canais discretos registrados no anteparo."
        )
        st.button(
            "▶️ Carregar Experimento 1 na Bancada",
            on_click=carregar_cenario,
            args=("1. Quantização (1 Filtro)", 0, "+", 90, "+", 0, 1000)
        )
        with st.expander("Análise física"):
            st.write(
                "O operador $\\hat{S}_z$ possui apenas dois autovalores ($\\pm\\hbar/2$). Mesmo com spins inicialmente distribuídos "
                "isotropicamente, cada medição projeta o átomo em um dos dois autoestados, com $P(+) = P(-) = \\operatorname{Tr}(\\hat{\\rho}\\hat{P}_\\pm) = 1/2$."
            )

    with st.container(border=True):
        st.markdown("### Experimento 2: Analisadores Perpendiculares (90°)")
        st.write(
            "O Filtro 1 ($0^\\circ$) prepara o estado puro $|+z\\rangle$, que incide sobre um segundo analisador orientado em $90^\\circ$ ($\\hat{x}$). "
            "Verifique por que a transmissão não se anula a $90^\\circ$, ao contrário de polarizadores ópticos cruzados."
        )
        st.button(
            "▶️ Carregar Experimento 2 na Bancada",
            on_click=carregar_cenario,
            args=("2. Projeção (2 Filtros)", 0, "+", 90, "+", 0, 1000)
        )
        with st.expander("Análise física"):
            st.write(
                "Na base de $\\hat{S}_x$, o estado $|+z\\rangle = \\frac{1}{\\sqrt{2}}(|+x\\rangle + |-x\\rangle)$ é uma superposição simétrica. "
                "Logo, $P(+x|+z) = P(-x|+z) = \\cos^2(90^\\circ/2) = 1/2$. Em spin-1/2, estados ortogonais correspondem a eixos antiparalelos ($180^\\circ$)."
            )

    with st.container(border=True):
        st.markdown("### Experimento 3: Medição Intermediária e Reaparição de Estado (z → x → z)")
        st.write(
            "O Filtro 1 ($0^\\circ$) seleciona apenas $|+z\\rangle$, bloqueando integralmente $|-z\\rangle$. "
            "Compare o resultado no Filtro 3 ($0^\\circ$) quando o Filtro 2 intermediário está em $90^\\circ$ versus alinhado em $0^\\circ$."
        )
        c_d3a, c_d3b = st.columns(2)
        c_d3a.button(
            "▶️ Carregar cascata z → x → z (F2 em 90°)",
            on_click=carregar_cenario,
            args=("3. Colapso de Estado (3 Filtros)", 0, "+", 90, "+", 0, 1000),
            use_container_width=True
        )
        c_d3b.button(
            "▶️ Carregar controle z → z → z (F2 em 0°)",
            on_click=carregar_cenario,
            args=("3. Colapso de Estado (3 Filtros)", 0, "+", 0, "+", 0, 1000),
            use_container_width=True
        )
        with st.expander("Análise física"):
            st.write(
                "Como $[\\hat{S}_z, \\hat{S}_x] \\neq 0$, selecionar $|+x\\rangle$ em F2 projeta o estado em "
                "$|+x\\rangle = \\frac{1}{\\sqrt{2}}(|+z\\rangle + |-z\\rangle)$, destruindo a preparação anterior em $z$ e fazendo "
                "$|-z\\rangle$ reaparecer em F3 com probabilidade condicional $P(-z|+x) = 1/2$ (e probabilidade total $P_{\\text{total}} = 1/8$ desde a fonte)."
            )

st.divider()
st.markdown(
    """
    <div style="text-align: center; font-size: 0.85rem; color: #94a3b8;">
        Desenvolvido por <strong style="color: #e2e8f0;">Wesley Sales de Souza</strong> •
        Licenciatura em Física • DEFIS – IFMA •
        Grupo de Magnetismo e Física Computacional (GMFC)
    </div>
    """,
    unsafe_allow_html=True,
)