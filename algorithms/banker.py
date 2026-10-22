"""
Banker's Algorithm Core Engine
Implements Modules M2 (Data Management), M3 (Need Matrix Calculation),
M4 (Safety Checking), and M5 (Safe-Sequence Generation).
"""

import time
from typing import List, Tuple, Dict, Any, Optional
import numpy as np


class StepTraceRecord:
    """Detailed record of one decision step in the safety algorithm."""
    def __init__(
        self,
        step_number: int,
        candidate_process: int,
        need_vector: List[int],
        work_before: List[int],
        is_eligible: bool,
        comparison_details: List[str],
        work_after: List[int],
        finish_status: List[bool],
        current_safe_sequence: List[int],
        explanation: str
    ):
        self.step_number = step_number
        self.candidate_process = candidate_process
        self.need_vector = need_vector
        self.work_before = work_before
        self.is_eligible = is_eligible
        self.comparison_details = comparison_details
        self.work_after = work_after
        self.finish_status = finish_status
        self.current_safe_sequence = current_safe_sequence
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "process": f"P{self.candidate_process}",
            "need": str(self.need_vector),
            "work_before": str(self.work_before),
            "eligible": "Yes" if self.is_eligible else "No",
            "comparisons": "; ".join(self.comparison_details),
            "work_after": str(self.work_after),
            "finish": str([int(f) for f in self.finish_status]),
            "safe_sequence": " -> ".join([f"P{p}" for p in self.current_safe_sequence]) if self.current_safe_sequence else "[None]",
            "explanation": self.explanation
        }


class SafetyCheckResult:
    """Comprehensive result object returned by the Banker's safety check."""
    def __init__(
        self,
        is_safe: bool,
        safe_sequence: List[int],
        step_trace: List[StepTraceRecord],
        need_matrix: List[List[int]],
        initial_work: List[int],
        final_work: List[int],
        unfinished_processes: List[int],
        eligibility_checks_count: int,
        element_comparisons_count: int,
        execution_time_seconds: float,
        verdict_message: str,
        educational_explanation: str,
        all_safe_sequences: Optional[List[List[int]]] = None
    ):
        self.is_safe = is_safe
        self.safe_sequence = safe_sequence
        self.step_trace = step_trace
        self.need_matrix = need_matrix
        self.initial_work = initial_work
        self.final_work = final_work
        self.unfinished_processes = unfinished_processes
        self.eligibility_checks_count = eligibility_checks_count
        self.element_comparisons_count = element_comparisons_count
        self.execution_time_seconds = execution_time_seconds
        self.verdict_message = verdict_message
        self.educational_explanation = educational_explanation
        self.all_safe_sequences = all_safe_sequences or []

    @property
    def safe_sequence_str(self) -> str:
        if self.is_safe and self.safe_sequence:
            return " -> ".join([f"P{p}" for p in self.safe_sequence])
        return "No Safe Sequence Found"


def compute_need_matrix(allocation: List[List[int]], maximum: List[List[int]]) -> List[List[int]]:
    """
    Module M3: Computes Need matrix = Maximum - Allocation.
    Need[i][j] represents the remaining resources that process Pi may claim.
    """
    n = len(allocation)
    m = len(allocation[0])
    need = []
    for i in range(n):
        row = []
        for j in range(m):
            row.append(maximum[i][j] - allocation[i][j])
        need.append(row)
    return need


def is_eligible(
    process_idx: int,
    need_row: List[int],
    work_vector: List[int],
    finish_flag: bool
) -> Tuple[bool, List[str], int]:
    """
    Checks if process process_idx can complete with current work_vector.
    Condition: Finish[i] == False and Need[i][j] <= Work[j] for all j = 0..m-1.
    Returns: (is_eligible, comparison_details, element_comparisons_performed)
    """
    if finish_flag:
        return False, ["Process already marked as finished"], 0

    m = len(work_vector)
    comparison_details = []
    element_comparisons = 0

    for j in range(m):
        element_comparisons += 1
        comp_str = f"R{j}: Need({need_row[j]}) <= Work({work_vector[j]})"
        if need_row[j] <= work_vector[j]:
            comparison_details.append(f"{comp_str} [Pass]")
        else:
            comparison_details.append(f"{comp_str} [FAIL]")
            return False, comparison_details, element_comparisons

    return True, comparison_details, element_comparisons


def run_safety_algorithm(
    allocation: List[List[int]],
    maximum: List[List[int]],
    available: List[int],
    compute_all_sequences: bool = True
) -> SafetyCheckResult:
    """
    Module M4 & M5: Executes the traditional Banker's Safety Algorithm.
    Follows deterministic lowest-index tie-breaking rule from SLA-2 Section 7.5.

    Steps:
      1. Need = Maximum - Allocation
      2. Work = copy of Available
      3. Finish = [False] * n
      4. SafeSequence = []
      5. Loop: find lowest index i where Finish[i]==False and Need[i] <= Work.
         If found: Work += Allocation[i], Finish[i] = True, append i to SafeSequence.
         Restart search.
         If none found: stop loop.
      6. Verdict: Safe if all(Finish), else Unsafe.
    """
    start_time = time.perf_counter()

    n = len(allocation)
    m = len(available)

    # M3: Need Matrix
    need = compute_need_matrix(allocation, maximum)

    # Initialize working copies
    work = [int(v) for v in available]
    finish = [False] * n
    safe_sequence: List[int] = []
    step_trace: List[StepTraceRecord] = []

    eligibility_checks = 0
    element_comparisons_total = 0
    step_counter = 1

    # Record initial state (Step 0)
    step_trace.append(StepTraceRecord(
        step_number=0,
        candidate_process=-1,
        need_vector=[],
        work_before=list(work),
        is_eligible=True,
        comparison_details=["Initial state setup: Work = Available"],
        work_after=list(work),
        finish_status=list(finish),
        current_safe_sequence=[],
        explanation=f"System initialized with Work = {work}. All processes marked as unfinished."
    ))

    # Main Safety Checking Loop
    while len(safe_sequence) < n:
        found_eligible = False

        for i in range(n):
            if not finish[i]:
                eligibility_checks += 1
                eligible, details, elem_comps = is_eligible(i, need[i], work, finish[i])
                element_comparisons_total += elem_comps

                if eligible:
                    # Process i can be simulated to completion
                    work_before = list(work)
                    for j in range(m):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(i)
                    found_eligible = True

                    explanation = (
                        f"Process P{i} is selected: Need {need[i]} <= Work {work_before}. "
                        f"P{i} runs to completion, releases its allocated resources {allocation[i]}. "
                        f"Updated Work = {work}."
                    )

                    step_trace.append(StepTraceRecord(
                        step_number=step_counter,
                        candidate_process=i,
                        need_vector=list(need[i]),
                        work_before=work_before,
                        is_eligible=True,
                        comparison_details=details,
                        work_after=list(work),
                        finish_status=list(finish),
                        current_safe_sequence=list(safe_sequence),
                        explanation=explanation
                    ))

                    step_counter += 1
                    # Restart search from lowest index to maintain deterministic order
                    break

        if not found_eligible:
            # Stalled: No unfinished process can satisfy its remaining Need with current Work
            unfinished = [i for i in range(n) if not finish[i]]
            break

    elapsed_time = time.perf_counter() - start_time
    is_safe = all(finish)
    unfinished_processes = [i for i in range(n) if not finish[i]]

    if is_safe:
        verdict_message = f"SAFE STATE: A valid execution sequence exists ({' -> '.join([f'P{p}' for p in safe_sequence])})."
        educational_explanation = (
            "The system is currently in a SAFE STATE. This means the operating system can allocate resources "
            "to each process in the order of the safe sequence such that every process can satisfy its maximum "
            "resource demand, complete its tasks, and release its resources back to the pool without deadlocking. "
            "Deadlock is guaranteed to be avoided."
        )
    else:
        verdict_message = f"UNSAFE STATE: No safe sequence exists. Unfinished processes: {['P' + str(p) for p in unfinished_processes]}."
        educational_explanation = (
            "The system is currently in an UNSAFE STATE. No remaining unfinished process has a Need vector "
            f"less than or equal to the current Work vector {work}. "
            "IMPORTANT OPERATING SYSTEMS DISTINCTION: An unsafe state does NOT mean the system is currently deadlocked. "
            "Processes might still complete if they voluntarily release resources early or never request their full Maximum. "
            "However, the operating system can no longer guarantee that deadlock will not occur if all processes simultaneously "
            "demand their full declared maximum claims. Therefore, the Banker's Algorithm cautiously avoids entering this state."
        )

    all_sequences = []
    if compute_all_sequences and is_safe:
        all_sequences = find_all_safe_sequences(allocation, maximum, available)

    return SafetyCheckResult(
        is_safe=is_safe,
        safe_sequence=safe_sequence,
        step_trace=step_trace,
        need_matrix=need,
        initial_work=list(available),
        final_work=list(work),
        unfinished_processes=unfinished_processes,
        eligibility_checks_count=eligibility_checks,
        element_comparisons_count=element_comparisons_total,
        execution_time_seconds=elapsed_time,
        verdict_message=verdict_message,
        educational_explanation=educational_explanation,
        all_safe_sequences=all_sequences
    )


def find_all_safe_sequences(
    allocation: List[List[int]],
    maximum: List[List[int]],
    available: List[int]
) -> List[List[int]]:
    """
    Finds all mathematically valid permutations of safe sequences using DFS backtracking.
    Demonstrates to students that the safe sequence is not necessarily unique.
    """
    n = len(allocation)
    m = len(available)
    need = compute_need_matrix(allocation, maximum)

    results: List[List[int]] = []

    def backtrack(current_work: List[int], finish_flags: List[bool], current_path: List[int]):
        if len(current_path) == n:
            results.append(list(current_path))
            return

        for i in range(n):
            if not finish_flags[i]:
                # Check if Need[i] <= current_work
                can_run = True
                for j in range(m):
                    if need[i][j] > current_work[j]:
                        can_run = False
                        break
                if can_run:
                    new_work = [current_work[j] + allocation[i][j] for j in range(m)]
                    finish_flags[i] = True
                    current_path.append(i)

                    backtrack(new_work, finish_flags, current_path)

                    current_path.pop()
                    finish_flags[i] = False

    backtrack(list(available), [False] * n, [])
    return results
