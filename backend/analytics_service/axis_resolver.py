from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd


class TANAWAxisResolver:
    """
    Phase 2: Axis Resolver & Visualization Selector (non-blocking)
    - Rule-based preferred axes per analytic
    - Uses dataset columns to pick first available candidate
    - Provides fallbacks and a reason trail
    - Ready for optional AI confirmation later (not invoked here)
    """

    ANALYTIC_AXIS_RULES: Dict[str, Dict[str, List[str]]] = {
        "sales_summary": {
            "x_priority": ["Sale_Date", "Date", "Order_Date", "Invoice_Date"],
            "y_priority": ["Sales_Amount", "Sales", "Revenue", "Amount"],
            "chart": "line",
        },
        "product_performance": {
            "x_priority": ["Product", "Product_Name", "Product_Category", "Product_ID", "Item"],
            "y_priority": ["Sales_Amount", "Sales", "Revenue", "Amount"],
            "chart": "bar",
        },
        "regional_sales": {
            "x_priority": ["Region", "Area", "Branch", "Location"],
            "y_priority": ["Sales_Amount", "Sales", "Revenue", "Amount"],
            "chart": "bar",
        },
        "product_demand_forecast": {
            "x_priority": ["Sale_Date", "Date"],
            "y_priority": ["Quantity_Sold", "Quantity", "Units_Sold", "Demand"],
            "group_priority": ["Product", "Product_Name", "Product_Category"],
            "chart": "multi_line",
        },
    }

    def __init__(self) -> None:
        pass

    def suggest_axes(self, df: pd.DataFrame, analytic_key: str) -> Dict[str, Any]:
        rules = self.ANALYTIC_AXIS_RULES.get(analytic_key)
        if not rules:
            return {
                "analytic": analytic_key,
                "x": None,
                "y": None,
                "group": None,
                "chart": None,
                "reason": f"No rules for analytic '{analytic_key}'"
            }

        cols_lower = {c.lower(): c for c in df.columns}

        def pick_first(candidates: List[str]) -> Optional[str]:
            for cand in candidates:
                c = cols_lower.get(cand.lower())
                if c is not None:
                    return c
            return None

        x_col = pick_first(rules.get("x_priority", []))
        y_col = pick_first(rules.get("y_priority", []))
        g_col = pick_first(rules.get("group_priority", []))

        reason: List[str] = []
        if not x_col:
            reason.append("No preferred X found; will fallback to first datetime-like or index")
        if not y_col:
            reason.append("No preferred Y found; will fallback to first numeric column")

        # Soft fallbacks: try to infer by dtype
        if x_col is None:
            # datetime-like fallback
            for c in df.columns:
                if self._looks_datetime(df[c]):
                    x_col = c
                    reason.append(f"Fallback X selected by datetime heuristic: {c}")
                    break
            if x_col is None:
                x_col = df.columns[0]
                reason.append(f"Fallback X selected as first column: {x_col}")

        if y_col is None:
            # numeric fallback
            for c in df.columns:
                if self._looks_numeric(df[c]):
                    y_col = c
                    reason.append(f"Fallback Y selected by numeric heuristic: {c}")
                    break
            if y_col is None:
                y_col = df.columns[-1]
                reason.append(f"Fallback Y selected as last column: {y_col}")

        return {
            "analytic": analytic_key,
            "x": x_col,
            "y": y_col,
            "group": g_col,
            "chart": rules.get("chart"),
            "reason": "; ".join(reason) if reason else "Matched preferred rules",
        }

    # ---------------- helpers ----------------
    def _looks_datetime(self, s: pd.Series) -> bool:
        try:
            pd.to_datetime(s, errors="raise")
            return True
        except Exception:
            return False

    def _looks_numeric(self, s: pd.Series) -> bool:
        try:
            pd.to_numeric(s, errors="raise")
            return True
        except Exception:
            return False


