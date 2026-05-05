# 🇧🇷 Painel Econômico BR

Dashboard interativo de indicadores macroeconômicos do Brasil, com coleta automática de dados via API do Banco Central, análise exploratória com Pandas e visualizações com Plotly + Streamlit.

---

##  Indicadores Monitorados

| Indicador | Descrição | Fonte (SGS) |
|-----------|-----------|-------------|
| **Selic** | Taxa básica de juros (% a.a.) | Série 432 |
| **IPCA** | Inflação oficial mensal (%) | Série 433 |
| **Câmbio USD/BRL** | Cotação do dólar (venda, média mensal) | Série 1 |

---

##  Preview do Dashboard

![Dashboard Preview](data/dashboard_preview.png)

> *Dashboard com séries históricas, variação mensal, matriz de correlação e KPIs em tempo real.*

---

##  Como Rodar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/painel-economico-br.git
cd painel-economico-br
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# ou
.venv\Scripts\activate           # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Colete os dados da API do BCB
```bash
python src/coletor.py
```
> Os CSVs serão salvos automaticamente em `data/`.

### 5. (Opcional) Execute o notebook de análise exploratória
```bash
jupyter notebook notebooks/analise_exploratoria.ipynb
```

### 6. Suba o dashboard Streamlit
```bash
streamlit run src/dashboard.py
```
Acesse em: **http://localhost:8501**

---

##  Estrutura do Projeto

```
painel-economico-br/
│
├── src/
│   ├── coletor.py        # Coleta de dados via API SGS/BCB
│   ├── analise.py        # Análise exploratória com Pandas
│   └── dashboard.py      # Dashboard interativo Streamlit + Plotly
│
├── data/
│   ├── selic.csv         # Taxa Selic histórica (gerado automaticamente)
│   ├── ipca.csv          # IPCA histórico (gerado automaticamente)
│   └── cambio_usd.csv    # Câmbio USD/BRL histórico (gerado automaticamente)
│
├── notebooks/
│   └── analise_exploratoria.ipynb   # EDA completa com Matplotlib/Seaborn
│
├── requirements.txt      # Dependências Python
├── .gitignore
└── README.md
```

---

##  Tecnologias

| Biblioteca | Versão | Uso |
|------------|--------|-----|
| `requests` | 2.31.0 | Coleta via API REST (BCB/SGS) |
| `pandas` | 2.2.0 | Manipulação e análise de dados |
| `numpy` | 1.26.4 | Operações numéricas |
| `matplotlib` | 3.8.3 | Gráficos estáticos no notebook |
| `seaborn` | 0.13.2 | Heatmap de correlação |
| `plotly` | 5.20.0 | Gráficos interativos no dashboard |
| `streamlit` | 1.32.0 | Interface web do dashboard |
| `jupyter` | 1.0.0 | Notebook de análise exploratória |

---

##  Funcionalidades do Dashboard

- **KPIs** com último valor disponível e variação vs. mês anterior
- **Gráficos de linha** interativos com linha de média e hover unificado
- **Subplots** com todos os indicadores no mesmo eixo temporal
- **Gráfico de barras** de variação mensal (últimos 24 meses)
- **Heatmap de correlação** de Pearson entre os indicadores
- **Tabela de estatísticas descritivas** (média, desvio, min/max, coeficiente de variação)
- **Extremos históricos** com data e valor
- **Scatter matrix** para análise de dispersão cruzada
- **Sidebar configurável**: período, indicadores visíveis, botão de atualização

---

##  Análises Implementadas

```python
# Estatísticas descritivas
estatisticas_descritivas(df)    # média, mediana, desvio, Q1/Q3, coef. variação

# Variações
calcular_variacoes(df)          # variação mensal e acumulada 12 meses

# Correlação
matriz_correlacao(df)           # matriz de Pearson entre indicadores

# Extremos
extremos_historicos(df)         # máximos e mínimos históricos com data

# Resumo recente
resumo_recente(df, meses=12)    # estatísticas dos últimos 12 meses
```

---

##  API do Banco Central

Os dados são coletados do **SGS (Sistema Gerenciador de Séries Temporais)** do Banco Central do Brasil.

Endpoint base:
```
https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json
```

Parâmetros aceitos: `dataInicial`, `dataFinal` no formato `DD/MM/AAAA`.

> O dashboard faz cache local dos CSVs em `data/` para evitar chamadas desnecessárias. Use o botão **"Atualizar Dados da API"** na sidebar para forçar nova coleta.

---

##  Boas Práticas Adotadas

- ✅ Separação de responsabilidades em módulos (`coletor`, `analise`, `dashboard`)
- ✅ Docstrings em todas as funções públicas
- ✅ Logging estruturado com níveis INFO/ERROR
- ✅ Cache com `@st.cache_data` para evitar reprocessamento
- ✅ Tratamento de erros nas chamadas de rede
- ✅ `requirements.txt` com versões fixadas
- ✅ `.gitignore` configurado

---

##  Licença

MIT License — sinta-se livre para usar, modificar e distribuir.