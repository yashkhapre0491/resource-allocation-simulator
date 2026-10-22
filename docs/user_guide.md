# Resource Allocation Simulator — User Guide

**Project**: Resource Allocation Simulator: Deadlock Avoidance Using Banker's Algorithm with Research-Based Resource Reservation  
**Course**: Operating Systems | Second Year Computer Engineering (SYCM3, Semester III, AY 2026–2027)  
**Institution**: Shah & Anchor Kutchhi Engineering College, Chembur, Mumbai  
**Authors**: Yash Khapre (PRN 125BTCM1149, Roll 25) & Aman Kumar (PRN 125BTCM1092, Roll 26)  
**Faculty Guide**: Mrs. Vaishali Kosambkar  

---

## 1. Introduction

The **Resource Allocation Simulator** is an interactive, browser-based learning and demonstration tool designed for Operating Systems coursework. It models the dynamic allocation of system resources among competing processes, enforces **deadlock avoidance** using Dijkstra's **Banker's Algorithm**, simulates on-demand **Resource Requests**, and demonstrates an experimental **Deadlock-Free Resource Reservation (DFRR)** prototype inspired by modern research.

---

## 2. Quick-Start Guide (Windows)

1. **Open PowerShell or Command Prompt** in the project directory:
   ```cmd
   cd c:\Users\Yash\Desktop\resource-allocation-simulator
   ```

2. **Run the batch script** (automated launch):
   ```cmd
   run_simulator.bat
   ```
   *Alternatively, launch via Python command:*
   ```cmd
   python -m streamlit run app.py
   ```

3. **Open your browser** to the local URL:
   `http://localhost:8501`

---

## 3. Simulator Modules & Walkthrough

The application features six dedicated modes accessible via the left sidebar:

### 3.1. 📊 System Setup & Need Matrix Calculation
- **Process and Resource Counts**: Set $n$ (1 to 10) and $m$ (1 to 10) and click **Reset / Apply Dimension Changes**.
- **Matrix Editors**:
  - **Allocation Matrix**: Current instances of each resource $R_j$ held by process $P_i$.
  - **Maximum Matrix**: Maximum instances $P_i$ can claim over its runtime.
  - **Available Vector**: Free, unallocated instances currently in the OS pool.
  - **Reserved Pool (DFRR)**: Safety reserve buffer for DFRR unblocking experiments.
- **Validation Engine**: Real-time checking against rules **V1 through V7** (range, non-negativity, dimension match, no NaNs, Allocation $\le$ Maximum, Maximum $\le$ Total Capacity).
- **Need Matrix Display**: Computed automatically as:
  $$\text{Need}[i][j] = \text{Maximum}[i][j] - \text{Allocation}[i][j]$$

### 3.2. 🛡️ Banker's Safety & Step Trace
- **Safe / Unsafe Verdict Badge**: Instant colored status banner:
  - 🟢 **SAFE STATE**: Displays deterministic safe sequence ($P_0 \to P_1 \to P_2$).
  - 🔴 **UNSAFE STATE**: Warns that no complete sequence can guarantee deadlock-free execution.
- **Interactive Stepper**:
  - Use **Previous Step**, **Next Step**, **Reset to Step 0**, or the **Step Slider** to inspect each step.
  - See Candidate Process, Work Vector Before, comparison results ($Pass / Fail$), Work Vector After release, and updated Finish flags.
- **Work Vector Growth Chart**: Interactive Plotly bar chart tracking available resources expanding as processes finish and return allocations.
- **Alternative Safe Sequences**: Backtracking engine enumerates all valid permutations for the current state (e.g., Example A reveals 4 valid sequences).

### 3.3. 🔄 Resource-Request Simulation
- Select a requesting process $P_i$ from the dropdown.
- Input the requested resource vector ($Req$).
- Click **Evaluate Resource Request**:
  - **Condition 1**: Checks if $Req \le \text{Need}[i]$. (Rejects with error if process exceeds maximum claim).
  - **Condition 2**: Checks if $Req \le \text{Available}$. (Sets status to **Wait** if free instances are insufficient).
  - **Condition 3**: Performs tentative allocation on working copies:
    $$Available' = Available - Req$$
    $$Allocation'[i] = Allocation[i] + Req$$
    $$Need'[i] = Need[i] - Req$$
  - Runs Safety Check on tentative state.
  - If SAFE: Grants request. User can optionally click **Permanently Apply Changes**.
  - If UNSAFE: Denies request and **rolls back** tentative changes, preserving the initial state.

### 3.4. 🔬 DFRR Research Extension
- Models the **Deadlock-Free Resource Reservation** technique from *Botlagunta, Agrawal & Rao (2022)*.
- Splits total physical capacity into:
  - **Allocated Resources**
  - **Normal Available Pool**
  - **Reserved Resource Pool**
- Invariant verified at every event:
  $$\text{Total}[j] = \text{Allocated}[j] + \text{Available}_{\text{norm}}[j] + \text{Reserved}[j]$$
- If normal resources cannot satisfy any process, DFRR loans from the reserved pool to unblock the candidate with the lowest deficit. The process completes, restores the reserved pool, and deposits its held allocation into normal available.
- Full event log documents each reservation, unblocking, and replenishment.

### 3.5. ⚖️ Side-by-Side Comparison
- Directly benchmarks **Traditional Banker's** vs **DFRR** across 20 iterations.
- Displays:
  - Execution time in microseconds ($\mu s$).
  - Number of eligibility checks.
  - Safety verdicts.
- Provides a comprehensive comparison matrix covering operating principles, overhead, and limitations.

### 3.6. 📚 Viva Guide & SDG Mapping
- Summarizes alignment with **SDG 9** (Industry, Innovation & Infrastructure) and **SDG 4** (Quality Education).
- Contains high-yield viva questions with textbook answers covering $O(n^2 m)$ complexity, tie-breaking independence, and unsafe vs. deadlock definitions.

---

## 4. Preloaded Academic Scenarios

Load any scenario via the sidebar dropdown:
- **Example A**: Official SLA-1 & SLA-2 sample ($P_0 \to P_1 \to P_2$).
- **Example A2**: Silberschatz 5-process benchmark ($P_1 \to P_3 \to P_0 \to P_2 \to P_4$).
- **Example B**: Zero available resources (immediate unsafe state).
- **Example B2**: Stall after partial progress ($P_0$ finishes, $P_1$ and $P_2$ stall).
- **Example C**: Request granted preserving safety ($P_1$ requests `[0, 0, 1]`).
- **Example D**: Request denied exceeding remaining Need ($P_0$ requests `[2, 0, 0]`).
- **Example E**: Request must wait due to insufficient Available ($P_1$ requests `[0, 1, 2]`).
- **Example F**: DFRR unblocking scenario where Banker's stalls, but reserved pool saves the system.
