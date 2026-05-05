# 🇧🇷 Painel Econômico BR

![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Gráficos-3F4F75?style=flat&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Análise-150458?style=flat&logo=pandas&logoColor=white)
![Banco Central](https://img.shields.io/badge/Fonte-Banco%20Central%20do%20Brasil-009c3b?style=flat)

Dashboard interativo para monitoramento dos principais indicadores macroeconômicos do Brasil, com coleta automática de dados via API do Banco Central, análise exploratória e visualizações dinâmicas.

---

##  O que o projeto faz

O **Painel Econômico BR** coleta, processa e visualiza 3 indicadores essenciais da economia brasileira:

| Indicador | O que representa | Fonte (SGS) |
|-----------|-----------------|-------------|
| **Selic** | Taxa básica de juros (% a.a.) | Série 432 |
| **IPCA** | Inflação oficial mensal (%) | Série 433 |
| **Câmbio USD/BRL** | Cotação do dólar americano | Série 1 |

---

##  Funcionalidades

- **KPIs em tempo real** com último valor e variação vs. mês anterior
- **Gráficos de linha interativos** com série histórica de até 15 anos
- **Variação mensal** em barras dos últimos 24 meses
- **Matriz de correlação** entre os indicadores (Pearson)
- **Estatísticas descritivas** completas (média, desvio padrão, min/max, coeficiente de variação)
- **Extremos históricos** com data e valor
- **Scatter matrix** para análise de dispersão cruzada
- **Sidebar configurável**: período, indicadores visíveis, botão de atualização

---

##  Tecnologias

| Biblioteca | Uso |
|------------|-----|
| `requests` | Coleta de dados via API REST (BCB/SGS) |
| `pandas` | Manipulação e análise de dados |
| `numpy` | Operações numéricas |
| `plotly` | Gráficos interativos |
| `streamlit` | Interface web do dashboard |

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
├── data/                 # CSVs gerados automaticamente
│
├── notebooks/
│   └── analise_exploratoria.ipynb
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

##  Como Rodar

### 1. Clone o repositório
```bash
git clone https://github.com/NathanPintoNascimento/painel-economico-br.git
cd painel-economico-br
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv .venv

# Mac/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate.bat
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Colete os dados do Banco Central
```bash
python src/coletor.py
```

### 5. Suba o dashboard
```bash
python -m streamlit run src/dashboard.py
```

Acesse em **http://localhost:8501** 

---

##  API do Banco Central

Os dados são coletados do **SGS (Sistema Gerenciador de Séries Temporais)** do Banco Central do Brasil.

```
https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json
```

O dashboard faz **cache local em CSV** para evitar chamadas desnecessárias. Use o botão **"Atualizar Dados"** na sidebar para forçar nova coleta.

---

##  Análises Implementadas

```python
estatisticas_descritivas(df)   # média, mediana, desvio padrão, quartis
calcular_variacoes(df)         # variação mensal e acumulada 12 meses  
matriz_correlacao(df)          # correlação de Pearson entre indicadores
extremos_historicos(df)        # máximos e mínimos com data
resumo_recente(df, meses=12)   # estatísticas dos últimos 12 meses
```

---

##  Boas Práticas Adotadas

-  Separação de responsabilidades em módulos (`coletor`, `analise`, `dashboard`)
-  Docstrings em todas as funções
-  Logging estruturado com níveis INFO/ERROR
-  Cache com `@st.cache_data` para evitar reprocessamento
-  Tratamento de erros nas chamadas de rede
-  `requirements.txt` com dependências declaradas
-  `.gitignore` configurado

---

##  Autor

Feito por **Nathan Nascimento** — conecte-se no [LinkedIn](www.linkedin.com/in/
nathan-nascimento-)

---

##  Licença

MIT License — sinta-se livre para usar, modificar e distribuir.
