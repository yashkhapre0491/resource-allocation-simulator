"""
Resource-Request Algorithm Engine
Implements the tentative allocation, safety testing, and rollback mechanism
for dynamic resource requests under Banker's Algorithm.
"""

from typing import List, Tuple, Dict, Any, Optional
import copy
from algorithms.banker import compute_need_matrix, run_safety_algorithm, SafetyCheckResult
from utils.validation import validate_resource_request


class ResourceRequestResult:
    """Result of evaluating an OS resource request."""
    def __init__(
        self,
        process_id: int,
        request_vector: List[int],
        status: str,
        is_granted: bool,
        message: str,
        educational_explanation: str,
        original_available: List[int],
        original_allocation: List[List[int]],
        original_need: List[List[int]],
        resulting_available: List[int],
        resulting_allocation: List[List[int]],
        resulting_need: List[List[int]],
        tentative_safety_result: Optional[SafetyCheckResult] = None
    ):
        self.process_id = process_id
        self.request_vector = request_vector
        self.status = status  # 'GRANTED', 'DENIED_EXCEEDS_NEED', 'MUST_WAIT_INSUFFICIENT_AVAILABLE', 'DENIED_UNSAFE'
        self.is_granted = is_granted
        self.message = message
        self.educational_explanation = educational_explanation
        self.original_available = original_available
        self.original_allocation = original_allocation
        self.original_need = original_need
        self.resulting_available = resulting_available
        self.resulting_allocation = resulting_allocation
        self.resulting_need = resulting_need
        self.tentative_safety_result = tentative_safety_result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "process": f"P{self.process_id}",
            "request": str(self.request_vector),
            "status": self.status,
            "granted": "Yes" if self.is_granted else "No",
            "message": self.message,
            "safe_sequence": self.tentative_safety_result.safe_sequence_str if self.tentative_safety_result else "N/A"
        }


def evaluate_resource_request(
    allocation: List[List[int]],
    maximum: List[List[int]],
    available: List[int],
    process_id: int,
    request_vector: List[int]
) -> ResourceRequestResult:
    """
    Evaluates a resource request vector for process process_id.

    Algorithm:
      1. Verify Request <= Need[process_id]. If false, DENIED (exceeded maximum claim).
      2. Verify Request <= Available. If false, MUST WAIT (insufficient resources currently free).
      3. Tentatively allocate:
           Available' = Available - Request
           Allocation'[process_id] = Allocation[process_id] + Request
           Need'[process_id] = Need[process_id] - Request
      4. Run safety algorithm on tentative state.
      5. If Safe:
           Grant request. State changes become effective.
         If Unsafe:
           Roll back changes. Restore original state. Process must wait.
    """
    n = len(allocation)
    m = len(available)

    if process_id < 0 or process_id >= n:
        raise ValueError(f"Invalid process index P{process_id}; system has {n} processes (P0 to P{n-1}).")

    # Compute current Need
    need = compute_need_matrix(allocation, maximum)

    # Perform Rule Checks
    is_eligible_for_test, status_code, validation_msg = validate_resource_request(
        process_id=process_id,
        request=request_vector,
        need_row=need[process_id],
        available_vector=available
    )

    if not is_eligible_for_test:
        edu_expl = ""
        if status_code == "DENIED_EXCEEDS_NEED":
            edu_expl = (
                f"Process P{process_id} requested resources exceeding its declared maximum claim minus current allocation. "
                "Operating system rule violation: A process cannot claim more resources than its declared Maximum requirement."
            )
        elif status_code == "WAIT_INSUFFICIENT_AVAILABLE":
            edu_expl = (
                f"Current available resources {available} cannot satisfy request {request_vector}. "
                f"Process P{process_id} must enter a waiting queue until executing processes release resources."
            )
        else:
            edu_expl = f"Request validation failed: {validation_msg}"

        return ResourceRequestResult(
            process_id=process_id,
            request_vector=list(request_vector),
            status=status_code,
            is_granted=False,
            message=validation_msg,
            educational_explanation=edu_expl,
            original_available=copy.deepcopy(available),
            original_allocation=copy.deepcopy(allocation),
            original_need=copy.deepcopy(need),
            resulting_available=copy.deepcopy(available),
            resulting_allocation=copy.deepcopy(allocation),
            resulting_need=copy.deepcopy(need),
            tentative_safety_result=None
        )

    # Tentative allocation (working copies)
    tentative_available = [available[j] - request_vector[j] for j in range(m)]
    tentative_allocation = copy.deepcopy(allocation)
    for j in range(m):
        tentative_allocation[process_id][j] += request_vector[j]

    tentative_maximum = copy.deepcopy(maximum)
    tentative_need = compute_need_matrix(tentative_allocation, tentative_maximum)

    # Run safety algorithm on tentative state
    safety_result = run_safety_algorithm(
        allocation=tentative_allocation,
        maximum=tentative_maximum,
        available=tentative_available,
        compute_all_sequences=True
    )

    if safety_result.is_safe:
        # Request is GRANTED
        msg = f"Request GRANTED for P{process_id}: Tentative state is SAFE."
        edu_expl = (
            f"The operating system tentatively deducted {request_vector} from Available and allocated it to P{process_id}. "
            f"The resulting system state is confirmed SAFE with safe execution sequence: {safety_result.safe_sequence_str}. "
            "Because a safe sequence exists, deadlock avoidance guarantees no deadlocks will occur, so the allocation is permanently granted."
        )
        return ResourceRequestResult(
            process_id=process_id,
            request_vector=list(request_vector),
            status="GRANTED",
            is_granted=True,
            message=msg,
            educational_explanation=edu_expl,
            original_available=copy.deepcopy(available),
            original_allocation=copy.deepcopy(allocation),
            original_need=copy.deepcopy(need),
            resulting_available=tentative_available,
            resulting_allocation=tentative_allocation,
            resulting_need=tentative_need,
            tentative_safety_result=safety_result
        )
    else:
        # Request is DENIED / ROLLED BACK
        msg = f"Request DENIED for P{process_id}: Granting this request leads to an UNSAFE STATE."
        edu_expl = (
            f"The operating system simulated allocating {request_vector} to P{process_id}. "
            f"However, in the tentative state, remaining free resources {tentative_available} were insufficient "
            f"to guarantee completion of remaining processes ({['P' + str(p) for p in safety_result.unfinished_processes]}). "
            "To prevent potential deadlock, the tentative allocation is rolled back completely. Original state is preserved."
        )
        return ResourceRequestResult(
            process_id=process_id,
            request_vector=list(request_vector),
            status="DENIED_UNSAFE",
            is_granted=False,
            message=msg,
            educational_explanation=edu_expl,
            original_available=copy.deepcopy(available),
            original_allocation=copy.deepcopy(allocation),
            original_need=copy.deepcopy(need),
            resulting_available=copy.deepcopy(available),
            resulting_allocation=copy.deepcopy(allocation),
            resulting_need=copy.deepcopy(need),
            tentative_safety_result=safety_result
        )
