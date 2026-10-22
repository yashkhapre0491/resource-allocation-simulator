# Resource Allocation Simulator: Deadlock Avoidance Using Banker's Algorithm with Research-Based Resource Reservation

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![Pytest](https://img.shields.io/badge/Pytest-Passed%20(24%2F24)-success.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Academic Project Details
- **Project Title**: Resource Allocation Simulator – Deadlock Avoidance using Banker’s Algorithm
- **Course**: Operating System (Course Code: CSC303 / SLA-2)
- **Department**: Department of Computer Engineering
- **Institution**: Shah & Anchor Kutchhi Engineering College (Autonomous Institute Affiliated to University of Mumbai)
- **Class**: SYCM3 | **Semester**: III | **Academic Year**: 2026–2027
- **Students**:
  - **Yash Khapre** (PRN: `125BTCM1149`, Roll No: `25`)
  - **Aman Kumar** (PRN: `125BTCM1092`, Roll No: `26`)
- **Faculty Guide**: **Mrs. Vaishali Kosambkar**
- **SDG Mapping**:
  - **Primary**: SDG 9 — Industry, Innovation and Infrastructure
  - **Secondary**: SDG 4 — Quality Education

---

## 1. Project Overview & Problem Statement

In multitasking computer operating systems, multiple concurrently executing processes compete for a shared finite set of physical resources (such as CPU cores, memory pages, tape drives, printers, and disk I/O channels). If resources are allocated blindly without forward-looking safety checks, a circular dependency may form where every process waits for resources held by another process—a catastrophic condition known as **deadlock**.

This project provides a complete, modern, interactive **Resource Allocation Simulator** implementing:
1. **Dijkstra's Classic Banker's Algorithm** for centralized deadlock avoidance.
2. **On-Demand Resource-Request Simulation** with automated tentative state verification and safe rollback.
3. An experimental research-inspired extension: **Deadlock-Free Resource Reservation (DFRR)** based on *Botlagunta, Agrawal & Rao (2022)*.
4. **Step-by-step educational visualization**, execution timers, operation counters, and comprehensive automated test suites.

---

## 2. Key Objectives & Features

- **Input Validation Suite (Rules V1–V7)**: Enforces dimensions, non-negativity, numeric integrity, $\text{Allocation} \le \text{Maximum}$, and total capacity limits.
- **Automated Need Matrix Computation**: Automatically computes $\text{Need} = \text{Maximum} - \text{Allocation}$.
- **Safety Algorithm & Safe-Sequence Generation**:
  - Deterministic tie-breaking (lowest index first, conforming to SLA-2 specifications).
  - Highlighting of Work vector growth as completed processes release held allocations.
  - Backtracking DFS engine to discover and display **all alternative valid safe sequences**.
- **Interactive Stepper**: Step through algorithm execution with *Previous*, *Next*, *Reset*, and *Slider* controls.
- **Resource Request Engine**:
  - Validates $\text{Request} \le \text{Need}$ and $\text{Request} \le \text{Available}$.
  - Evaluates safety on a tentative state.
  - Demonstrates atomic grant or safe rollback.
- **DFRR Research Prototype**:
  - Models a two-tier resource architecture: Normal Available Pool + Reserved Pool.
  - Demonstrates how reserved buffers unblock stalled bottleneck processes.
- **Side-by-Side Comparison**: Live benchmarking (median execution time, comparisons, outcome) comparing Banker's Algorithm vs DFRR.
- **Preloaded Academic Library**: 1-click loading of scenarios **A through F** (including the official SLA sample and Silberschatz 5-process benchmark).

---

## 3. Technology Stack

- **Language**: Python 3.11+
- **Web Dashboard**: Streamlit
- **Data & Matrix Computations**: NumPy & Pandas
- **Interactive Visualizations**: Plotly Express & Plotly Graph Objects
- **Automated Testing Suite**: Pytest
- **Platform**: Cross-platform (optimized for Windows 10/11)

---

## 4. Project Folder Structure

```
resource-allocation-simulator/
├── app.py                     # Main interactive Streamlit web dashboard
├── algorithms/                # Core independent algorithm logic
│   ├── __init__.py
│   ├── banker.py              # Banker's safety algorithm & safe sequence generator
│   ├── resource_request.py    # Resource-request evaluation & rollback engine
│   └── dfrr.py                # Deadlock-Free Resource Reservation prototype
├── utils/                     # Supporting utilities and definitions
│   ├── __init__.py
│   ├── validation.py          # Input validation rules V1 through V7
│   ├── examples.py            # Preloaded academic scenarios A through F
│   └── metrics.py             # Performance counters, complexity & benchmarks
├── tests/                     # Comprehensive automated unit tests (24 tests)
│   ├── __init__.py
│   ├── test_banker.py         # Banker's safety checks (TC-01 to TC-06, TC-13)
│   ├── test_resource_request.py # Request evaluation & rollback correctness
│   ├── test_dfrr.py           # DFRR accounting & unblocking invariant tests
│   └── test_validation.py     # Validation rules V1-V7 & edge cases E1-E10
├── docs/                      # Academic reports & documentation
│   ├── user_guide.md          # User manual for students and faculty
│   ├── algorithm_explanation.md # Mathematical formulas & SLA worked sample
│   └── research_comparison.md # 5-paper synthesis & DFRR analysis
├── requirements.txt           # Python dependency specifications
├── run_simulator.bat          # 1-click Windows launcher batch script
└── README.md                  # Project overview and instructions
```

---

## 5. Installation & Execution Guide (Windows)

### Prerequisites:
- Windows 10/11 with Python 3.10+ installed.

### Option A: 1-Click Launch (Recommended for Windows)
Simply double-click:
```
run_simulator.bat
```
This batch file will automatically verify dependencies and open the application in your default web browser at `http://localhost:8501`.

### Option B: Manual Command Line Launch
1. Open PowerShell or Command Prompt in the project folder:
   ```powershell
   cd c:\Users\Yash\Desktop\resource-allocation-simulator
   ```

2. *(Optional)* Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install required packages:
   ```powershell
   pip install -r requirements.txt
   ```

4. Launch the Streamlit application:
   ```powershell
   streamlit run app.py
   ```

5. Open your browser to:
   ```
   http://localhost:8501
   ```

---

## 6. Running Automated Tests

The project includes 24 automated unit tests verifying input validation, edge cases, Banker's safety checking, resource-request rollback, and DFRR invariants.

Run all tests from the project root:
```powershell
python -m pytest tests -v
```

### Expected Output:
```
tests/test_banker.py::test_tc01_need_calculation PASSED
tests/test_banker.py::test_tc02_safe_state_sla_sample PASSED
tests/test_banker.py::test_tc03_resource_conservation PASSED
tests/test_banker.py::test_tc04_unsafe_no_eligible_process PASSED
tests/test_banker.py::test_tc05_unsafe_stall_after_progress PASSED
tests/test_banker.py::test_tc06_single_process_case PASSED
tests/test_banker.py::test_tc13_order_independence_of_verdict PASSED
tests/test_banker.py::test_multiple_valid_safe_sequences PASSED
tests/test_banker.py::test_silberschatz_benchmark PASSED
tests/test_dfrr.py::test_dfrr_unblocks_stalled_system PASSED
tests/test_dfrr.py::test_dfrr_resource_accounting_invariant PASSED
tests/test_dfrr.py::test_dfrr_stall_when_reserve_pool_insufficient PASSED
tests/test_dfrr.py::test_dfrr_total_mismatch_raises_error PASSED
tests/test_resource_request.py::test_request_granted_safe PASSED
tests/test_resource_request.py::test_request_denied_exceeds_need PASSED
tests/test_resource_request.py::test_request_must_wait_insufficient_available PASSED
tests/test_resource_request.py::test_request_denied_due_to_unsafe_tentative_state PASSED
tests/test_validation.py::test_v1_invalid_process_and_resource_count PASSED
tests/test_validation.py::test_v2_negative_values_rejected PASSED
tests/test_validation.py::test_v3_dimension_mismatch PASSED
tests/test_validation.py::test_v4_nan_or_malformed_input PASSED
tests/test_validation.py::test_v5_allocation_exceeds_maximum PASSED
tests/test_validation.py::test_v6_maximum_exceeds_total_instances PASSED
tests/test_validation.py::test_request_validation_conditions PASSED
============================== 24 passed in 0.30s ==============================
```

---

## 7. Example Execution Walkthrough (SLA-1 / SLA-2 Official Sample)

### Input Data:
- Processes: $P_0, P_1, P_2$ ($n=3$)
- Resources: $R_1, R_2, R_3$ ($m=3$)
- **Allocation Matrix**:
  $$P_0: [1, 0, 1], \quad P_1: [1, 1, 0], \quad P_2: [1, 1, 1]$$
- **Maximum Matrix**:
  $$P_0: [2, 1, 1], \quad P_1: [1, 2, 2], \quad P_2: [2, 1, 2]$$
- **Available Vector**:
  $$\text{Available}: [1, 1, 1]$$

### Execution & Output:
1. **Need Matrix**:
   $$P_0: [1, 1, 0], \quad P_1: [0, 1, 2], \quad P_2: [1, 0, 1]$$
2. **Work Progression**:
   - Initial Work: `(1, 1, 1)`
   - Step 1: $P_0$ satisfies $\text{Need} \le \text{Work}$. Runs, finishes, releases `(1, 0, 1)`. Work becomes `(2, 1, 2)`.
   - Step 2: $P_1$ satisfies $\text{Need} \le \text{Work}$. Runs, finishes, releases `(1, 1, 0)`. Work becomes `(3, 2, 2)`.
   - Step 3: $P_2$ satisfies $\text{Need} \le \text{Work}$. Runs, finishes, releases `(1, 1, 1)`. Work becomes `(4, 3, 3)`.
3. **Verdict**:
   - Status: **SAFE**
   - Safe Sequence: **$P_0 \to P_1 \to P_2$**
   - Final Work: `(4, 3, 3)` (conserves $\sum \text{Allocations} + \text{Available}$)

---

## 8. Research Extension: DFRR Prototype

### Research Source:
- **Botlagunta, M. D., Agrawal, S., & Rajeswara Rao, R. (2022)**. *"A Novel Resource Management Technique for Deadlock-Free Systems."* *International Journal of Information Technology*, 14(2), 627–635.

### Prototype Assumptions & Academic Claims:
- This is an **educational research-inspired prototype**.
- The physical capacity is partitioned into:
  $$\text{Total} = \text{Allocated} + \text{Available}_{\text{norm}} + \text{Reserved}$$
- When available normal resources are insufficient for any process to progress, the system loans from the reserved buffer to the candidate with the smallest deficit.
- We document honestly that reserving resources reduces the immediate unreserved capacity for standard processes; hence, DFRR is a specialized technique rather than an unqualified replacement for Banker's Algorithm.

---

## 9. Limitations & Future Scope

### Limitations:
1. **Static Maximum Claims**: Banker's Algorithm assumes processes declare maximum claims up front, which may not hold in unpredictable real-time software.
2. **Centralized Model**: Assumes a single centralized scheduler rather than distributed nodes.
3. **Synthetic Workloads**: Analyzes simulated process states rather than hooking into real Linux/Windows kernel threads.

### Future Scope:
1. Implementing hierarchical allocators for distributed clusters (*Madduri & Finkel, 1984*).
2. Integrating runtime graph caching for $O(\log n)$ safety checks (*Finkel & Madduri, 1987*).
3. Dynamic max claim updating based on control flow tree decomposition (*Lang, 1999*).
