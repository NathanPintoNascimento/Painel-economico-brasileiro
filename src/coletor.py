"""
coletor.py
----------
Módulo responsável por coletar dados econômicos da API do Banco Central do Brasil (SGS).

Indicadores coletados:
    - Selic: taxa de juros básica da economia (código 432)
    - IPCA: índice de inflação oficial (código 433)
    - Câmbio USD/BRL: cotação do dólar (código 1)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Configurações da API SGS (Sistema Gerenciador de Séries Temporais)
BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
DATA_DIR = Path(__file__).parent.parent / "data"

# Mapeamento dos indicadores: nome → código SGS
INDICADORES = {
    "selic": 432,       # Taxa Selic acumulada no mês (% a.a.)
    "ipca": 433,        # IPCA - variação mensal (%)
    "cambio_usd": 1,    # Taxa de câmbio USD/BRL - venda (média mensal)
}


def buscar_serie(codigo: int, data_inicio: str, data_fim: str) -> pd.DataFrame:
    """
    Busca uma série temporal no SGS/BCB.

    Args:
        codigo: Código da série no SGS.
        data_inicio: Data de início no formato DD/MM/AAAA.
        data_fim: Data de fim no formato DD/MM/AAAA.

    Returns:
        DataFrame com colunas 'data' (datetime) e 'valor' (float).
    """
    url = BASE_URL.format(codigo=codigo)
    params = {
        "formato": "json",
        "dataInicial": data_inicio,
        "dataFinal": data_fim,
    }

    try:
        logger.info(f"Buscando série {codigo} de {data_inicio} até {data_fim}...")
        resposta = requests.get(url, params=params, timeout=30)
        resposta.raise_for_status()

        dados = resposta.json()
        df = pd.DataFrame(dados)
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        df = df.dropna(subset=["valor"]).reset_index(drop=True)

        logger.info(f"  → {len(df)} registros coletados.")
        return df

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar série {codigo}: {e}")
        raise


def coletar_todos_indicadores(anos: int = 10) -> dict[str, pd.DataFrame]:
    """
    Coleta todos os indicadores definidos em INDICADORES para os últimos N anos.

    Args:
        anos: Quantidade de anos retroativos a coletar (padrão: 10).

    Returns:
        Dicionário {nome_indicador: DataFrame}.
    """
    data_fim = datetime.today()
    data_inicio = data_fim - timedelta(days=365 * anos)

    fmt = "%d/%m/%Y"
    inicio_str = data_inicio.strftime(fmt)
    fim_str = data_fim.strftime(fmt)

    resultados = {}
    for nome, codigo in INDICADORES.items():
        df = buscar_serie(codigo, inicio_str, fim_str)
        df = df.rename(columns={"valor": nome})
        resultados[nome] = df
        time.sleep(0.5)  # Respeita rate limit da API

    return resultados


def salvar_csvs(dados: dict[str, pd.DataFrame]) -> None:
    """
    Salva cada indicador como CSV na pasta data/.

    Args:
        dados: Dicionário retornado por coletar_todos_indicadores().
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for nome, df in dados.items():
        caminho = DATA_DIR / f"{nome}.csv"
        df.to_csv(caminho, index=False, encoding="utf-8-sig")
        logger.info(f"Salvo: {caminho}")


def carregar_csvs() -> dict[str, pd.DataFrame]:
    """
    Carrega os CSVs salvos da pasta data/.

    Returns:
        Dicionário {nome_indicador: DataFrame}.
    """
    dados = {}
    for nome in INDICADORES:
        caminho = DATA_DIR / f"{nome}.csv"
        if caminho.exists():
            df = pd.read_csv(caminho, parse_dates=["data"])
            dados[nome] = df
            logger.info(f"Carregado: {caminho} ({len(df)} registros)")
        else:
            logger.warning(f"Arquivo não encontrado: {caminho}")
    return dados


if __name__ == "__main__":
    logger.info("=== Iniciando coleta de dados do BCB ===")
    dados = coletar_todos_indicadores(anos=10)
    salvar_csvs(dados)
    logger.info("=== Coleta concluída com sucesso! ===")