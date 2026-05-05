"""
analise.py
----------
Módulo de análise exploratória dos indicadores econômicos coletados.

Realiza:
    - Estatísticas descritivas (média, mediana, desvio padrão, min/max)
    - Variações mensais e anuais
    - Matriz de correlação entre os indicadores
    - Identificação de máximos e mínimos históricos
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def combinar_indicadores(dados: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Combina todos os indicadores em um único DataFrame alinhado pela data.

    Args:
        dados: Dicionário {nome: DataFrame com colunas 'data' e nome}.

    Returns:
        DataFrame combinado com 'data' como índice.
    """
    dfs = []
    for nome, df in dados.items():
        df_col = df.set_index("data")[[nome]]
        dfs.append(df_col)

    combinado = pd.concat(dfs, axis=1, join="outer")
    combinado = combinado.sort_index()
    logger.info(f"DataFrame combinado: {combinado.shape[0]} datas × {combinado.shape[1]} indicadores")
    return combinado


def estatisticas_descritivas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula estatísticas descritivas para cada indicador.

    Args:
        df: DataFrame combinado com índice datetime.

    Returns:
        DataFrame de estatísticas.
    """
    stats = df.describe().T
    stats["mediana"] = df.median()
    stats["coef_variacao"] = (df.std() / df.mean() * 100).round(2)

    # Renomear colunas para português
    stats = stats.rename(columns={
        "count": "contagem",
        "mean": "média",
        "std": "desvio_padrão",
        "min": "mínimo",
        "max": "máximo",
        "25%": "q1",
        "50%": "q2",
        "75%": "q3",
    })

    return stats.round(4)


def calcular_variacoes(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Calcula variações mensais e acumuladas nos últimos 12 meses.

    Args:
        df: DataFrame combinado.

    Returns:
        Dicionário com DataFrames de variação mensal e anual.
    """
    variacao_mensal = df.pct_change() * 100
    variacao_12m = df.pct_change(periods=12) * 100

    return {
        "variacao_mensal": variacao_mensal.round(4),
        "variacao_12m": variacao_12m.round(4),
    }


def matriz_correlacao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a matriz de correlação de Pearson entre os indicadores.

    Args:
        df: DataFrame combinado.

    Returns:
        Matriz de correlação (DataFrame).
    """
    corr = df.corr(method="pearson").round(4)
    logger.info("Matriz de correlação calculada.")
    return corr


def extremos_historicos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica as datas e valores de máximos e mínimos históricos.

    Args:
        df: DataFrame combinado.

    Returns:
        DataFrame com máximos e mínimos para cada indicador.
    """
    registros = []
    for col in df.columns:
        serie = df[col].dropna()
        registros.append({
            "indicador": col,
            "valor_máximo": serie.max(),
            "data_máximo": serie.idxmax().strftime("%Y-%m"),
            "valor_mínimo": serie.min(),
            "data_mínimo": serie.idxmin().strftime("%Y-%m"),
        })

    return pd.DataFrame(registros).set_index("indicador")


def resumo_recente(df: pd.DataFrame, meses: int = 12) -> pd.DataFrame:
    """
    Retorna estatísticas dos últimos N meses.

    Args:
        df: DataFrame combinado.
        meses: Quantidade de meses recentes a analisar.

    Returns:
        DataFrame com estatísticas do período recente.
    """
    cutoff = df.index.max() - pd.DateOffset(months=meses)
    recente = df[df.index >= cutoff]
    stats = recente.describe().T[["mean", "std", "min", "max"]].round(4)
    stats.columns = ["média_recente", "desvio_recente", "mínimo_recente", "máximo_recente"]
    return stats


def executar_analise_completa(dados: dict[str, pd.DataFrame]) -> dict:
    """
    Executa o pipeline completo de análise exploratória.

    Args:
        dados: Dicionário carregado pelo coletor.

    Returns:
        Dicionário com todos os resultados de análise.
    """
    logger.info("=== Iniciando análise exploratória ===")

    df = combinar_indicadores(dados)

    resultados = {
        "df_combinado": df,
        "estatisticas": estatisticas_descritivas(df),
        "variacoes": calcular_variacoes(df),
        "correlacao": matriz_correlacao(df),
        "extremos": extremos_historicos(df),
        "resumo_recente": resumo_recente(df, meses=12),
    }

    # Log de destaques
    logger.info("\n--- Estatísticas Descritivas ---")
    logger.info(f"\n{resultados['estatisticas'].to_string()}")

    logger.info("\n--- Matriz de Correlação ---")
    logger.info(f"\n{resultados['correlacao'].to_string()}")

    logger.info("\n--- Extremos Históricos ---")
    logger.info(f"\n{resultados['extremos'].to_string()}")

    logger.info("=== Análise concluída! ===")
    return resultados


if __name__ == "__main__":
    from coletor import carregar_csvs
    dados = carregar_csvs()
    resultados = executar_analise_completa(dados)