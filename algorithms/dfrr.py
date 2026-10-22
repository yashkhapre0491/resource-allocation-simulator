"""
Deadlock-Free Resource Reservation (DFRR) Engine
Research Extension based on Botlagunta, Agrawal & Rao (2022):
"A Novel Resource Management Technique for Deadlock-Free Systems",
International Journal of Information Technology, Vol. 14, No. 2, pp. 627-635.

NOTE: This is an academic research-inspired prototype. It demonstrates how a
dedicated reserved resource pool can assist stalled processes in reaching completion,
thereby avoiding circular-wait conditions without requiring full recursive permutation
checks on every request.
"""

import time
import copy
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from algorithms.banker import compute_need_matrix


class DFRREventLog:
    """Log entry detailing a DFRR simulation event."""
    def __init__(
        self,
        step: int,
        event_type: str,  # 'INIT', 'NORMAL_ALLOC', 'RESERVE_INVOKED', 'RELEASE', 'STALL'
        process_id: int,
        action: str,
        normal_available: List[int],
        reserved_pool: List[int],
        allocated_total: List[int],
        explanation: str
    ):
        self.step = step
        self.event_type = event_type
        self.process_id = process_id
        self.action = action
        self.normal_available = list(normal_available)
        self.reserved_pool = list(reserved_pool)
        self.allocated_total = list(allocated_total)
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "type": self.event_type,
            "process": f"P{self.process_id}" if self.process_id >= 0 else "-",
            "action": self.action,
            "normal_available": str(self.normal_available),
            "reserved_pool": str(self.reserved_pool),
            "allocated_total": str(self.allocated_total),
            "explanation": self.explanation
        }


class DFRRSimulationResult:
    """Encapsulates the full execution state and comparison metrics of DFRR."""
    def __init__(
        self,
        is_successful: bool,
        execution_sequence: List[int],
        reserved_pool_invocations: int,
        events: List[DFRREventLog],
        total_resources: List[int],
        initial_normal_available: List[int],
        initial_reserved_pool: List[int],
        final_normal_available: List[int],
        final_reserved_pool: List[int],
        unfinished_processes: List[int],
        execution_time_seconds: float,
        verdict_message: str,
        research_notes: str
    ):
        self.is_successful = is_successful
        self.execution_sequence = execution_sequence
        self.reserved_pool_invocations = reserved_pool_invocations
        self.events = events
        self.total_resources = total_resources
        self.initial_normal_available = initial_normal_available
        self.initial_reserved_pool = initial_reserved_pool
        self.final_normal_available = final_normal_available
        self.final_reserved_pool = final_reserved_pool
        self.unfinished_processes = unfinished_processes
        self.execution_time_seconds = execution_time_seconds
        self.verdict_message = verdict_message
        self.research_notes = research_notes

    @property
    def sequence_str(self) -> str:
        if self.is_successful and self.execution_sequence:
            return " -> ".join([f"P{p}" for p in self.execution_sequence])
        return "No Complete Sequence (Stalled)"


def run_dfrr_simulation(
    allocation: List[List[int]],
    maximum: List[List[int]],
    available_normal: List[int],
    reserved_pool: List[int],
    total_resources: Optional[List[int]] = None
) -> DFRRSimulationResult:
    """
    Simulates resource scheduling using Deadlock-Free Resource Reservation (DFRR).

    Invariants maintained:
      1. Physical Invariant: Total[j] = sum(Allocation[:][j]) + Available_Normal[j] + Reserved_Pool[j]
      2. No double allocation: Reserved resources temporarily leased to a process are locked until release.
      3. No negative resources at any time.

    Algorithm:
      1. Check unfinished processes that can be satisfied by Available_Normal (Normal phase).
         If found, process runs, finishes, releases allocation to Available_Normal.
      2. If no process can be satisfied by Available_Normal alone:
         Search for an unfinished process Pi where Need[i][j] <= Available_Normal[j] + Reserved_Pool[j].
         If found (Reservation phase):
           - Compute deficit: Deficit[j] = max(0, Need[i][j] - Available_Normal[j]).
           - Deduct Deficit from Reserved_Pool.
           - Allocate all remaining Need to Pi.
           - Pi finishes and releases:
               Deficit is restored back to Reserved_Pool.
               Its original Allocation is added to Available_Normal.
           - Normal pool is now larger; continue loop.
      3. If no process can be satisfied even with Reserved_Pool, the system stalls.
    """
    start_time = time.perf_counter()

    n = len(allocation)
    m = len(available_normal)

    # Compute sum of initial allocations
    current_alloc = copy.deepcopy(allocation)
    sum_alloc = [sum(current_alloc[i][j] for i in range(n)) for j in range(m)]

    # Compute or verify total resources
    if total_resources is None:
        total_resources = [sum_alloc[j] + available_normal[j] + reserved_pool[j] for j in range(m)]
    else:
        # Validate total invariant
        for j in range(m):
            expected = sum_alloc[j] + available_normal[j] + reserved_pool[j]
            if total_resources[j] != expected:
                raise ValueError(
                    f"DFRR Accounting Invariant Mismatch on R{j}: "
                    f"Total ({total_resources[j]}) != Alloc ({sum_alloc[j]}) + Normal ({available_normal[j]}) + Reserved ({reserved_pool[j]})."
                )

    need = compute_need_matrix(current_alloc, maximum)
    norm_avail = list(available_normal)
    res_pool = list(reserved_pool)
    finish = [False] * n
    execution_seq: List[int] = []
    events: List[DFRREventLog] = []
    reserve_invocations = 0

    step = 0
    events.append(DFRREventLog(
        step=step,
        event_type="INIT",
        process_id=-1,
        action="System Initialized",
        normal_available=norm_avail,
        reserved_pool=res_pool,
        allocated_total=sum_alloc,
        explanation=f"Initial state: Normal Available={norm_avail}, Reserved Pool={res_pool}, Total Physical={total_resources}."
    ))

    while len(execution_seq) < n:
        step += 1
        found_process = False

        # Phase 1: Normal Allocation Check (Need <= norm_avail)
        for i in range(n):
            if not finish[i]:
                can_satisfy_normal = all(need[i][j] <= norm_avail[j] for j in range(m))
                if can_satisfy_normal:
                    # Allocate and complete process i
                    finish[i] = True
                    execution_seq.append(i)
                    found_process = True

                    # Process completes and releases allocation to normal pool
                    for j in range(m):
                        norm_avail[j] += current_alloc[i][j]

                    sum_alloc = [sum(current_alloc[p][j] for p in range(n) if not finish[p]) for j in range(m)]

                    events.append(DFRREventLog(
                        step=step,
                        event_type="NORMAL_ALLOC",
                        process_id=i,
                        action=f"P{i} satisfied via Normal Available",
                        normal_available=norm_avail,
                        reserved_pool=res_pool,
                        allocated_total=sum_alloc,
                        explanation=(
                            f"Process P{i} satisfied by normal pool (Need {need[i]} <= Avail {norm_avail}). "
                            f"Completed and released {current_alloc[i]} back to Normal Available."
                        )
                    ))
                    break

        if found_process:
            continue

        # Phase 2: Reserve Pool Check (Need <= norm_avail + res_pool)
        for i in range(n):
            if not finish[i]:
                can_satisfy_with_reserve = all(need[i][j] <= (norm_avail[j] + res_pool[j]) for j in range(m))
                if can_satisfy_with_reserve:
                    reserve_invocations += 1
                    found_process = True
                    finish[i] = True
                    execution_seq.append(i)

                    # Compute deficit borrowed from reserve pool
                    deficit = [max(0, need[i][j] - norm_avail[j]) for j in range(m)]

                    # Deduct deficit temporarily from reserve pool
                    for j in range(m):
                        res_pool[j] -= deficit[j]
                        norm_avail[j] -= (need[i][j] - deficit[j])

                    # Process completes and releases all resources
                    # 1. Restore reserved pool
                    for j in range(m):
                        res_pool[j] += deficit[j]
                    # 2. Add process's allocation + remaining resources to normal available
                    for j in range(m):
                        norm_avail[j] += (current_alloc[i][j] + (need[i][j] - deficit[j]))

                    sum_alloc = [sum(current_alloc[p][j] for p in range(n) if not finish[p]) for j in range(m)]

                    events.append(DFRREventLog(
                        step=step,
                        event_type="RESERVE_INVOKED",
                        process_id=i,
                        action=f"P{i} UNBLOCKED using Reserved Pool",
                        normal_available=norm_avail,
                        reserved_pool=res_pool,
                        allocated_total=sum_alloc,
                        explanation=(
                            f"Normal pool alone was insufficient for P{i} (Need {need[i]} > Avail). "
                            f"DFRR invoked Reserved Pool: borrowed {deficit}. P{i} completed, restored "
                            f"reserved pool to {res_pool}, and released its held resources {current_alloc[i]} into Normal Available."
                        )
                    ))
                    break

        if not found_process:
            # Stalled completely: Neither normal nor reserved pool can satisfy any remaining process
            unfinished = [i for i in range(n) if not finish[i]]
            events.append(DFRREventLog(
                step=step,
                event_type="STALL",
                process_id=-1,
                action="System Stalled",
                normal_available=norm_avail,
                reserved_pool=res_pool,
                allocated_total=sum_alloc,
                explanation=(
                    f"Stall condition: None of the remaining processes ({['P' + str(p) for p in unfinished]}) "
                    f"can be satisfied even with combined Normal ({norm_avail}) + Reserved ({res_pool}) resources."
                )
            ))
            break

    elapsed_time = time.perf_counter() - start_time
    is_successful = all(finish)
    unfinished_processes = [i for i in range(n) if not finish[i]]

    if is_successful:
        verdict = f"DFRR SUCCESSFUL: All processes completed safely ({' -> '.join([f'P{p}' for p in execution_seq])})."
        notes = (
            "The DFRR model successfully avoided system stalling by leveraging the reserved resource pool "
            f"({reserve_invocations} reserve invocation(s)). Processes that would have caused a bottleneck "
            "were temporarily assisted to completion, freeing up resources for remaining tasks."
        )
    else:
        verdict = f"DFRR STALLED: Unable to complete all processes. Unfinished: {['P' + str(p) for p in unfinished_processes]}."
        notes = (
            "The configured reserve pool was insufficient to unblock remaining processes. "
            "Under DFRR, if the reserved pool size is smaller than the deficit of the smallest pending process, "
            "the system cannot guarantee deadlock-free progress without additional external resources."
        )

    return DFRRSimulationResult(
        is_successful=is_successful,
        execution_sequence=execution_seq,
        reserved_pool_invocations=reserve_invocations,
        events=events,
        total_resources=total_resources,
        initial_normal_available=list(available_normal),
        initial_reserved_pool=list(reserved_pool),
        final_normal_available=norm_avail,
        final_reserved_pool=res_pool,
        unfinished_processes=unfinished_processes,
        execution_time_seconds=elapsed_time,
        verdict_message=verdict,
        research_notes=notes
    )
