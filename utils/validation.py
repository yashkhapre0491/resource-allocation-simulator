"""
Module M1: Input Validation
Implements validation rules V1 through V7 as specified in academic project SLA-2 specifications.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np


class ValidationError(Exception):
    """Raised when input matrices or vectors fail consistency checks."""
    pass


class ValidationResult:
    """Encapsulates validation findings, errors, and warnings."""
    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None, warnings: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __repr__(self) -> str:
        return f"ValidationResult(is_valid={self.is_valid}, errors={len(self.errors)}, warnings={len(self.warnings)})"


def validate_system_state(
    n: int,
    m: int,
    allocation: Any,
    maximum: Any,
    available: Any,
    min_procs: int = 1,
    max_procs: int = 10,
    min_res: int = 1,
    max_res: int = 10,
    check_v6: bool = True
) -> ValidationResult:
    """
    Validates the complete system state against rules V1 - V7:
      V1: Process count n and Resource count m are integers within allowed range.
      V2: Every matrix and vector entry is a non-negative integer (>= 0).
      V3: Allocation and Maximum are n x m; Available has length m.
      V4: No entry is null, empty, NaN, or non-integer.
      V5: Allocation[i][j] <= Maximum[i][j] for all i in [0..n-1] and j in [0..m-1].
      V6: Maximum[i][j] <= TotalInstances[j] where TotalInstances[j] = sum(Allocation[:][j]) + Available[j].
      V7: Need[i][j] >= 0 (defensive invariant check).

    Returns:
        ValidationResult: object indicating valid status with detailed messages.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Rule V1: Process count and Resource count
    if not isinstance(n, (int, np.integer)) or n < min_procs or n > max_procs:
        errors.append(f"V1: Number of processes (n={n}) must be a whole number between {min_procs} and {max_procs}.")
    if not isinstance(m, (int, np.integer)) or m < min_res or m > max_res:
        errors.append(f"V1: Number of resource types (m={m}) must be a whole number between {min_res} and {max_res}.")

    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # Convert to standard python lists/numpy arrays for safe inspection
    try:
        alloc_arr = np.array(allocation, dtype=float)
        max_arr = np.array(maximum, dtype=float)
        avail_arr = np.array(available, dtype=float)
    except Exception as e:
        errors.append(f"V4: Malformed input data could not be parsed as numeric arrays: {str(e)}")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # Rule V3: Dimensions
    if alloc_arr.shape != (n, m):
        errors.append(f"V3: Allocation matrix dimensions {alloc_arr.shape} do not match expected {n} x {m}.")
    if max_arr.shape != (n, m):
        errors.append(f"V3: Maximum matrix dimensions {max_arr.shape} do not match expected {n} x {m}.")
    if avail_arr.shape != (m,) and avail_arr.shape != (1, m):
        errors.append(f"V3: Available vector dimensions {avail_arr.shape} do not match expected length {m}.")
    else:
        avail_arr = avail_arr.flatten()

    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # Rule V2 & V4: Non-negative integers, no NaNs
    if np.isnan(alloc_arr).any() or np.isnan(max_arr).any() or np.isnan(avail_arr).any():
        errors.append("V4: Missing, blank, or NaN values detected in matrix/vector cells.")

    if not np.all(alloc_arr == np.floor(alloc_arr)):
        errors.append("V2: All entries in Allocation matrix must be integers.")
    if not np.all(max_arr == np.floor(max_arr)):
        errors.append("V2: All entries in Maximum matrix must be integers.")
    if not np.all(avail_arr == np.floor(avail_arr)):
        errors.append("V2: All entries in Available vector must be integers.")

    if (alloc_arr < 0).any():
        errors.append("V2: Values must be non-negative integers; negative entries found in Allocation matrix.")
    if (max_arr < 0).any():
        errors.append("V2: Values must be non-negative integers; negative entries found in Maximum matrix.")
    if (avail_arr < 0).any():
        errors.append("V2: Values must be non-negative integers; negative entries found in Available vector.")

    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # Convert to pure integers
    alloc_int = alloc_arr.astype(int)
    max_int = max_arr.astype(int)
    avail_int = avail_arr.astype(int)

    # Rule V5: Allocation[i][j] <= Maximum[i][j]
    for i in range(n):
        for j in range(m):
            if alloc_int[i][j] > max_int[i][j]:
                errors.append(
                    f"V5: Allocation exceeds Maximum for P{i}, R{j} "
                    f"(Allocation={alloc_int[i][j]} > Maximum={max_int[i][j]}). "
                    f"Process cannot hold more resources than its declared maximum."
                )

    # Rule V6: Maximum[i][j] <= Total system instances
    # Total instances of resource j in system = sum of all allocations for j + currently available instances of j
    total_instances = np.sum(alloc_int, axis=0) + avail_int
    if check_v6:
        for i in range(n):
            for j in range(m):
                if max_int[i][j] > total_instances[j]:
                    errors.append(
                        f"V6: Maximum claim of P{i} for R{j} ({max_int[i][j]}) exceeds total system instances "
                        f"({total_instances[j]} = {np.sum(alloc_int[:, j])} allocated + {avail_int[j]} available). "
                        f"Process could never finish even if all other processes completed."
                    )

    # Rule V7: Need[i][j] >= 0
    need_int = max_int - alloc_int
    if (need_int < 0).any():
        errors.append("V7: Internal defensive check failed: Negative Need detected after calculation.")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


def validate_resource_request(
    process_id: int,
    request: List[int],
    need_row: List[int],
    available_vector: List[int]
) -> Tuple[bool, str, str]:
    """
    Validates a resource request vector against:
      1. Non-negativity and dimensions.
      2. Condition 1: Request[j] <= Need[i][j] for all j.
      3. Condition 2: Request[j] <= Available[j] for all j.

    Returns:
        (is_eligible_for_test, status_code, message)
        status_code in ['VALID_FOR_TEST', 'ERR_DIM', 'ERR_NEGATIVE', 'DENIED_EXCEEDS_NEED', 'WAIT_INSUFFICIENT_AVAILABLE']
    """
    m = len(available_vector)
    if len(request) != m:
        return False, "ERR_DIM", f"Request dimension ({len(request)}) does not match number of resource types ({m})."

    for j, val in enumerate(request):
        if not isinstance(val, (int, np.integer)) or val < 0:
            return False, "ERR_NEGATIVE", f"Request for R{j} must be a non-negative integer (received {val})."

    # Condition 1: Request <= Need
    for j in range(m):
        if request[j] > need_row[j]:
            return (
                False,
                "DENIED_EXCEEDS_NEED",
                f"Denied: Process P{process_id} requested {request[j]} units of R{j}, "
                f"which exceeds its declared remaining Need of {need_row[j]} units. "
                f"(Process has exceeded its maximum claim)."
            )

    # Condition 2: Request <= Available
    for j in range(m):
        if request[j] > available_vector[j]:
            return (
                False,
                "WAIT_INSUFFICIENT_AVAILABLE",
                f"Must Wait: Process P{process_id} requested {request[j]} units of R{j}, "
                f"but only {available_vector[j]} units are currently available. "
                f"Process must wait until resources are released by other processes."
            )

    return True, "VALID_FOR_TEST", "Request satisfies Need and Available limits; ready for tentative safety check."
