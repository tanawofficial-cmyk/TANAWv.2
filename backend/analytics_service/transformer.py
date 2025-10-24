from __future__ import annotations

from typing import Dict, Any, List, Optional
import pandas as pd


class TANAWChartTransformer:
    """
    Phase 3: Data Cleaning & Transformation (non-blocking pilot)
    - Standardizes grouping/aggregation per analytic
    - Returns grouped DataFrame + summary; does not replace existing charts yet
    - Safe and read-only relative to the current generation flow
    """

    ANALYTIC_TRANSFORMS: Dict[str, Dict[str, Any]] = {
        "sales_summary": {"group_by": ["Sale_Date"], "agg": {"Sales_Amount": "sum"}},
        "product_performance": {"group_by": ["Product", "Product_Name", "Product_Category"], "agg": {"Sales_Amount": "sum"}},
        "regional_sales": {"group_by": ["Region"], "agg": {"Sales_Amount": "sum"}},
        "product_demand_forecast": {"group_by": ["Sale_Date", "Product", "Product_Name", "Product_Category"], "agg": {"Quantity_Sold": "sum"}},
    }

    def __init__(self) -> None:
        pass

    def transform_for_analytic(self, df: pd.DataFrame, analytic_key: str, x: Optional[str], y: Optional[str], group: Optional[str]) -> Dict[str, Any]:
        rules = self.ANALYTIC_TRANSFORMS.get(analytic_key, {})

        # Resolve effective group_by based on available columns
        group_by: List[str] = []
        for candidate in rules.get("group_by", []):
            if candidate in df.columns and candidate not in group_by:
                group_by.append(candidate)
        # Include resolver suggestions
        for col in [x, group]:
            if col and col in df.columns and col not in group_by:
                group_by.append(col)

        # Resolve effective agg dict
        agg: Dict[str, str] = {}
        for k, v in rules.get("agg", {}).items():
            if k in df.columns:
                agg[k] = v
        # Include resolver Y if not present
        if y and y in df.columns and y not in agg:
            agg[y] = "sum"

        summary: Dict[str, Any] = {
            "analytic": analytic_key,
            "group_by": group_by,
            "agg": agg,
            "rows_in": len(df),
        }

        if not group_by or not agg:
            summary["status"] = "skipped"
            summary["reason"] = "Insufficient group_by or agg columns"
            return {"summary": summary, "data": None}

        try:
            grouped = df.groupby(group_by).agg(agg).reset_index()
            # Sort by X if available
            if x and x in grouped.columns:
                try:
                    grouped = grouped.sort_values(x)
                except Exception:
                    pass

            summary["rows_out"] = len(grouped)
            summary["status"] = "ok"
            return {"summary": summary, "data": grouped}
        except Exception as e:
            summary["status"] = "error"
            summary["reason"] = str(e)
            return {"summary": summary, "data": None}


