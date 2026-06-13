"""Memory helper logic moved out of the backend agent."""

from __future__ import annotations

from app.core.models import WinnerGene
from app.core.state_store import GeneStore


def remember_gene(store: GeneStore, gene: WinnerGene) -> WinnerGene:
    store.add(gene)
    return gene


def list_winner_genes(store: GeneStore) -> list[WinnerGene]:
    return store.list()


def promote_gene(store: GeneStore, symbol: str, timeframe: str) -> WinnerGene | None:
    return store.promote(symbol, timeframe)
