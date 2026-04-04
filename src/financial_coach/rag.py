from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

from financial_coach.auth import OzeroFgaClient


@dataclass
class RetrievalBundle:
    tables: Dict[str, pd.DataFrame]
    summaries: Dict[str, List[str]]


class TabularRagAgent:
    def __init__(self, fga_client: OzeroFgaClient):
        self.fga_client = fga_client

    def retrieve(self, user_id: str, query: str, tables: Dict[str, pd.DataFrame]) -> RetrievalBundle:
        authorized: Dict[str, pd.DataFrame] = {}
        summaries: Dict[str, List[str]] = {}
        query_lower = query.lower()

        for table_name, frame in tables.items():
            authorized_table = self.fga_client.authorize_table(user_id, table_name, frame, "read")
            authorized_rows = self.fga_client.authorize_rows(user_id, table_name, authorized_table, "read")
            filtered, summary = self._filter_rows(query_lower, table_name, authorized_rows)
            authorized[table_name] = filtered
            summaries[table_name] = summary

        return RetrievalBundle(tables=authorized, summaries=summaries)

    def _filter_rows(
        self, query_lower: str, table_name: str, frame: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[str]]:
        if frame.empty:
            return frame, ["No authorized rows available."]

        filtered = frame
        if table_name == "expenses":
            if "budget" in query_lower or "spend" in query_lower:
                filtered = frame.sort_values("amount", ascending=False).head(12)
        elif table_name == "debts":
            if "debt" in query_lower or "payoff" in query_lower:
                filtered = frame.sort_values("apr", ascending=False)
        elif table_name == "income":
            filtered = frame.sort_values("net_monthly", ascending=False)
        elif table_name == "assets":
            if "emergency" in query_lower or "savings" in query_lower:
                filtered = frame.sort_values("balance", ascending=False)

        summary = [
            f"authorized_rows={len(filtered)}",
            f"columns={', '.join(filtered.columns[:6])}",
        ]
        return filtered, summary

    @staticmethod
    def inject_context(bundle: RetrievalBundle) -> Dict[str, List[dict]]:
        injected: Dict[str, List[dict]] = {}
        for table_name, frame in bundle.tables.items():
            injected[table_name] = frame.to_dict(orient="records")
        return injected
