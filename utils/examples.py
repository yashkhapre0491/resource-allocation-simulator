"""
Preloaded Academic Examples
Includes all scenarios A through F, covering SLA-1, SLA-2, and textbook benchmarks.
"""

from typing import Dict, Any, List


class ScenarioExample:
    """Encapsulates a predefined educational scenario."""
    def __init__(
        self,
        name: str,
        category: str,
        description: str,
        n: int,
        m: int,
        allocation: List[List[int]],
        maximum: List[List[int]],
        available: List[int],
        expected_status: str,
        expected_safe_sequence: str,
        explanation: str,
        sample_request_pid: int = 0,
        sample_request_vector: List[int] = None,
        reserved_pool: List[int] = None
    ):
        self.name = name
        self.category = category
        self.description = description
        self.n = n
        self.m = m
        self.allocation = allocation
        self.maximum = maximum
        self.available = available
        self.expected_status = expected_status
        self.expected_safe_sequence = expected_safe_sequence
        self.explanation = explanation
        self.sample_request_pid = sample_request_pid
        self.sample_request_vector = sample_request_vector or [0] * m
        self.reserved_pool = reserved_pool or [0] * m


PRELOADED_EXAMPLES: Dict[str, ScenarioExample] = {
    "A: Safe State (SLA-1 / SLA-2 Official Sample)": ScenarioExample(
        name="Example A: Safe State (SLA-1 / SLA-2 Official Sample)",
        category="Safe State",
        description="The primary 3-process 3-resource case study from college SLA-1 & SLA-2 reports.",
        n=3,
        m=3,
        allocation=[
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1]
        ],
        maximum=[
            [2, 1, 1],
            [1, 2, 2],
            [2, 1, 2]
        ],
        available=[1, 1, 1],
        expected_status="SAFE",
        expected_safe_sequence="P0 -> P1 -> P2",
        explanation=(
            "Calculated Need: P0=(1,1,0), P1=(0,1,2), P2=(1,0,1).\n"
            "At start, P1 cannot run (Need R3=2 > Work R3=1). P0 has Need <= Work (1,1,1). "
            "P0 finishes, Work becomes (2,1,2). P1 can now finish, Work becomes (3,2,2). "
            "P2 finishes, Work becomes (4,3,3). Final Work equals total physical resources."
        ),
        sample_request_pid=1,
        sample_request_vector=[0, 0, 1],
        reserved_pool=[1, 1, 1]
    ),

    "A2: Safe State (Silberschatz 5-Process Benchmark)": ScenarioExample(
        name="Example A2: Safe State (Silberschatz Standard Benchmark)",
        category="Safe State",
        description="Classic Operating System Concepts (Silberschatz/Galvin/Gagne) 5-process 3-resource benchmark.",
        n=5,
        m=3,
        allocation=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2]
        ],
        maximum=[
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3]
        ],
        available=[3, 3, 2],
        expected_status="SAFE",
        expected_safe_sequence="P1 -> P3 -> P0 -> P2 -> P4 (or P1 -> P3 -> P4 -> P0 -> P2)",
        explanation=(
            "Total resources: (10, 5, 7). Initial Work = (3, 3, 2).\n"
            "Need matrix: P0=(7,4,3), P1=(1,2,2), P2=(6,0,0), P3=(0,1,1), P4=(4,3,1).\n"
            "Under deterministic lowest-index tie-breaking: P1 finishes first (Work->5,3,2), "
            "then P3 finishes (Work->7,4,3). P0 can now finish (Need 7,4,3 <= Work 7,4,3), "
            "followed by P2 and P4. Multiple safe sequences exist."
        ),
        sample_request_pid=1,
        sample_request_vector=[1, 0, 2],
        reserved_pool=[1, 1, 1]
    ),

    "B: Unsafe State (Zero Available Resources)": ScenarioExample(
        name="Example B: Unsafe State (Zero Available Resources - SLA-2 TC-04)",
        category="Unsafe State",
        description="The SLA-1 matrix with zero free resources (Available = [0, 0, 0]).",
        n=3,
        m=3,
        allocation=[
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1]
        ],
        maximum=[
            [2, 1, 1],
            [1, 2, 2],
            [2, 1, 2]
        ],
        available=[0, 0, 0],
        expected_status="UNSAFE",
        expected_safe_sequence="None (Immediate Stall)",
        explanation=(
            "Need matrix remains P0=(1,1,0), P1=(0,1,2), P2=(1,0,1).\n"
            "With Work = (0,0,0), every process has at least one positive Need component exceeding 0. "
            "No process can be started. The system is immediately deemed UNSAFE."
        ),
        sample_request_pid=0,
        sample_request_vector=[0, 0, 0],
        reserved_pool=[1, 1, 1]
    ),

    "B2: Unsafe State (Stall After Partial Progress - SLA-2 E7)": ScenarioExample(
        name="Example B2: Unsafe State (Stall After Partial Progress - SLA-2 E7)",
        category="Unsafe State",
        description="A scenario where the algorithm makes initial progress but subsequently stalls.",
        n=3,
        m=1,
        allocation=[
            [1],
            [1],
            [1]
        ],
        maximum=[
            [1],
            [3],
            [3]
        ],
        available=[0],
        expected_status="UNSAFE",
        expected_safe_sequence="Partial: P0 only",
        explanation=(
            "Need values: P0=0, P1=2, P2=2. Available = (0).\n"
            "P0 needs 0 <= 0, so P0 finishes and releases 1. Work becomes (1).\n"
            "Now P1 needs 2 and P2 needs 2. Neither can proceed with Work=1.\n"
            "System stalls. Unfinished processes: P1, P2. Verdict: UNSAFE."
        ),
        sample_request_pid=1,
        sample_request_vector=[1],
        reserved_pool=[1]
    ),

    "C: Request Granted Preserving Safety": ScenarioExample(
        name="Example C: Request Granted Preserving Safety",
        category="Resource Request",
        description="Process P1 requests [0, 0, 1] from SLA-1 sample state.",
        n=3,
        m=3,
        allocation=[
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1]
        ],
        maximum=[
            [2, 1, 1],
            [1, 2, 2],
            [2, 1, 2]
        ],
        available=[1, 1, 1],
        expected_status="GRANTED",
        expected_safe_sequence="P0 -> P1 -> P2",
        explanation=(
            "P1 requests [0, 0, 1].\n"
            "Condition 1: Request [0,0,1] <= Need P1 [0,1,2] -> Passed.\n"
            "Condition 2: Request [0,0,1] <= Available [1,1,1] -> Passed.\n"
            "Tentative State: Available becomes [1,1,0]. Allocation P1 becomes [1,1,1].\n"
            "Safety Check: P0 needs [1,1,0] <= [1,1,0], finishes, releases [1,0,1]. Work becomes [2,1,1].\n"
            "P1 needs [0,1,1] <= [2,1,1], finishes. P2 finishes. State remains SAFE. Request GRANTED."
        ),
        sample_request_pid=1,
        sample_request_vector=[0, 0, 1],
        reserved_pool=[1, 1, 1]
    ),

    "D: Request Denied (Exceeds Process Need)": ScenarioExample(
        name="Example D: Request Denied (Exceeds Process Need)",
        category="Resource Request",
        description="Process P0 requests [2, 0, 0], exceeding its declared remaining Need [1, 1, 0].",
        n=3,
        m=3,
        allocation=[
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1]
        ],
        maximum=[
            [2, 1, 1],
            [1, 2, 2],
            [2, 1, 2]
        ],
        available=[1, 1, 1],
        expected_status="DENIED_EXCEEDS_NEED",
        expected_safe_sequence="N/A",
        explanation=(
            "Process P0 declares Maximum [2, 1, 1] and already holds [1, 0, 1], giving Need = [1, 1, 0].\n"
            "If P0 requests [2, 0, 0], for R0: Request(2) > Need(1).\n"
            "Operating System Rule: An error is immediately raised because the process has exceeded its maximum claim."
        ),
        sample_request_pid=0,
        sample_request_vector=[2, 0, 0],
        reserved_pool=[1, 1, 1]
    ),

    "E: Request Must Wait (Insufficient Available)": ScenarioExample(
        name="Example E: Request Must Wait (Insufficient Available)",
        category="Resource Request",
        description="Process P1 requests [0, 1, 2], which is within its Need [0, 1, 2], but exceeds Available [1, 1, 1].",
        n=3,
        m=3,
        allocation=[
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1]
        ],
        maximum=[
            [2, 1, 1],
            [1, 2, 2],
            [2, 1, 2]
        ],
        available=[1, 1, 1],
        expected_status="MUST_WAIT_INSUFFICIENT_AVAILABLE",
        expected_safe_sequence="N/A",
        explanation=(
            "P1 requests [0, 1, 2].\n"
            "Need check: [0, 1, 2] <= [0, 1, 2] -> Pass.\n"
            "Available check: For R2, requested 2 units, but only 1 unit is available in the system.\n"
            "Operating System Rule: Process P1 must wait in the wait-queue until running processes release instances."
        ),
        sample_request_pid=1,
        sample_request_vector=[0, 1, 2],
        reserved_pool=[1, 1, 1]
    ),

    "F: DFRR Research Scenario (Reserve Pool Unblocks System)": ScenarioExample(
        name="Example F: DFRR Research Scenario (Reserve Pool Unblocks System)",
        category="Research Extension (DFRR)",
        description="A scenario where normal Banker's stalls (UNSAFE), but DFRR unblocks the bottleneck via reserved pool.",
        n=3,
        m=2,
        allocation=[
            [2, 1],
            [1, 2],
            [1, 1]
        ],
        maximum=[
            [4, 2],
            [2, 4],
            [3, 2]
        ],
        available=[0, 1],  # Normal available
        expected_status="DFRR_SUCCESSFUL",
        expected_safe_sequence="P0 -> P1 -> P2 (via DFRR)",
        explanation=(
            "Need matrix: P0=(2,1), P1=(1,2), P2=(2,1).\n"
            "Normal Available = (0, 1).\n"
            "Under traditional Banker's: No process can start because all need R0 >= 1 > Available(0). STALL / UNSAFE!\n"
            "Under DFRR with Reserved Pool = [2, 0]:\n"
            "Total physical resources = Allocated(4,4) + Normal(0,1) + Reserved(2,0) = (6,5).\n"
            "DFRR checks: P0 needs (2,1) <= Normal(0,1) + Reserved(2,0) = (2,1). Match!\n"
            "P0 borrows (2,0) from the reserved pool, completes, restores (2,0) to reserved pool, and releases its allocation (2,1) into Normal Available!\n"
            "Normal Available becomes (2,2). Now P1 and P2 complete smoothly! Deadlock prevented without full permutation re-computation."
        ),
        sample_request_pid=0,
        sample_request_vector=[0, 0],
        reserved_pool=[2, 0]
    )
}
