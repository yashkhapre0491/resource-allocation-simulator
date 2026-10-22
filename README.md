# Resource Allocation Simulator — Banker's Algorithm

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![Pytest](https://img.shields.io/badge/Pytest-Passed-success.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An interactive, responsive single-page web simulator implementing **Dijkstra's Banker's Algorithm** for deadlock avoidance in operating systems. Designed with a clean two-column dashboard layout modeled directly after academic Operating Systems system specifications.

---

## 1. Overview & Operating Principle

In multitasking operating systems, multiple concurrently executing processes compete for a shared finite set of resources (CPU, memory, devices). Granting resource claims without forward-looking checks can push the system into an **unsafe state**, leading to circular wait and **deadlock**.

The **Banker's Algorithm** avoids deadlock by simulating hypothetical process completion:
1. **Need Matrix Calculation**: 
   $$\text{Need}[i][j] = \text{Maximum}[i][j] - \text{Allocation}[i][j]$$
2. **Safety Check**:
   - Initializes $\text{Work} = \text{Available}$ and $\text{Finish}[i] = \text{False}$.
   - Finds an unfinished process $P_i$ whose $\text{Need}[i] \le \text{Work}$ across all resource types.
   - Simulates process $P_i$ completing and releasing its allocated resources:
     $$\text{Work} = \text{Work} + \text{Allocation}[i]$$
   - Marks $P_i$ as finished and repeats until all processes complete (**SAFE**) or no eligible process remains (**UNSAFE**).

---

## 2. Interface Components (Two-Column Layout)

The application provides a compact, wireframe-faithful layout structured into 10 numbered modules:

### Left Column: Inputs & Actions
1. **Configuration**: Set process count ($n$) and resource count ($m$) with dynamic matrix generation.
2. **Allocation Matrix (editable)**: Current resource instances held by each process ($n \times m$).
3. **Maximum Matrix (editable)**: Peak resource claims declared by each process ($n \times m$).
4. **Available Vector (editable)**: Currently free, unallocated instances of each resource type ($m$).
5. **Actions**:
   - `Calculate Need`: Computes and displays the read-only Need Matrix with full validation.
   - `Run Safety Check`: Validates inputs, executes the safety algorithm, updates system status, and produces the execution trace.
   - `Reset`: Restores default $3 \times 3$ values and clears previous execution traces.

### Right Column: Outputs & Trace
6. **Need Matrix (calculated, read-only)**: Dynamic display of remaining requirements ($\text{Need} = \text{Maximum} - \text{Allocation}$).
7. **System Status**: High-visibility status indicator (`SAFE` in green or `UNSAFE` in red).
8. **Safe Sequence**: Interactive ordered sequence badges ($P0 \to P1 \to P2$) or clear notice if no sequence exists.
9. **Step-by-Step Trace**: Table showing decision step, candidate process, eligibility check (`yes`/`no`), and resulting Work vector.
10. **Message Line**: Context-aware status notification (red for input validation errors, green for success).

---

## 3. Technology Stack

- **Python 3.11+**
- **Streamlit**: Web interface & interactive state management
- **NumPy & Pandas**: Matrix operations & data tables
- **Pytest**: Automated test suite

---

## 4. Quick-Start Guide (Windows)

### Option A: 1-Click Launch (Recommended)
Double-click:
```cmd
run_simulator.bat
```

### Option B: Command Line Launch
1. Open PowerShell or Command Prompt in the project folder:
   ```powershell
   cd c:\Users\Yash\Desktop\resource-allocation-simulator
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Launch the Streamlit application:
   ```powershell
   streamlit run app.py
   ```

4. Open your browser at:
   ```
   http://localhost:8501
   ```

---

## 5. Sample Default Execution

### Initial Inputs:
- **Processes ($n$)**: 3 ($P0, P1, P2$)
- **Resources ($m$)**: 3 ($R0, R1, R2$)
- **Allocation**:
  $$P0: [1, 0, 1], \quad P1: [1, 1, 0], \quad P2: [1, 1, 1]$$
- **Maximum**:
  $$P0: [2, 1, 1], \quad P1: [1, 2, 2], \quad P2: [2, 1, 2]$$
- **Available**:
  $$R0: 1, \quad R1: 1, \quad R2: 1$$

### Calculated Output:
- **Need Matrix**:
  $$P0: [1, 1, 0], \quad P1: [0, 1, 2], \quad P2: [1, 0, 1]$$
- **System Status**: **SAFE**
- **Safe Sequence**: **$P0 \to P1 \to P2$**
- **Trace Progression**:
  - Step 1: $P0 \implies \text{Need} \le \text{Work} \implies \text{Work after} = (2, 1, 2)$
  - Step 2: $P1 \implies \text{Need} \le \text{Work} \implies \text{Work after} = (3, 2, 2)$
  - Step 3: $P2 \implies \text{Need} \le \text{Work} \implies \text{Work after} = (4, 3, 3)$

---

## 6. Running Automated Tests

Run the automated test suite with:
```powershell
python -m pytest tests -v
```
All unit tests verify Need calculation, safe/unsafe state detection, boundary conditions, and validation rules.
