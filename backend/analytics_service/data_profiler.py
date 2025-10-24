from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class TANAWDataProfiler:
    """
    Phase 1: Data Validation & Profiling (read-only)
    - Verifies canonical columns per analytic (non-blocking)
    - Profiles dtypes, null ratios, uniqueness, sample values
    - Attempts safe type coercions (copy) to surface issues
    - Emits a compact JSON-serializable profile

    NOTE: This module does NOT mutate the original DataFrame used by the
    existing pipeline; it works on copies and only returns metadata.
    """

    # Canonical expectations per analytic (minimal for P1)
    ANALYTIC_REQUIREMENTS: Dict[str, Dict[str, List[str]]] = {
        "sales_summary": {
            "required_any": {
                "Date": ["Sale_Date", "Date", "Order_Date", "Invoice_Date"],
                "Sales": ["Sales_Amount", "Sales", "Revenue", "Amount"],
            }
        },
        "product_performance": {
            "required_any": {
                "Product": ["Product", "Product_Name", "Product_ID", "Item", "Product_Category"],
                "Sales": ["Sales_Amount", "Sales", "Revenue", "Amount"],
            }
        },
        "regional_sales": {
            "required_any": {
                "Region": ["Region", "Area", "Branch", "Location"],
                "Sales": ["Sales_Amount", "Sales", "Revenue", "Amount"],
            }
        },
        "product_demand_forecast": {
            "required_any": {
                "Date": ["Sale_Date", "Date"],
                "Quantity": ["Quantity_Sold", "Quantity", "Units_Sold", "Demand"],
                "Product": ["Product", "Product_Name", "Product_Category"],
            }
        },
    }

    def __init__(self) -> None:
        pass

    def build_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Return a compact profile describing the dataset.
        Safe for JSON; converts numpy types to python primitives.
        """
        profile: Dict[str, Any] = {
            "shape": list(df.shape),
            "columns": list(df.columns),
            "column_profile": {},
            "coercion_preview": {},
        }

        total_rows = len(df) if len(df) > 0 else 1

        for col in df.columns:
            s = df[col]
            dtype = str(s.dtype)
            null_pct = float(s.isna().mean())
            uniq_ratio = float(s.nunique(dropna=True) / total_rows)
            sample_vals = self._sample_values(s)

            profile["column_profile"][col] = {
                "dtype": dtype,
                "null_ratio": round(null_pct, 6),
                "unique_ratio": round(uniq_ratio, 6),
                "sample": sample_vals,
            }

            # Non-destructive coercion preview (for observability only)
            profile["coercion_preview"][col] = {
                "as_datetime_ok": self._can_datetime(s),
                "as_numeric_ok": self._can_numeric(s),
                "looks_categorical": self._looks_categorical(s, uniq_ratio),
            }

        return profile

    def validate_requirements(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check which analytics have their minimal canonical columns present.
        Non-blocking: only reports findings.
        """
        results: Dict[str, Any] = {}
        cols_lower = {c.lower(): c for c in df.columns}

        for analytic, spec in self.ANALYTIC_REQUIREMENTS.items():
            req_any = spec.get("required_any", {})
            found: Dict[str, Optional[str]] = {}
            missing: List[str] = []

            for role, candidates in req_any.items():
                chosen = None
                for cand in candidates:
                    if cand.lower() in cols_lower:
                        chosen = cols_lower[cand.lower()]
                        break
                if chosen:
                    found[role] = chosen
                else:
                    found[role] = None
                    missing.append(role)

            results[analytic] = {
                "found": found,
                "missing_roles": missing,
                "ready": len(missing) == 0,
            }

        return results

    # ------------------- helpers -------------------
    def _sample_values(self, s: pd.Series, k: int = 3) -> List[Any]:
        try:
            vals = s.dropna().astype(str).unique().tolist()[:k]
            return vals
        except Exception:
            return []

    def _can_datetime(self, s: pd.Series) -> bool:
        try:
            pd.to_datetime(s, errors="raise")
            return True
        except Exception:
            return False

    def _can_numeric(self, s: pd.Series) -> bool:
        try:
            pd.to_numeric(s, errors="raise")
            return True
        except Exception:
            return False

    def _looks_categorical(self, s: pd.Series, uniq_ratio: float) -> bool:
        # Heuristic: low cardinality relative to rows
        return uniq_ratio < 0.05 or s.dtype == object


