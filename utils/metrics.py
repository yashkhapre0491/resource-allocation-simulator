"""
Performance Analysis & Metrics Engine
Implements Module M6: Computes execution times, operation counts,
theoretical bounds, resource utilization, and side-by-side comparisons.
"""

import time
from typing import List, Dict, Any, Tuple
import numpy as np
from algorithms.banker import run_safety_algorithm, compute_need_matrix, SafetyCheckResult
from algorithms.dfrr import run_dfrr_simulation, DFRRSimulationResult


def compute_resource_utilization(
    allocation: List[List[int]],
    available: List[int]
) -> Dict[str, Any]:
    """
    Computes total resource instances, allocated amounts, free amounts,
    and allocation percentages per resource type.
    """
    alloc_arr = np.array(allocation)
    avail_arr = np.array(available)

    sum_alloc = np.sum(alloc_arr, axis=0)
    total = sum_alloc + avail_arr

    m = len(available)
    utilization_per_res = []
    for j in range(m):
        pct = (sum_alloc[j] / total[j] * 100.0) if total[j] > 0 else 0.0
        utilization_per_res.append({
            "resource": f"R{j}",
            "allocated": int(sum_alloc[j]),
            "available": int(avail_arr[j]),
            "total": int(total[j]),
            "utilization_pct": round(pct, 2)
        })

    overall_alloc = int(np.sum(sum_alloc))
    overall_total = int(np.sum(total))
    overall_pct = (overall_alloc / overall_total * 100.0) if overall_total > 0 else 0.0

    return {
        "per_resource": utilization_per_res,
        "overall_allocated": overall_alloc,
        "overall_total": overall_total,
        "overall_utilization_pct": round(overall_pct, 2)
    }


def get_theoretical_complexity(n: int, m: int) -> Dict[str, Any]:
    """
    Returns theoretical operation bounds from SLA-2 Section 9.2 (Tables 29 & 30):
      - Need Matrix: O(n * m)
      - Safety Algorithm Worst-case: O(n^2 * m)
      - Auxiliary matrix storage: O(n * m)
    """
    need_ops = n * m
    safety_worst_case_ops = (n ** 2) * m
    storage_elements = 3 * (n * m) + (2 * m) + n  # Alloc + Max + Need + Avail + Work + Finish

    return {
        "n": n,
        "m": m,
        "need_complexity_formula": "O(n · m)",
        "need_ops_bound": need_ops,
        "safety_complexity_formula": "O(n² · m)",
        "safety_worst_case_bound": safety_worst_case_ops,
        "storage_elements": storage_elements
    }


def benchmark_side_by_side(
    allocation: List[List[int]],
    maximum: List[List[int]],
    available_normal: List[int],
    reserved_pool: List[int],
    runs: int = 10
) -> Dict[str, Any]:
    """
    Executes multiple runs to benchmark Banker's Algorithm vs DFRR on the identical state.
    Reports median timing, checks, and outcome comparison.
    """
    n = len(allocation)
    m = len(available_normal)

    # In traditional Banker's, available includes the normal free resources.
    # What if reserved pool is added to available for Banker's? We test Banker's on Normal Available,
    # and also on Combined Total Available to give an honest academic comparison!
    banker_normal_times = []
    banker_normal_result: SafetyCheckResult = None
    for _ in range(runs):
        t0 = time.perf_counter()
        banker_normal_result = run_safety_algorithm(allocation, maximum, available_normal, compute_all_sequences=False)
        t1 = time.perf_counter()
        banker_normal_times.append((t1 - t0) * 1e6)  # microseconds

    # Banker's with all free resources combined (Available + Reserved)
    combined_available = [available_normal[j] + reserved_pool[j] for j in range(m)]
    banker_combined_times = []
    banker_combined_result: SafetyCheckResult = None
    for _ in range(runs):
        t0 = time.perf_counter()
        banker_combined_result = run_safety_algorithm(allocation, maximum, combined_available, compute_all_sequences=False)
        t1 = time.perf_counter()
        banker_combined_times.append((t1 - t0) * 1e6)

    # DFRR
    dfrr_times = []
    dfrr_result: DFRRSimulationResult = None
    for _ in range(runs):
        t0 = time.perf_counter()
        dfrr_result = run_dfrr_simulation(allocation, maximum, available_normal, reserved_pool)
        t1 = time.perf_counter()
        dfrr_times.append((t1 - t0) * 1e6)

    return {
        "n": n,
        "m": m,
        "runs": runs,
        "banker_normal": {
            "is_safe": banker_normal_result.is_safe,
            "sequence": banker_normal_result.safe_sequence_str,
            "median_time_us": round(float(np.median(banker_normal_times)), 2),
            "checks": banker_normal_result.eligibility_checks_count,
            "element_comparisons": banker_normal_result.element_comparisons_count
        },
        "banker_combined": {
            "is_safe": banker_combined_result.is_safe,
            "sequence": banker_combined_result.safe_sequence_str,
            "median_time_us": round(float(np.median(banker_combined_times)), 2),
            "checks": banker_combined_result.eligibility_checks_count,
            "element_comparisons": banker_combined_result.element_comparisons_count
        },
        "dfrr": {
            "is_successful": dfrr_result.is_successful,
            "sequence": dfrr_result.sequence_str,
            "median_time_us": round(float(np.median(dfrr_times)), 2),
            "reserve_invocations": dfrr_result.reserved_pool_invocations,
            "events_count": len(dfrr_result.events)
        }
    }
