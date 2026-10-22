"""
Unit tests for Banker's Safety Algorithm.
Covers test cases TC-01 to TC-06 and TC-13 from SLA-2 Table 22,
multiple valid safe sequences, and single-process / zero-resource edge cases.
"""

import pytest
from algorithms.banker import (
    compute_need_matrix,
    run_safety_algorithm,
    find_all_safe_sequences
)
from utils.examples import PRELOADED_EXAMPLES


def test_tc01_need_calculation():
    """TC-01: Need calculation matches analytical SLA-1 / SLA-2 Table 19."""
    alloc = [[1, 0, 1], [1, 1, 0], [1, 1, 1]]
    maximum = [[2, 1, 1], [1, 2, 2], [2, 1, 2]]
    need = compute_need_matrix(alloc, maximum)

    assert need == [
        [1, 1, 0],  # P0
        [0, 1, 2],  # P1
        [1, 0, 1]   # P2
    ]


def test_tc02_safe_state_sla_sample():
    """TC-02: Sample execution returns SAFE with safe sequence P0 -> P1 -> P2."""
    ex = PRELOADED_EXAMPLES["A: Safe State (SLA-1 / SLA-2 Official Sample)"]
    result = run_safety_algorithm(ex.allocation, ex.maximum, ex.available)

    assert result.is_safe is True
    assert result.safe_sequence == [0, 1, 2]
    assert result.safe_sequence_str == "P0 -> P1 -> P2"
    assert len(result.unfinished_processes) == 0


def test_tc03_resource_conservation():
    """TC-03: Final Work equals sum of Allocations + initial Available = (4,3,3)."""
    alloc = [[1, 0, 1], [1, 1, 0], [1, 1, 1]]
    maximum = [[2, 1, 1], [1, 2, 2], [2, 1, 2]]
    avail = [1, 1, 1]
    result = run_safety_algorithm(alloc, maximum, avail)

    expected_final_work = [
        sum(alloc[i][j] for i in range(3)) + avail[j] for j in range(3)
    ]  # (1+1+1 + 1, 0+1+1 + 1, 1+0+1 + 1) = [4, 3, 3]

    assert result.final_work == expected_final_work
    assert result.final_work == [4, 3, 3]


def test_tc04_unsafe_no_eligible_process():
    """TC-04: Available = (0,0,0) yields immediate UNSAFE."""
    alloc = [[1, 0, 1], [1, 1, 0], [1, 1, 1]]
    maximum = [[2, 1, 1], [1, 2, 2], [2, 1, 2]]
    avail = [0, 0, 0]
    result = run_safety_algorithm(alloc, maximum, avail)

    assert result.is_safe is False
    assert len(result.safe_sequence) == 0
    assert result.unfinished_processes == [0, 1, 2]
    assert "UNSAFE STATE" in result.verdict_message


def test_tc05_unsafe_stall_after_progress():
    """TC-05: m=1 case where P0 finishes, but P1 and P2 stall (SLA-2 E7)."""
    alloc = [[1], [1], [1]]
    maximum = [[1], [3], [3]]
    avail = [0]
    result = run_safety_algorithm(alloc, maximum, avail)

    assert result.is_safe is False
    assert result.safe_sequence == [0]  # P0 completed
    assert result.unfinished_processes == [1, 2]  # P1 and P2 stalled


def test_tc06_single_process_case():
    """TC-06 / E8: Single process n=1, m=1."""
    alloc = [[1]]
    maximum = [[3]]
    avail = [2]
    result = run_safety_algorithm(alloc, maximum, avail)

    assert result.is_safe is True
    assert result.safe_sequence == [0]
    assert result.final_work == [3]


def test_tc13_order_independence_of_verdict():
    """TC-13: Reordering rows as P2, P0, P1 maintains SAFE verdict."""
    # Reordered:
    # Orig P2 -> Row 0: alloc [1,1,1], max [2,1,2]
    # Orig P0 -> Row 1: alloc [1,0,1], max [2,1,1]
    # Orig P1 -> Row 2: alloc [1,1,0], max [1,2,2]
    alloc = [[1, 1, 1], [1, 0, 1], [1, 1, 0]]
    maximum = [[2, 1, 2], [2, 1, 1], [1, 2, 2]]
    avail = [1, 1, 1]

    result = run_safety_algorithm(alloc, maximum, avail)
    assert result.is_safe is True
    assert len(result.safe_sequence) == 3


def test_multiple_valid_safe_sequences():
    """Validates that find_all_safe_sequences discovers all 4 valid sequences for Example A."""
    alloc = [[1, 0, 1], [1, 1, 0], [1, 1, 1]]
    maximum = [[2, 1, 1], [1, 2, 2], [2, 1, 2]]
    avail = [1, 1, 1]

    all_seqs = find_all_safe_sequences(alloc, maximum, avail)
    # The 4 mathematically valid safe sequences for this system are:
    # [0, 1, 2] (P0 -> P1 -> P2)
    # [0, 2, 1] (P0 -> P2 -> P1)
    # [2, 0, 1] (P2 -> P0 -> P1)
    # [2, 1, 0] (P2 -> P1 -> P0)
    assert len(all_seqs) == 4
    assert [0, 1, 2] in all_seqs
    assert [0, 2, 1] in all_seqs
    assert [2, 0, 1] in all_seqs
    assert [2, 1, 0] in all_seqs


def test_silberschatz_benchmark():
    """
    Tests classic 5-process 3-resource benchmark.
    Under lowest-index tie-breaking (SLA-2 Table 16), deterministic sequence is P1 -> P3 -> P0 -> P2 -> P4.
    """
    ex = PRELOADED_EXAMPLES["A2: Safe State (Silberschatz 5-Process Benchmark)"]
    result = run_safety_algorithm(ex.allocation, ex.maximum, ex.available)
    assert result.is_safe is True
    assert result.safe_sequence == [1, 3, 0, 2, 4]
    # Check that [1, 3, 4, 0, 2] is also recognized in all valid safe sequences
    assert [1, 3, 4, 0, 2] in result.all_safe_sequences
