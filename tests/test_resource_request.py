"""
Unit tests for Resource-Request Algorithm.
Covers Request <= Need check, Request <= Available check, tentative state evaluation,
granting safe requests, and rollback correctness for unsafe / invalid requests.
"""

import pytest
import copy
from algorithms.resource_request import evaluate_resource_request
from utils.examples import PRELOADED_EXAMPLES


def test_request_granted_safe():
    """Example C: P1 requests [0, 0, 1] from Example A, which is granted."""
    ex = PRELOADED_EXAMPLES["A: Safe State (SLA-1 / SLA-2 Official Sample)"]

    orig_alloc = copy.deepcopy(ex.allocation)
    orig_avail = copy.deepcopy(ex.available)
    orig_max = copy.deepcopy(ex.maximum)

    result = evaluate_resource_request(
        allocation=ex.allocation,
        maximum=ex.maximum,
        available=ex.available,
        process_id=1,
        request_vector=[0, 0, 1]
    )

    assert result.is_granted is True
    assert result.status == "GRANTED"
    assert result.resulting_available == [1, 1, 0]
    assert result.resulting_allocation[1] == [1, 1, 1]
    assert result.resulting_need[1] == [0, 1, 1]

    # Verify original matrices passed were not modified in place
    assert ex.allocation == orig_alloc
    assert ex.available == orig_avail


def test_request_denied_exceeds_need():
    """Example D: P0 requests [2, 0, 0], exceeding its Need [1, 1, 0]."""
    ex = PRELOADED_EXAMPLES["A: Safe State (SLA-1 / SLA-2 Official Sample)"]

    result = evaluate_resource_request(
        allocation=ex.allocation,
        maximum=ex.maximum,
        available=ex.available,
        process_id=0,
        request_vector=[2, 0, 0]
    )

    assert result.is_granted is False
    assert result.status == "DENIED_EXCEEDS_NEED"
    assert "exceeds its declared remaining Need" in result.message
    # Resulting matrices equal original
    assert result.resulting_available == ex.available
    assert result.resulting_allocation == ex.allocation


def test_request_must_wait_insufficient_available():
    """Example E: P1 requests [0, 1, 2], exceeding Available [1, 1, 1]."""
    ex = PRELOADED_EXAMPLES["A: Safe State (SLA-1 / SLA-2 Official Sample)"]

    result = evaluate_resource_request(
        allocation=ex.allocation,
        maximum=ex.maximum,
        available=ex.available,
        process_id=1,
        request_vector=[0, 1, 2]
    )

    assert result.is_granted is False
    assert result.status == "WAIT_INSUFFICIENT_AVAILABLE"
    assert "only 1 units are currently available" in result.message
    assert result.resulting_available == ex.available
    assert result.resulting_allocation == ex.allocation


def test_request_denied_due_to_unsafe_tentative_state():
    """
    Test request that satisfies Need and Available, but causes tentative state to become UNSAFE.
    Rollback must keep original state intact.
    """
    ex = PRELOADED_EXAMPLES["A: Safe State (SLA-1 / SLA-2 Official Sample)"]
    # If P0 requests its full need [1, 1, 0]:
    # Available becomes [0, 0, 1].
    # Then P0 holds [2, 1, 1], its need is [0, 0, 0].
    # Wait, if P0 need is [0,0,0], P0 can finish immediately.
    # What if P2 requests [1, 0, 1]?
    # Available becomes [0, 1, 0]. P2 need becomes [0, 0, 0], finishes, Work becomes [1, 2, 1].
    # Let's test a case where request takes all free resources such that no process has Need <= Work.
    alloc = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2]
    ]
    maximum = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2]
    ]
    available = [3, 3, 2]

    # Process 0 requests [0, 2, 0].
    # Need[0] is [7, 4, 3]. Request [0, 2, 0] <= Need and <= Available.
    # Tentative Available becomes [3, 1, 2].
    # Tentative Alloc[0] = [0, 3, 0], Need[0] = [7, 2, 3].
    # Can P1 run? Need[1] is [1, 2, 2]. For R1: Need is 2 > Work 1!
    # Can P2 run? Need[2] is [6, 0, 0] > Work 3!
    # Can P0 run? Need[0] is [7, 2, 3] > Work 3!
    # No process can run! Tentative state is UNSAFE!
    result = evaluate_resource_request(
        allocation=alloc,
        maximum=maximum,
        available=available,
        process_id=0,
        request_vector=[0, 2, 0]
    )

    assert result.is_granted is False
    assert result.status == "DENIED_UNSAFE"
    assert "UNSAFE STATE" in result.message
    # Verified rollback: resulting equals original
    assert result.resulting_available == available
    assert result.resulting_allocation == alloc
