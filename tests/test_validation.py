"""
Unit tests for Validation module (Rules V1 - V7 and Edge Cases E1 - E5, E10).
Corresponds to SLA-2 Table 14, Table 17, and Table 22.
"""

import pytest
from utils.validation import validate_system_state, validate_resource_request


def test_v1_invalid_process_and_resource_count():
    """E2 / TC-08: Check n=0, negative n, float n, and n > 10."""
    res = validate_system_state(
        n=0, m=3,
        allocation=[[]], maximum=[[]], available=[1, 1, 1]
    )
    assert not res.is_valid
    assert any("V1" in err for err in res.errors)

    res = validate_system_state(
        n=-2, m=3,
        allocation=[[]], maximum=[[]], available=[1, 1, 1]
    )
    assert not res.is_valid

    res = validate_system_state(
        n=11, m=3,
        allocation=[[0, 0, 0]] * 11, maximum=[[1, 1, 1]] * 11, available=[1, 1, 1]
    )
    assert not res.is_valid
    assert any("whole number between 1 and 10" in err for err in res.errors)


def test_v2_negative_values_rejected():
    """E1 / TC-07: Allocation P0 R1 = -1 is rejected."""
    alloc = [[-1, 0, 1], [1, 1, 0], [1, 1, 1]]
    maximum = [[2, 1, 1], [1, 2, 2], [2, 1, 2]]
    avail = [1, 1, 1]
    res = validate_system_state(n=3, m=3, allocation=alloc, maximum=maximum, available=avail)
    assert not res.is_valid
    assert any("V2: Values must be non-negative integers" in err for err in res.errors)


def test_v3_dimension_mismatch():
    """E3 / TC-09: Matrix dimensions do not match n x m."""
    alloc = [[1, 0, 1], [1, 1, 0], [1, 1, 1]]
    # Maximum has row with 2 elements instead of 3
    maximum = [[2, 1], [1, 2], [2, 1]]
    avail = [1, 1, 1]
    res = validate_system_state(n=3, m=3, allocation=alloc, maximum=maximum, available=avail)
    assert not res.is_valid
    assert any("V3" in err for err in res.errors)


def test_v4_nan_or_malformed_input():
    """E5 / TC-11: Blank cell, text or NaN entries."""
    alloc = [[float("nan"), 0, 1], [1, 1, 0], [1, 1, 1]]
    maximum = [[2, 1, 1], [1, 2, 2], [2, 1, 2]]
    avail = [1, 1, 1]
    res = validate_system_state(n=3, m=3, allocation=alloc, maximum=maximum, available=avail)
    assert not res.is_valid
    assert any("V4" in err for err in res.errors)


def test_v5_allocation_exceeds_maximum():
    """E4 / TC-10: P1 Allocation (2,1,0) exceeds Maximum (1,2,2) for R0."""
    alloc = [[1, 0, 1], [2, 1, 0], [1, 1, 1]]
    maximum = [[2, 1, 1], [1, 2, 2], [2, 1, 2]]
    avail = [1, 1, 1]
    res = validate_system_state(n=3, m=3, allocation=alloc, maximum=maximum, available=avail)
    assert not res.is_valid
    assert any("V5: Allocation exceeds Maximum for P1, R0" in err for err in res.errors)


def test_v6_maximum_exceeds_total_instances():
    """E10 / TC-12: Max P1 R2 = 5 while total R2 is only 3."""
    alloc = [[1, 0, 1], [1, 1, 0], [1, 1, 1]]
    # Total R1 = 0 + 1 + 1 + 1 (avail) = 3. Setting Max P1 R1 = 5 exceeds total system capacity!
    maximum = [[2, 1, 1], [1, 5, 2], [2, 1, 2]]
    avail = [1, 1, 1]
    res = validate_system_state(n=3, m=3, allocation=alloc, maximum=maximum, available=avail, check_v6=True)
    assert not res.is_valid
    assert any("V6: Maximum claim of P1 for R1" in err for err in res.errors)


def test_request_validation_conditions():
    """Tests request exceeding Need and exceeding Available."""
    need_row = [1, 1, 0]
    avail = [1, 1, 1]

    # Exceeds Need
    is_ok, code, msg = validate_resource_request(0, [2, 0, 0], need_row, avail)
    assert not is_ok
    assert code == "DENIED_EXCEEDS_NEED"

    # Exceeds Available
    is_ok, code, msg = validate_resource_request(0, [0, 1, 2], [0, 2, 3], avail)
    assert not is_ok
    assert code == "WAIT_INSUFFICIENT_AVAILABLE"

    # Valid
    is_ok, code, msg = validate_resource_request(0, [1, 0, 0], need_row, avail)
    assert is_ok
    assert code == "VALID_FOR_TEST"
