from __future__ import annotations

import json
import hashlib
from typing import Dict, Any, List


class TANAWChartValidator:
    """
    Phase 4: Chart Builder Validation (no-duplicate check, sanity rules)
    - Computes stable hashes of chart data payloads to flag potential duplication
    - Adds lightweight sanity checks (min points, presence of x/y or lines)
    """

    def __init__(self) -> None:
        pass

    def validate(self, charts: List[Dict[str, Any]]) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            "duplicates": [],
            "issues": [],
            "summary": {"checked": len(charts), "duplicates": 0, "issues": 0},
        }

        seen: Dict[str, str] = {}  # hash -> chart id/title

        for idx, chart in enumerate(charts):
            cid = chart.get("id") or chart.get("title") or f"chart_{idx}"
            data = chart.get("data", {})
            chart_type = chart.get("type", "")

            # Sanity checks
            if not self._has_points(data):
                report["issues"].append({
                    "id": cid,
                    "type": "no_points",
                    "message": "Chart has no data points",
                })

            # Phase 4: Multi-line chart specific validation
            if chart_type == "multi_line":
                multi_line_issues = self._validate_multi_line_chart(data, cid)
                report["issues"].extend(multi_line_issues)

            # Duplicate detection by data hash
            try:
                h = self._hash_payload(data)
                if h in seen:
                    report["duplicates"].append({
                        "id": cid,
                        "dup_of": seen[h],
                        "message": "Chart data duplicates another analytic",
                    })
                else:
                    seen[h] = cid
            except Exception:
                # Ignore hashing errors; keep system robust
                pass

        report["summary"]["duplicates"] = len(report["duplicates"])
        report["summary"]["issues"] = len(report["issues"])
        return report

    # ---------------- helpers ----------------
    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        # Canonicalize JSON to ensure consistent hashing
        s = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def _has_points(self, data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict):
            return False
        if "x" in data and isinstance(data.get("x"), list):
            return len(data.get("x", [])) > 0
        if "lines" in data and isinstance(data.get("lines"), dict):
            # Multi-line chart validation: check that all lines have data
            lines = data["lines"]
            if not lines or len(lines) == 0:
                return False
            # Check that all lines have the same length as x-axis
            x_length = len(data.get("x", []))
            if x_length == 0:
                return False
            # Validate each line has proper data
            for line_name, line_data in lines.items():
                if not isinstance(line_data, list) or len(line_data) != x_length:
                    return False
                # Check for all zeros (empty data)
                if all(v == 0 for v in line_data):
                    return False
            return True
        if "historical" in data and "forecast" in data:
            return (len(data["historical"].get("x", [])) + len(data["forecast"].get("x", []))) > 0
        return False

    def _validate_multi_line_chart(self, data: Dict[str, Any], chart_id: str) -> List[Dict[str, Any]]:
        """Phase 4: Validate multi-line chart data structure"""
        issues = []
        
        if not isinstance(data, dict):
            issues.append({
                "id": chart_id,
                "type": "invalid_data_structure",
                "message": "Multi-line chart data is not a dictionary"
            })
            return issues
        
        # Check for required multi-line structure
        if "lines" not in data:
            issues.append({
                "id": chart_id,
                "type": "missing_lines_object",
                "message": "Multi-line chart missing 'lines' object"
            })
            return issues
        
        if "x" not in data:
            issues.append({
                "id": chart_id,
                "type": "missing_x_axis",
                "message": "Multi-line chart missing 'x' axis data"
            })
            return issues
        
        lines = data.get("lines", {})
        x_data = data.get("x", [])
        
        if not isinstance(lines, dict) or len(lines) == 0:
            issues.append({
                "id": chart_id,
                "type": "empty_lines",
                "message": "Multi-line chart has no product lines"
            })
            return issues
        
        if not isinstance(x_data, list) or len(x_data) == 0:
            issues.append({
                "id": chart_id,
                "type": "empty_x_axis",
                "message": "Multi-line chart has no x-axis data"
            })
            return issues
        
        # Validate each product line
        for line_name, line_data in lines.items():
            if not isinstance(line_data, list):
                issues.append({
                    "id": chart_id,
                    "type": "invalid_line_data",
                    "message": f"Product line '{line_name}' is not a list"
                })
                continue
            
            if len(line_data) != len(x_data):
                issues.append({
                    "id": chart_id,
                    "type": "mismatched_line_length",
                    "message": f"Product line '{line_name}' length ({len(line_data)}) doesn't match x-axis length ({len(x_data)})"
                })
                continue
            
            # Check for all zeros (no data)
            if all(v == 0 for v in line_data):
                issues.append({
                    "id": chart_id,
                    "type": "empty_line_data",
                    "message": f"Product line '{line_name}' has no data (all zeros)"
                })
                continue
        
        return issues


