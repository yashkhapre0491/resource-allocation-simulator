"""
Unit tests for Deadlock-Free Resource Reservation (DFRR) Prototype.
Covers resource accounting invariants, reserve pool unblocking,
replenishment, over-allocation prevention, and stall handling.
"""

import pytest
from algorithms.dfrr import run_dfrr_simulation
from algorithms.banker import run_safety_algorithm
from utils.examples import PRELOADED_EXAMPLES


def test_dfrr_unblocks_stalled_system():
    """Example F: Normal Banker's is UNSAFE, but DFRR completes using reserve pool."""
    ex = PRELOADED_EXAMPLES["F: DFRR Research Scenario (Reserve Pool Unblocks System)"]

    # 1. First verify standard Banker's stalls with available=[0, 1]
    banker_res = run_safety_algorithm(ex.allocation, ex.maximum, ex.available)
    assert banker_res.is_safe is False
    assert len(banker_res.safe_sequence) == 0

    # 2. Run DFRR with reserved_pool=[2, 0]
    dfrr_res = run_dfrr_simulation(
        allocation=ex.allocation,
        maximum=ex.maximum,
        available_normal=ex.available,
        reserved_pool=ex.reserved_pool
    )

    assert dfrr_res.is_successful is True
    assert dfrr_res.reserved_pool_invocations >= 1
    assert len(dfrr_res.execution_sequence) == 3
    # Reserve pool must end up fully restored to initial amount
    assert dfrr_res.final_reserved_pool == ex.reserved_pool


def test_dfrr_resource_accounting_invariant():
    """Verifies that Total = Alloc + Normal + Reserved holds at all points."""
    ex = PRELOADED_EXAMPLES["F: DFRR Research Scenario (Reserve Pool Unblocks System)"]
    dfrr_res = run_dfrr_simulation(
        allocation=ex.allocation,
        maximum=ex.maximum,
        available_normal=ex.available,
        reserved_pool=ex.reserved_pool
    )

    total = dfrr_res.total_resources
    for event in dfrr_res.events:
        # Sum of current allocated + normal_available + reserved_pool must match total
        for j in range(len(total)):
            calc = event.allocated_total[j] + event.normal_available[j] + event.reserved_pool[j]
            assert calc == total[j], f"Invariant violated at step {event.step} on R{j}"


def test_dfrr_stall_when_reserve_pool_insufficient():
    """When reserve pool is zero or too small, DFRR detects stall without crash."""
    ex = PRELOADED_EXAMPLES["F: DFRR Research Scenario (Reserve Pool Unblocks System)"]

    # With reserved pool [0, 0], DFRR cannot unblock P0
    dfrr_res = run_dfrr_simulation(
        allocation=ex.allocation,
        maximum=ex.maximum,
        available_normal=ex.available,
        reserved_pool=[0, 0]
    )

    assert dfrr_res.is_successful is False
    assert len(dfrr_res.unfinished_processes) == 3
    assert dfrr_res.reserved_pool_invocations == 0


def test_dfrr_total_mismatch_raises_error():
    """Passing an inconsistent total_resources vector raises ValueError."""
    alloc = [[1, 0], [0, 1]]
    maximum = [[2, 1], [1, 2]]
    avail = [1, 1]
    res_pool = [1, 1]
    # Sum alloc = [1, 1]. Total should be [3, 3].
    with pytest.raises(ValueError, match="Accounting Invariant Mismatch"):
        run_dfrr_simulation(
            alloc, maximum, avail, res_pool, total_resources=[99, 99]
        )
