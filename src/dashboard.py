"""
dashboard.py
------------
Dashboard interativo do Painel Econômico BR.

Tecnologias:
    - Streamlit: interface web
    - Plotly: gráficos interativos
    - Pandas: manipulação de dados

Como rodar:
    streamlit run src/dashboard.py
"""

import sys
from pathlib import Path

# Garante importação dos módulos locais
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from coletor import coletar_todos_indicadores, salvar_csvs, carregar_csvs, DATA_DIR
from analise import executar_analise_completa

# ─────────────────────────────────────────
#  Configuração da Página
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Painel Econômico BR",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
#  CSS Customizado
# ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #003087 0%, #009c3b 50%, #ffdf00 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { color: white; font-size: 2.2rem; font-weight: 700; margin: 0; }
    .main-header p  { color: rgba(255,255,255,0.9); margin: 0.4rem 0 0; font-size: 1rem; }

    .kpi-card {
        background: #1e1e2e;
        border: 1px solid #2d2d42;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .kpi-label { color: #8b8fa8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { color: #f8f8f2; font-size: 2rem; font-weight: 700; }
    .kpi-delta-pos { color: #50fa7b; font-size: 0.9rem; }
    .kpi-delta-neg { color: #ff5555; font-size: 0.9rem; }

    .section-title { font-size: 1.1rem; font-weight: 600; color: #cdd6f4; margin: 1.5rem 0 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  Paleta de Cores
# ─────────────────────────────────────────
CORES = {
    "selic":      "#ff79c6",
    "ipca":       "#ffb86c",
    "cambio_usd": "#8be9fd",
}

NOMES = {
    "selic":      "Selic (% a.a.)",
    "ipca":       "IPCA (% mês)",
    "cambio_usd": "Câmbio USD/BRL",
}


# ─────────────────────────────────────────
#  Cache de dados
# ─────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Carregando dados do Banco Central...")
def carregar_dados(anos: int) -> tuple[dict, dict]:
    """Carrega dados do cache local ou busca na API."""
    csvs_existem = all((DATA_DIR / f"{ind}.csv").exists() for ind in ["selic", "ipca", "cambio_usd"])

    if csvs_existem:
        dados = carregar_csvs()
    else:
        dados = coletar_todos_indicadores(anos=anos)
        salvar_csvs(dados)

    analise = executar_analise_completa(dados)
    return dados, analise


# ─────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configurações")

    anos = st.slider("Período (anos)", min_value=1, max_value=15, value=10, step=1)

    if st.button("🔄 Atualizar Dados da API", use_container_width=True):
        st.cache_data.clear()
        # Remove CSVs para forçar novo download
        for ind in ["selic", "ipca", "cambio_usd"]:
            f = DATA_DIR / f"{ind}.csv"
            if f.exists():
                f.unlink()
        st.rerun()

    st.divider()
    st.markdown("### 📊 Indicadores")
    mostrar_selic = st.checkbox("Selic", value=True)
    mostrar_ipca  = st.checkbox("IPCA",  value=True)
    mostrar_cambio = st.checkbox("Câmbio USD/BRL", value=True)

    st.divider()
    st.markdown("""
    **Fontes de dados**
    - [BCB / SGS](https://www.bcb.gov.br/estatisticas/tabelaespecial)
    - Selic: série 432
    - IPCA: série 433
    - Câmbio: série 1
    """)


# ─────────────────────────────────────────
#  Header
# ─────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🇧🇷 Painel Econômico BR</h1>
    <p>Indicadores macroeconômicos do Brasil • Fonte: Banco Central do Brasil (SGS)</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  Carregamento
# ─────────────────────────────────────────
dados, analise = carregar_dados(anos)
df = analise["df_combinado"]
stats = analise["estatisticas"]
extremos = analise["extremos"]
corr = analise["correlacao"]

indicadores_ativos = []
if mostrar_selic:  indicadores_ativos.append("selic")
if mostrar_ipca:   indicadores_ativos.append("ipca")
if mostrar_cambio: indicadores_ativos.append("cambio_usd")

if not indicadores_ativos:
    st.warning("Selecione ao menos um indicador na barra lateral.")
    st.stop()


# ─────────────────────────────────────────
#  KPIs — Últimos valores
# ─────────────────────────────────────────
st.markdown('<p class="section-title">📌 Último valor disponível</p>', unsafe_allow_html=True)

kpi_cols = st.columns(len(indicadores_ativos))
for col, ind in zip(kpi_cols, indicadores_ativos):
    serie = df[ind].dropna()
    ultimo = serie.iloc[-1]
    penultimo = serie.iloc[-2] if len(serie) > 1 else ultimo
    delta = ultimo - penultimo

    delta_html = f'<p class="kpi-delta-{"pos" if delta >= 0 else "neg"}">{"▲" if delta >= 0 else "▼"} {abs(delta):.4f}</p>'
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-label">{NOMES[ind]}</p>
            <p class="kpi-value">{ultimo:.4f}</p>
            {delta_html}
            <p style="color:#6c7086;font-size:0.72rem;">{serie.index[-1].strftime('%b/%Y')}</p>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────
#  Gráfico de Linhas — Séries Históricas
# ─────────────────────────────────────────
st.markdown('<p class="section-title">📈 Evolução Histórica</p>', unsafe_allow_html=True)

abas = st.tabs([NOMES[i] for i in indicadores_ativos] + ["📊 Todos (subplots)"])

for aba, ind in zip(abas[:-1], indicadores_ativos):
    with aba:
        serie = df[[ind]].dropna().reset_index()
        fig = px.line(
            serie, x="data", y=ind,
            title=f"{NOMES[ind]} — Série Histórica ({anos} anos)",
            labels={"data": "Data", ind: NOMES[ind]},
            color_discrete_sequence=[CORES[ind]],
            template="plotly_dark",
        )
        fig.update_traces(line_width=1.8)
        fig.update_layout(
            plot_bgcolor="#1e1e2e",
            paper_bgcolor="#1e1e2e",
            font_color="#cdd6f4",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=30),
        )
        # Linha da média
        media = serie[ind].mean()
        fig.add_hline(y=media, line_dash="dot", line_color="#6c7086",
                      annotation_text=f"Média: {media:.2f}",
                      annotation_position="bottom right")
        st.plotly_chart(fig, use_container_width=True)

# Aba Todos (subplots)
with abas[-1]:
    fig = make_subplots(
        rows=len(indicadores_ativos), cols=1,
        shared_xaxes=True,
        subplot_titles=[NOMES[i] for i in indicadores_ativos],
        vertical_spacing=0.08,
    )
    for idx, ind in enumerate(indicadores_ativos, start=1):
        serie = df[[ind]].dropna().reset_index()
        fig.add_trace(
            go.Scatter(
                x=serie["data"], y=serie[ind],
                mode="lines", name=NOMES[ind],
                line=dict(color=CORES[ind], width=1.8),
            ),
            row=idx, col=1,
        )
    fig.update_layout(
        height=300 * len(indicadores_ativos),
        template="plotly_dark",
        plot_bgcolor="#1e1e2e",
        paper_bgcolor="#1e1e2e",
        font_color="#cdd6f4",
        showlegend=False,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────
#  Variação Mensal (Barras)
# ─────────────────────────────────────────
st.markdown('<p class="section-title">📉 Variação Mensal (%)</p>', unsafe_allow_html=True)

var = analise["variacoes"]["variacao_mensal"][indicadores_ativos].dropna().tail(24).reset_index()
var_melt = var.melt(id_vars="data", var_name="Indicador", value_name="Variação (%)")
var_melt["Indicador"] = var_melt["Indicador"].map(NOMES)

fig_bar = px.bar(
    var_melt, x="data", y="Variação (%)", color="Indicador",
    barmode="group",
    title="Variação Mensal — últimos 24 meses",
    template="plotly_dark",
    color_discrete_map={NOMES[k]: v for k, v in CORES.items()},
)
fig_bar.update_layout(
    plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
    font_color="#cdd6f4", margin=dict(l=20, r=20, t=50, b=30),
)
st.plotly_chart(fig_bar, use_container_width=True)


# ─────────────────────────────────────────
#  Correlação + Estatísticas
# ─────────────────────────────────────────
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<p class="section-title">🔗 Correlação entre Indicadores</p>', unsafe_allow_html=True)
    corr_filtrada = corr.loc[indicadores_ativos, indicadores_ativos]
    labels = [NOMES[i] for i in indicadores_ativos]

    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_filtrada.values,
        x=labels, y=labels,
        colorscale="RdBu",
        zmin=-1, zmax=1,
        text=corr_filtrada.values.round(2),
        texttemplate="%{text}",
        showscale=True,
    ))
    fig_corr.update_layout(
        template="plotly_dark",
        plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
        font_color="#cdd6f4",
        margin=dict(l=20, r=20, t=20, b=20),
        height=350,
    )
    st.plotly_chart(fig_corr, use_container_width=True)

with col_right:
    st.markdown('<p class="section-title">📋 Estatísticas Descritivas</p>', unsafe_allow_html=True)
    stats_filtrada = stats.loc[indicadores_ativos, ["média", "desvio_padrão", "mínimo", "máximo", "coef_variacao"]]
    stats_filtrada.index = [NOMES[i] for i in indicadores_ativos]
    st.dataframe(stats_filtrada.style.format("{:.4f}"), use_container_width=True)

    st.markdown('<p class="section-title">🏆 Extremos Históricos</p>', unsafe_allow_html=True)
    extremos_filtrados = extremos.loc[indicadores_ativos]
    extremos_filtrados.index = [NOMES[i] for i in indicadores_ativos]
    st.dataframe(extremos_filtrados, use_container_width=True)


# ─────────────────────────────────────────
#  Scatter Matrix
# ─────────────────────────────────────────
if len(indicadores_ativos) >= 2:
    st.markdown('<p class="section-title">🔍 Dispersão entre Indicadores</p>', unsafe_allow_html=True)
    df_scatter = df[indicadores_ativos].dropna().rename(columns=NOMES)
    fig_scatter = px.scatter_matrix(
        df_scatter,
        dimensions=list(df_scatter.columns),
        template="plotly_dark",
        color_discrete_sequence=["#bd93f9"],
        opacity=0.5,
    )
    fig_scatter.update_traces(marker=dict(size=3))
    fig_scatter.update_layout(
        plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
        font_color="#cdd6f4",
        height=500,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ─────────────────────────────────────────
#  Rodapé
# ─────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center;color:#6c7086;font-size:0.8rem;'>"
    "Painel Econômico BR • Dados: Banco Central do Brasil (SGS) • "
    "Construído com Python, Streamlit e Plotly"
    "</p>",
    unsafe_allow_html=True,
)