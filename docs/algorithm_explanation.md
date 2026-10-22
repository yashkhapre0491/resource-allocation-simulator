# Algorithm Specification: Banker's Algorithm & Resource-Request Evaluation

**Project**: Resource Allocation Simulator: Deadlock Avoidance Using Banker's Algorithm  
**Course**: Operating Systems | Second Year Computer Engineering (SYCM3, Semester III)  
**Institution**: Shah & Anchor Kutchhi Engineering College, Chembur, Mumbai  
**Authors**: Yash Khapre (PRN 125BTCM1149) & Aman Kumar (PRN 125BTCM1092)  
**Faculty Guide**: Mrs. Vaishali Kosambkar  

---

## 1. Mathematical Formalism

Let:
- $n$: number of active processes in the system, indexed $i \in \{0, 1, \dots, n-1\}$.
- $m$: number of distinct resource types, indexed $j \in \{0, 1, \dots, m-1\}$.
- $\text{Available} \in \mathbb{N}^m$: vector where $\text{Available}[j]$ is the number of free instances of resource type $R_j$.
- $\text{Allocation} \in \mathbb{N}^{n \times m}$: matrix where $\text{Allocation}[i][j]$ is the number of instances of resource $R_j$ currently allocated to process $P_i$.
- $\text{Maximum} \in \mathbb{N}^{n \times m}$: matrix where $\text{Maximum}[i][j]$ is the maximum number of instances of resource $R_j$ process $P_i$ may claim.
- $\text{Need} \in \mathbb{N}^{n \times m}$: derived matrix representing the remaining instances of resource $R_j$ required by process $P_i$ to complete its execution:
  $$\text{Need}[i][j] = \text{Maximum}[i][j] - \text{Allocation}[i][j]$$

### Conservation & Consistency Invariants:
1. **Bounded Claim**: $\forall i \in [0, n-1], \forall j \in [0, m-1]: 0 \le \text{Allocation}[i][j] \le \text{Maximum}[i][j]$.
2. **System Capacity**: Total instances of resource $R_j$ in the computer system:
   $$\text{Total}[j] = \sum_{i=0}^{n-1} \text{Allocation}[i][j] + \text{Available}[j]$$
   Every process's maximum claim cannot exceed system capacity: $\text{Maximum}[i][j] \le \text{Total}[j]$.

---

## 2. Banker's Safety Algorithm

The safety algorithm determines whether the current resource allocation state is **SAFE** (i.e., there exists at least one order of execution in which all processes can satisfy their maximum claims and terminate).

### Pseudocode (Conforming to SLA-2 Table 16):

```
FUNCTION isEligible(i, Need, Work, m, Finish):
    IF Finish[i] == TRUE THEN
        RETURN FALSE
    FOR j <- 0 TO m - 1 DO:
        IF Need[i][j] > Work[j] THEN
            RETURN FALSE  // A shortage in any resource disqualifies Pi
    RETURN TRUE

FUNCTION safetyCheck(n, m, Allocation, Maximum, Available):
    Need <- computeNeed(Allocation, Maximum)
    Work <- copy(Available)
    Finish <- array of size n filled with FALSE
    SafeSequence <- empty list

    LOOP:
        chosen <- -1
        FOR i <- 0 TO n - 1 DO:
            comparisons <- comparisons + 1
            IF isEligible(i, Need, Work, m, Finish) THEN
                chosen <- i
                BREAK  // Deterministic lowest-index tie-breaking rule

        IF chosen == -1 THEN
            EXIT LOOP  // Stalled: No eligible unfinished process remains

        // Process 'chosen' is assumed to run, complete, and release its held resources
        FOR j <- 0 TO m - 1 DO:
            Work[j] <- Work[j] + Allocation[chosen][j]
        Finish[chosen] <- TRUE
        SafeSequence.append(chosen)

        IF all Finish == TRUE THEN
            EXIT LOOP

    is_safe <- (all Finish == TRUE)
    RETURN is_safe, SafeSequence, Work, comparisons
```

### Deterministic Tie-Breaking (Lowest Index First):
When multiple processes are simultaneously eligible ($\text{Need}[i] \le \text{Work}$), our engine prioritizes the lowest process index $i$. While different tie-breaking rules can produce different valid permutations of the safe sequence, they **never change the safety verdict** (whether the system is safe or unsafe).

---

## 3. Step-by-Step Worked Execution (SLA-1 / SLA-2 Official Sample)

Given $n=3$ processes ($P_0, P_1, P_2$) and $m=3$ resources ($R_1, R_2, R_3$):

$$\text{Allocation} = \begin{pmatrix} 1 & 0 & 1 \\ 1 & 1 & 0 \\ 1 & 1 & 1 \end{pmatrix}, \quad \text{Maximum} = \begin{pmatrix} 2 & 1 & 1 \\ 1 & 2 & 2 \\ 2 & 1 & 2 \end{pmatrix}, \quad \text{Available} = \begin{pmatrix} 1 & 1 & 1 \end{pmatrix}$$

### Step A: Need Matrix Calculation
$$\text{Need} = \text{Maximum} - \text{Allocation} = \begin{pmatrix} 2-1 & 1-0 & 1-1 \\ 1-1 & 2-1 & 2-0 \\ 2-1 & 1-1 & 2-1 \end{pmatrix} = \begin{pmatrix} 1 & 1 & 0 \\ 0 & 1 & 2 \\ 1 & 0 & 1 \end{pmatrix}$$

### Step B: Execution Trace
| Step | Candidate | Need$[i]$ | Work (Before) | Need $\le$ Work? | Action / Release | Work (After) | Finish Array | Safe Sequence |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | — | — | $(1, 1, 1)$ | Initial Setup | Work = Available | $(1, 1, 1)$ | `[F, F, F]` | `[]` |
| **1** | $P_0$ | $(1, 1, 0)$ | $(1, 1, 1)$ | **Yes** ($1 \le 1, 1 \le 1, 0 \le 1$) | $P_0$ completes; releases $(1,0,1)$ | $(2, 1, 2)$ | `[T, F, F]` | $P_0$ |
| **2** | $P_1$ | $(0, 1, 2)$ | $(2, 1, 2)$ | **Yes** ($0 \le 2, 1 \le 1, 2 \le 2$) | $P_1$ completes; releases $(1,1,0)$ | $(3, 2, 2)$ | `[T, T, F]` | $P_0 \to P_1$ |
| **3** | $P_2$ | $(1, 0, 1)$ | $(3, 2, 2)$ | **Yes** ($1 \le 3, 0 \le 2, 1 \le 2$) | $P_2$ completes; releases $(1,1,1)$ | $(4, 3, 3)$ | `[T, T, T]` | $P_0 \to P_1 \to P_2$ |
| **4** | — | — | $(4, 3, 3)$ | All Finish = True | **Algorithm Terminates: SAFE** | $(4, 3, 3)$ | `[T, T, T]` | **SAFE** |

**Final Resource Conservation Verification**:
$$\text{Final Work} = (4, 3, 3) = \sum \text{Allocation} + \text{Initial Available} = (3, 2, 2) + (1, 1, 1) = (4, 3, 3)$$

---

## 4. Resource-Request Algorithm

When a process $P_i$ makes a request vector $\text{Request}_i$:
1. **Rule 1**: If $\exists j: \text{Request}_i[j] > \text{Need}[i][j]$, raise an error (`DENIED_EXCEEDS_NEED`). The process has exceeded its maximum claim.
2. **Rule 2**: If $\exists j: \text{Request}_i[j] > \text{Available}[j]$, process $P_i$ must wait (`MUST_WAIT_INSUFFICIENT_AVAILABLE`).
3. **Tentative Allocation**:
   $$\text{Available}' = \text{Available} - \text{Request}_i$$
   $$\text{Allocation}'[i] = \text{Allocation}[i] + \text{Request}_i$$
   $$\text{Need}'[i] = \text{Need}[i] - \text{Request}_i$$
4. **Safety Verification**:
   Execute the Safety Algorithm on the tentative state $(\text{Available}', \text{Allocation}', \text{Need}')$.
   - **If Safe**: Grant the request. The tentative state becomes the permanent system state.
   - **If Unsafe**: Deny the request and **roll back** the tentative modifications. The original state is completely restored, and $P_i$ is placed in a waiting queue.

---

## 5. Computational Complexity Analysis

| Operation | Time Complexity | Auxiliary Space Complexity | Theoretical Reasoning |
| :--- | :---: | :---: | :--- |
| **Need Matrix Calculation** | $O(n \cdot m)$ | $O(n \cdot m)$ | Matrix subtraction for each of the $n \times m$ cells. |
| **Safety Check (Worst-case)** | $O(n^2 \cdot m)$ | $O(n + m)$ | Up to $n$ passes; each pass scans up to $n$ processes; each comparison checks $m$ resource types. Total comparisons: $\frac{n(n+1)}{2} \cdot m$. |
| **Resource Request Evaluation**| $O(n^2 \cdot m)$ | $O(n \cdot m)$ | Involves vector checks $O(m)$ plus one full safety check $O(n^2 \cdot m)$. |
| **DFS All Safe Sequences** | $O(n! \cdot m)$ | $O(n)$ | Backtracking tree exploring all valid topological permutations. |
