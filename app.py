"""
Resource Allocation Simulator — Deadlock Avoidance using Banker's Algorithm
with Research-Based Resource Reservation (DFRR)

Academic Project: Second Year Engineering (SYCM3, Semester III, AY 2026-2027)
Department of Computer Engineering, Shah & Anchor Kutchhi Engineering College
Students: Yash Khapre (PRN 125BTCM1149, Roll 25), Aman Kumar (PRN 125BTCM1092, Roll 26)
Guide: Mrs. Vaishali Kosambkar
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import copy

from algorithms.banker import (
    compute_need_matrix,
    run_safety_algorithm,
    find_all_safe_sequences,
    SafetyCheckResult
)
from algorithms.resource_request import (
    evaluate_resource_request,
    ResourceRequestResult
)
from algorithms.dfrr import (
    run_dfrr_simulation,
    DFRRSimulationResult
)
from utils.validation import (
    validate_system_state,
    validate_resource_request,
    ValidationResult
)
from utils.examples import PRELOADED_EXAMPLES
from utils.metrics import (
    compute_resource_utilization,
    get_theoretical_complexity,
    benchmark_side_by_side
)

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Resource Allocation Simulator | Banker's & DFRR",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Modern OS Theme Styling
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .status-safe {
        background-color: #d1fae5;
        border: 2px solid #10b981;
        color: #065f46;
        border-radius: 8px;
        padding: 14px 20px;
        font-weight: 700;
        font-size: 1.15rem;
        text-align: center;
    }
    .status-unsafe {
        background-color: #fee2e2;
        border: 2px solid #ef4444;
        color: #991b1b;
        border-radius: 8px;
        padding: 14px 20px;
        font-weight: 700;
        font-size: 1.15rem;
        text-align: center;
    }
    .status-info {
        background-color: #e0f2fe;
        border: 2px solid #0284c7;
        color: #075985;
        border-radius: 8px;
        padding: 14px 20px;
        font-weight: 600;
    }
    .step-badge {
        display: inline-block;
        background: #3b82f6;
        color: white;
        border-radius: 12px;
        padding: 2px 10px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .process-chip {
        display: inline-block;
        background: #e2e8f0;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 4px 12px;
        margin: 2px;
        font-weight: 600;
        font-family: monospace;
    }
    .seq-arrow {
        color: #64748b;
        font-weight: bold;
        margin: 0 4px;
    }
    .academic-header {
        border-bottom: 2px solid #0284c7;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# State Initialization in st.session_state
# ---------------------------------------------------------
default_ex = PRELOADED_EXAMPLES["A: Safe State (SLA-1 / SLA-2 Official Sample)"]

if "num_processes" not in st.session_state:
    st.session_state.num_processes = default_ex.n
if "num_resources" not in st.session_state:
    st.session_state.num_resources = default_ex.m
if "allocation_matrix" not in st.session_state:
    st.session_state.allocation_matrix = copy.deepcopy(default_ex.allocation)
if "maximum_matrix" not in st.session_state:
    st.session_state.maximum_matrix = copy.deepcopy(default_ex.maximum)
if "available_vector" not in st.session_state:
    st.session_state.available_vector = copy.deepcopy(default_ex.available)
if "reserved_vector" not in st.session_state:
    st.session_state.reserved_vector = copy.deepcopy(default_ex.reserved_pool)
if "active_step_index" not in st.session_state:
    st.session_state.active_step_index = 0
if "last_scenario_name" not in st.session_state:
    st.session_state.last_scenario_name = default_ex.name


def load_scenario(scenario_key: str):
    """Loads a preloaded academic scenario into session state."""
    sc = PRELOADED_EXAMPLES[scenario_key]
    st.session_state.num_processes = sc.n
    st.session_state.num_resources = sc.m
    st.session_state.allocation_matrix = copy.deepcopy(sc.allocation)
    st.session_state.maximum_matrix = copy.deepcopy(sc.maximum)
    st.session_state.available_vector = copy.deepcopy(sc.available)
    st.session_state.reserved_vector = copy.deepcopy(sc.reserved_pool)
    st.session_state.active_step_index = 0
    st.session_state.last_scenario_name = sc.name


# ---------------------------------------------------------
# Sidebar Navigation & Academic Metadata
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/server.png", width=64)
st.sidebar.title("Deadlock Avoidance")
st.sidebar.markdown("**Resource Allocation Simulator**")
st.sidebar.caption("Banker's Algorithm & DFRR Research Extension")

nav_page = st.sidebar.radio(
    "Navigation Mode",
    [
        "📊 System Setup & Need Matrix",
        "🛡️ Banker's Safety & Step Trace",
        "🔄 Resource-Request Simulation",
        "🔬 DFRR Research Extension",
        "⚖️ Side-by-Side Comparison",
        "📚 Viva Guide & SDG Mapping"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Preloaded Academic Scenarios")
selected_scenario = st.sidebar.selectbox(
    "Select Scenario to Load",
    list(PRELOADED_EXAMPLES.keys()),
    index=0
)

if st.sidebar.button("⚡ Load Selected Scenario", use_container_width=True):
    load_scenario(selected_scenario)
    st.sidebar.success(f"Loaded: {selected_scenario}")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Academic Details**
- **Course**: Operating System (SYCM3, Sem III)
- **Students**:
  - Yash Khapre (`125BTCM1149`, R25)
  - Aman Kumar (`125BTCM1092`, R26)
- **Guide**: Mrs. Vaishali Kosambkar
- **Dept**: Computer Engineering
- **College**: Shah & Anchor Kutchhi Engg. College
- **AY**: 2026–2027
""")

# ---------------------------------------------------------
# Common Helpers
# ---------------------------------------------------------
def render_matrix_editor(n: int, m: int, key_prefix: str, matrix_data: List[List[int]], row_prefix: str = "P", col_prefix: str = "R") -> List[List[int]]:
    cols = [f"{col_prefix}{j}" for j in range(m)]
    rows = [f"{row_prefix}{i}" for i in range(n)]
    df = pd.DataFrame(matrix_data, index=rows, columns=cols)
    edited_df = st.data_editor(
        df,
        key=f"{key_prefix}_editor",
        use_container_width=True,
        num_rows="fixed",
        disabled=False
    )
    return edited_df.values.astype(int).tolist()


def render_vector_editor(m: int, key_prefix: str, vector_data: List[int], col_prefix: str = "R") -> List[int]:
    cols = [f"{col_prefix}{j}" for j in range(m)]
    df = pd.DataFrame([vector_data], index=["Instances"], columns=cols)
    edited_df = st.data_editor(
        df,
        key=f"{key_prefix}_editor",
        use_container_width=True,
        num_rows="fixed",
        disabled=False
    )
    return edited_df.iloc[0].values.astype(int).tolist()


# =========================================================================
# PAGE 1: SYSTEM SETUP & NEED MATRIX CALCULATION
# =========================================================================
if nav_page == "📊 System Setup & Need Matrix":
    st.markdown('<div class="academic-header"><h2>📊 System Configuration & Need Matrix Calculation</h2></div>', unsafe_allow_html=True)
    st.markdown("""
    Configure the number of processes ($n$) and resource types ($m$). Enter or modify the **Allocation Matrix**,
    **Maximum Matrix**, and **Available Vector**. The simulator automatically validates input consistency against
    rules **V1 through V7** (from SLA-2 Table 14) and computes the **Need Matrix** ($\text{Need} = \text{Maximum} - \text{Allocation}$).
    """)

    col_cfg1, col_cfg2, col_cfg3 = st.columns([1, 1, 2])
    with col_cfg1:
        new_n = st.number_input("Processes (n)", min_value=1, max_value=10, value=st.session_state.num_processes, step=1)
    with col_cfg2:
        new_m = st.number_input("Resource Types (m)", min_value=1, max_value=10, value=st.session_state.num_resources, step=1)
    with col_cfg3:
        st.write("")
        st.write("")
        if st.button("🔄 Reset / Apply Dimension Changes", use_container_width=True):
            st.session_state.num_processes = int(new_n)
            st.session_state.num_resources = int(new_m)
            # Resize matrices cleanly
            st.session_state.allocation_matrix = [[0] * new_m for _ in range(new_n)]
            st.session_state.maximum_matrix = [[0] * new_m for _ in range(new_n)]
            st.session_state.available_vector = [0] * new_m
            st.session_state.reserved_vector = [0] * new_m
            st.rerun()

    n = st.session_state.num_processes
    m = st.session_state.num_resources

    # Matrix editors
    col_mat1, col_mat2 = st.columns(2)
    with col_mat1:
        st.subheader("1. Allocation Matrix (Held Resources)")
        st.caption("Resources currently assigned to each process ($n \\times m$)")
        st.session_state.allocation_matrix = render_matrix_editor(
            n, m, "alloc", st.session_state.allocation_matrix
        )

    with col_mat2:
        st.subheader("2. Maximum Matrix (Peak Claims)")
        st.caption("Maximum resources each process may claim during its lifecycle ($n \\times m$)")
        st.session_state.maximum_matrix = render_matrix_editor(
            n, m, "max", st.session_state.maximum_matrix
        )

    col_vec1, col_vec2 = st.columns(2)
    with col_vec1:
        st.subheader("3. Available Vector (Free Normal Instances)")
        st.caption("Unallocated instances currently available for immediate dispatch ($m$)")
        st.session_state.available_vector = render_vector_editor(
            m, "avail", st.session_state.available_vector
        )

    with col_vec2:
        st.subheader("4. Reserved Resource Pool (DFRR Extension)")
        st.caption("Safety buffer reserved for unblocking potential deadlocks in DFRR mode ($m$)")
        st.session_state.reserved_vector = render_vector_editor(
            m, "res_pool", st.session_state.reserved_vector
        )

    # Validation execution
    v_res = validate_system_state(
        n=n,
        m=m,
        allocation=st.session_state.allocation_matrix,
        maximum=st.session_state.maximum_matrix,
        available=st.session_state.available_vector,
        check_v6=True
    )

    st.markdown("---")
    st.subheader("5. Input Validation Status & Need Matrix (Calculated)")

    if not v_res.is_valid:
        st.error("⚠️ **Validation Failed! One or more rules violated:**")
        for err in v_res.errors:
            st.markdown(f"- ❌ `{err}`")
        st.info("Please correct the highlighted input values above. Need Matrix cannot be calculated on invalid data.")
    else:
        st.success("✅ **All Validation Rules (V1–V7) Passed! Data is mathematically consistent.**")

        # Calculate Need Matrix
        need_mat = compute_need_matrix(st.session_state.allocation_matrix, st.session_state.maximum_matrix)

        col_need, col_summary = st.columns([1, 1])
        with col_need:
            st.markdown("#### Calculated Need Matrix: $\\text{Need}[i][j] = \\text{Maximum}[i][j] - \\text{Allocation}[i][j]$")
            need_df = pd.DataFrame(
                need_mat,
                index=[f"P{i}" for i in range(n)],
                columns=[f"R{j}" for j in range(m)]
            )
            st.dataframe(need_df, use_container_width=True)

        with col_summary:
            st.markdown("#### System Resource Accounting Invariant")
            alloc_sums = np.sum(np.array(st.session_state.allocation_matrix), axis=0)
            avail_arr = np.array(st.session_state.available_vector)
            total_instances = alloc_sums + avail_arr

            summary_df = pd.DataFrame({
                "Resource": [f"R{j}" for j in range(m)],
                "Allocated": alloc_sums,
                "Available (Normal)": avail_arr,
                "Total Physical": total_instances,
                "Reserved (DFRR)": st.session_state.reserved_vector
            })
            st.dataframe(summary_df, use_container_width=True)

        # Quick action pills
        st.markdown("##### Quick Actions:")
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("🚀 Proceed to Safety Check & Step-by-Step Trace", use_container_width=True):
                st.session_state.nav_page = "🛡️ Banker's Safety & Step Trace"
                st.rerun()


# =========================================================================
# PAGE 2: BANKER'S SAFETY ALGORITHM & STEP-BY-STEP TRACE
# =========================================================================
elif nav_page == "🛡️ Banker's Safety & Step Trace":
    st.markdown('<div class="academic-header"><h2>🛡️ Banker\'s Safety Algorithm & Step-by-Step Execution</h2></div>', unsafe_allow_html=True)

    n = st.session_state.num_processes
    m = st.session_state.num_resources
    alloc = st.session_state.allocation_matrix
    maximum = st.session_state.maximum_matrix
    avail = st.session_state.available_vector

    # Validate first
    v_res = validate_system_state(n, m, alloc, maximum, avail)
    if not v_res.is_valid:
        st.error("Input validation failed. Please return to 'System Setup' and resolve errors:")
        for err in v_res.errors:
            st.markdown(f"- ❌ `{err}`")
        st.stop()

    safety_result = run_safety_algorithm(alloc, maximum, avail, compute_all_sequences=True)

    # Top Status Banner
    col_stat1, col_stat2, col_stat3 = st.columns([2, 1, 1])
    with col_stat1:
        if safety_result.is_safe:
            st.markdown(f"""
            <div class="status-safe">
                ✓ SYSTEM IS IN A SAFE STATE<br>
                <span style="font-size: 1rem; font-weight: normal;">Safe Sequence: <b>{safety_result.safe_sequence_str}</b></span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-unsafe">
                ✕ SYSTEM IS IN AN UNSAFE STATE<br>
                <span style="font-size: 1rem; font-weight: normal;">No Safe Sequence Exists (Deadlock Risk)</span>
            </div>
            """, unsafe_allow_html=True)

    with col_stat2:
        st.metric(
            "Eligibility Checks",
            f"{safety_result.eligibility_checks_count} checks",
            delta=f"{safety_result.element_comparisons_count} elem comps"
        )
    with col_stat3:
        st.metric(
            "Safety Check Time",
            f"{safety_result.execution_time_seconds * 1e6:.1f} µs"
        )

    st.markdown("---")

    # Step-by-step Interactive Stepper
    st.subheader("Interactive Step-by-Step Algorithm Stepper")
    st.caption("Demonstrate each decision to faculty during your viva. Use Previous/Next buttons or the slider.")

    total_steps = len(safety_result.step_trace)
    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1, 1, 1, 3])

    with col_ctrl1:
        if st.button("⏮️ Previous Step", disabled=(st.session_state.active_step_index <= 0), use_container_width=True):
            st.session_state.active_step_index -= 1
            st.rerun()

    with col_ctrl2:
        if st.button("⏭️ Next Step", disabled=(st.session_state.active_step_index >= total_steps - 1), use_container_width=True):
            st.session_state.active_step_index += 1
            st.rerun()

    with col_ctrl3:
        if st.button("⏪ Reset to Step 0", use_container_width=True):
            st.session_state.active_step_index = 0
            st.rerun()

    with col_ctrl4:
        st.session_state.active_step_index = st.slider(
            "Step Slider",
            min_value=0,
            max_value=total_steps - 1,
            value=min(st.session_state.active_step_index, total_steps - 1)
        )

    # Render Current Step Details
    curr_step = safety_result.step_trace[st.session_state.active_step_index]

    step_col1, step_col2 = st.columns([1.4, 1])
    with step_col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Step {curr_step.step_number} of {total_steps - 1}: {curr_step.explanation}</h4>
            <hr style="margin: 8px 0;">
            <p><b>Candidate Evaluated:</b> {f"P{curr_step.candidate_process}" if curr_step.candidate_process >= 0 else "System Initialization"}</p>
            <p><b>Work Vector Before:</b> <code>{curr_step.work_before}</code></p>
            <p><b>Candidate Need:</b> <code>{curr_step.need_vector if curr_step.need_vector else 'N/A'}</code></p>
            <p><b>Comparison Details:</b> {'; '.join(curr_step.comparison_details)}</p>
            <p><b>Work Vector After Release:</b> <code>{curr_step.work_after}</code></p>
            <p><b>Process Finish Status Array:</b> <code>{curr_step.finish_status}</code></p>
        </div>
        """, unsafe_allow_html=True)

    with step_col2:
        # Progress Sequence Visualizer
        st.markdown("#### Safe Sequence Formation")
        if curr_step.current_safe_sequence:
            chips = " <span class='seq-arrow'>➔</span> ".join(
                [f"<span class='process-chip'>P{p}</span>" for p in curr_step.current_safe_sequence]
            )
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.info("No processes completed yet in this step.")

        # Work growth chart
        st.markdown("#### Work Vector Growth")
        work_df = pd.DataFrame({
            "Resource": [f"R{j}" for j in range(m)],
            "Current Work": curr_step.work_after,
            "Initial Available": safety_result.initial_work,
            "Final Total": safety_result.final_work
        })
        fig = px.bar(
            work_df,
            x="Resource",
            y=["Initial Available", "Current Work", "Final Total"],
            barmode="group",
            height=240,
            color_discrete_sequence=["#94a3b8", "#3b82f6", "#10b981"]
        )
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

    # Full Step Trace Table
    st.markdown("---")
    st.subheader("Full Step-by-Step Execution Trace Table")
    trace_data = [s.to_dict() for s in safety_result.step_trace]
    st.dataframe(pd.DataFrame(trace_data), use_container_width=True)

    # Educational Explanation & Alternative Sequences
    col_edu1, col_edu2 = st.columns(2)
    with col_edu1:
        st.markdown("#### 📖 Educational Explanation")
        st.markdown(safety_result.educational_explanation)

    with col_edu2:
        st.markdown("#### 🔀 Alternative Valid Safe Sequences")
        if safety_result.all_safe_sequences:
            st.markdown(f"Found **{len(safety_result.all_safe_sequences)}** mathematically valid safe sequence permutation(s):")
            for seq in safety_result.all_safe_sequences:
                seq_str = " -> ".join([f"P{p}" for p in seq])
                st.markdown(f"- `{seq_str}`")
            st.caption("Demonstrates to examiners that while the deterministic lowest-index tie-breaker produces one sequence, multiple valid orders guarantee safety.")
        else:
            st.write("No alternative safe sequences exist.")


# =========================================================================
# PAGE 3: RESOURCE REQUEST SIMULATION
# =========================================================================
elif nav_page == "🔄 Resource-Request Simulation":
    st.markdown('<div class="academic-header"><h2>🔄 Dynamic Resource-Request Simulation</h2></div>', unsafe_allow_html=True)
    st.markdown("""
    Simulate a running process making an immediate request for additional resources. The OS applies the Banker's
    Resource-Request checks:
    1. $\\text{Request} \\le \\text{Need}[i]$ (Cannot exceed declared maximum claim)
    2. $\\text{Request} \\le \\text{Available}$ (Cannot exceed currently free instances)
    3. Tentative allocation and safety algorithm evaluation.
    4. If Safe: **Grant Request**. If Unsafe: **Deny & Roll Back** (preserving original state intact).
    """)

    n = st.session_state.num_processes
    m = st.session_state.num_resources
    alloc = st.session_state.allocation_matrix
    maximum = st.session_state.maximum_matrix
    avail = st.session_state.available_vector

    need = compute_need_matrix(alloc, maximum)

    col_req_proc, col_req_vec = st.columns([1, 2])
    with col_req_proc:
        selected_pid = st.selectbox(
            "Select Requesting Process",
            options=list(range(n)),
            format_func=lambda x: f"Process P{x}"
        )
        st.markdown(f"**Current Allocation:** `{alloc[selected_pid]}`")
        st.markdown(f"**Current Remaining Need:** `{need[selected_pid]}`")
        st.markdown(f"**Current System Available:** `{avail}`")

    with col_req_vec:
        st.markdown(f"##### Enter Request Vector for P{selected_pid}")
        req_inputs = []
        cols = st.columns(m)
        for j in range(m):
            with cols[j]:
                val = st.number_input(
                    f"Req R{j}",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=1,
                    key=f"req_input_{j}"
                )
                req_inputs.append(int(val))

        st.caption(f"Request Vector: `{req_inputs}`")

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        eval_btn = st.button("🧪 Evaluate Resource Request", use_container_width=True)

    if eval_btn:
        st.markdown("---")
        st.subheader("Evaluation Results & OS Action")

        req_res = evaluate_resource_request(
            allocation=alloc,
            maximum=maximum,
            available=avail,
            process_id=selected_pid,
            request_vector=req_inputs
        )

        if req_res.is_granted:
            st.markdown(f"""
            <div class="status-safe">
                ✓ REQUEST GRANTED FOR P{selected_pid}<br>
                <span style="font-size: 1rem; font-weight: normal;">{req_res.message}</span>
            </div>
            """, unsafe_allow_html=True)
        elif req_res.status == "WAIT_INSUFFICIENT_AVAILABLE":
            st.markdown(f"""
            <div class="status-info">
                ⏳ REQUEST MUST WAIT (INSUFFICIENT AVAILABLE)<br>
                <span style="font-size: 1rem; font-weight: normal;">{req_res.message}</span>
            </div>
            """, unsafe_allow_html=True)
        elif req_res.status == "DENIED_EXCEEDS_NEED":
            st.markdown(f"""
            <div class="status-unsafe">
                ❌ REQUEST DENIED (EXCEEDS REMAINING NEED)<br>
                <span style="font-size: 1rem; font-weight: normal;">{req_res.message}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-unsafe">
                🛑 REQUEST DENIED (TENTATIVE STATE UNSAFE)<br>
                <span style="font-size: 1rem; font-weight: normal;">{req_res.message}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Educational Explanation")
        st.write(req_res.educational_explanation)

        col_orig, col_tent = st.columns(2)
        with col_orig:
            st.markdown("##### Original System State")
            st.write(f"- Available: `{req_res.original_available}`")
            st.write(f"- Allocation P{selected_pid}: `{req_res.original_allocation[selected_pid]}`")
            st.write(f"- Need P{selected_pid}: `{req_res.original_need[selected_pid]}`")

        with col_tent:
            st.markdown("##### Resulting / Tentative State")
            st.write(f"- Available: `{req_res.resulting_available}`")
            st.write(f"- Allocation P{selected_pid}: `{req_res.resulting_allocation[selected_pid]}`")
            st.write(f"- Need P{selected_pid}: `{req_res.resulting_need[selected_pid]}`")

        if req_res.tentative_safety_result:
            st.markdown("##### Tentative Safety Trace:")
            st.write(f"- Safe Sequence: **{req_res.tentative_safety_result.safe_sequence_str}**")
            st.write(f"- Eligibility Checks: **{req_res.tentative_safety_result.eligibility_checks_count}**")

        if req_res.is_granted:
            if st.button("💾 Permanently Apply Changes to Session State", use_container_width=True):
                st.session_state.allocation_matrix = req_res.resulting_allocation
                st.session_state.available_vector = req_res.resulting_available
                st.success("State successfully updated!")
                st.rerun()


# =========================================================================
# PAGE 4: DFRR RESEARCH EXTENSION
# =========================================================================
elif nav_page == "🔬 DFRR Research Extension":
    st.markdown('<div class="academic-header"><h2>🔬 Deadlock-Free Resource Reservation (DFRR) — Research Extension</h2></div>', unsafe_allow_html=True)

    st.markdown("""
    > **Research Grounding**: Based on *Botlagunta, Agrawal & Rajeswara Rao (2022)*,
    > *"A Novel Resource Management Technique for Deadlock-Free Systems"*, *International Journal of Information Technology*,
    > Vol. 14, No. 2, pp. 627–635 (DOI: [10.1007/s41870-021-00670-6](https://doi.org/10.1007/s41870-021-00670-6)).
    >
    > **Academic Disclosure**: This is a **research-inspired, simplified prototype**. It explores how a dedicated
    > **Reserved Resource Pool** can unblock bottleneck processes that would otherwise stall under standard Banker's safety rules,
    > allowing them to run to completion and release all held resources without full permutation recalculation.
    """)

    n = st.session_state.num_processes
    m = st.session_state.num_resources
    alloc = st.session_state.allocation_matrix
    maximum = st.session_state.maximum_matrix
    avail = st.session_state.available_vector
    res_pool = st.session_state.reserved_vector

    col_dfrr_cfg1, col_dfrr_cfg2 = st.columns(2)
    with col_dfrr_cfg1:
        st.subheader("Configure Reserved Resource Pool")
        st.caption("Allocate safety reserve instances for each resource type")
        st.session_state.reserved_vector = render_vector_editor(m, "dfrr_res", st.session_state.reserved_vector)
        res_pool = st.session_state.reserved_vector

    with col_dfrr_cfg2:
        st.subheader("Physical Resource Breakdown")
        sum_alloc = [sum(alloc[i][j] for i in range(n)) for j in range(m)]
        total_physical = [sum_alloc[j] + avail[j] + res_pool[j] for j in range(m)]

        breakdown_df = pd.DataFrame({
            "Resource": [f"R{j}" for j in range(m)],
            "Allocated": sum_alloc,
            "Normal Available": avail,
            "Reserved Pool": res_pool,
            "Total Physical Capacity": total_physical
        })
        st.dataframe(breakdown_df, use_container_width=True)

    if st.button("🚀 Run DFRR Simulation", use_container_width=True):
        st.session_state.dfrr_ran = True

    if st.session_state.get("dfrr_ran", False):
        dfrr_result = run_dfrr_simulation(
            allocation=alloc,
            maximum=maximum,
            available_normal=avail,
            reserved_pool=res_pool
        )

        st.markdown("---")
        col_res1, col_res2, col_res3 = st.columns([2, 1, 1])
        with col_res1:
            if dfrr_result.is_successful:
                st.markdown(f"""
                <div class="status-safe">
                    ✓ DFRR SIMULATION SUCCESSFUL<br>
                    <span style="font-size: 1rem; font-weight: normal;">Execution Order: <b>{dfrr_result.sequence_str}</b></span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-unsafe">
                    ✕ DFRR SYSTEM STALLED<br>
                    <span style="font-size: 1rem; font-weight: normal;">Reserve pool insufficient to unblock remaining processes</span>
                </div>
                """, unsafe_allow_html=True)

        with col_res2:
            st.metric("Reserve Invocations", f"{dfrr_result.reserved_pool_invocations} times")
        with col_res3:
            st.metric("DFRR Execution Time", f"{dfrr_result.execution_time_seconds * 1e6:.1f} µs")

        st.markdown("#### Educational Research Notes")
        st.write(dfrr_result.research_notes)

        # Event log
        st.subheader("DFRR Event Log (Step-by-Step Accounting)")
        event_data = [e.to_dict() for e in dfrr_result.events]
        st.dataframe(pd.DataFrame(event_data), use_container_width=True)


# =========================================================================
# PAGE 5: SIDE-BY-SIDE COMPARISON
# =========================================================================
elif nav_page == "⚖️ Side-by-Side Comparison":
    st.markdown('<div class="academic-header"><h2>⚖️ Side-by-Side Comparison: Traditional Banker\'s vs DFRR</h2></div>', unsafe_allow_html=True)

    n = st.session_state.num_processes
    m = st.session_state.num_resources
    alloc = st.session_state.allocation_matrix
    maximum = st.session_state.maximum_matrix
    avail = st.session_state.available_vector
    res_pool = st.session_state.reserved_vector

    bench = benchmark_side_by_side(alloc, maximum, avail, res_pool, runs=20)

    st.markdown("### 1. Live Benchmark on Current System State (20 Iterations)")

    col_cmp1, col_cmp2, col_cmp3 = st.columns(3)
    with col_cmp1:
        st.markdown("#### Traditional Banker's (Normal Available)")
        st.write(f"- **Verdict:** {'SAFE' if bench['banker_normal']['is_safe'] else 'UNSAFE'}")
        st.write(f"- **Sequence:** `{bench['banker_normal']['sequence']}`")
        st.write(f"- **Median Execution Time:** `{bench['banker_normal']['median_time_us']} µs`")
        st.write(f"- **Eligibility Checks:** `{bench['banker_normal']['checks']}`")

    with col_cmp2:
        st.markdown("#### Traditional Banker's (Combined Total Available)")
        st.write(f"- **Verdict:** {'SAFE' if bench['banker_combined']['is_safe'] else 'UNSAFE'}")
        st.write(f"- **Sequence:** `{bench['banker_combined']['sequence']}`")
        st.write(f"- **Median Execution Time:** `{bench['banker_combined']['median_time_us']} µs`")
        st.write(f"- **Eligibility Checks:** `{bench['banker_combined']['checks']}`")

    with col_cmp3:
        st.markdown("#### Research DFRR (Normal + Reserved Pool)")
        st.write(f"- **Verdict:** {'SUCCESSFUL' if bench['dfrr']['is_successful'] else 'STALLED'}")
        st.write(f"- **Sequence:** `{bench['dfrr']['sequence']}`")
        st.write(f"- **Median Execution Time:** `{bench['dfrr']['median_time_us']} µs`")
        st.write(f"- **Reserve Pool Invocations:** `{bench['dfrr']['reserve_invocations']}`")

    st.markdown("---")
    st.markdown("### 2. Conceptual & Theoretical Comparison Matrix")

    comp_table = pd.DataFrame([
        {
            "Comparison Dimension": "Primary Operating Principle",
            "Traditional Banker's Algorithm (Dijkstra, 1965)": "Global centralized safety checking via greedy hypothetical simulation of completion.",
            "Deadlock-Free Resource Reservation (DFRR - Botlagunta et al. 2022)": "Dedicated reserved pool partition that unblocks bottleneck processes to release held resources."
        },
        {
            "Comparison Dimension": "Resource Management Model",
            "Traditional Banker's Algorithm (Dijkstra, 1965)": "Single unpartitioned pool of Available resources.",
            "Deadlock-Free Resource Reservation (DFRR - Botlagunta et al. 2022)": "Two-tier partitioned architecture: Normal Unreserved Pool + Reserved Pool."
        },
        {
            "Comparison Dimension": "Request Evaluation Overhead",
            "Traditional Banker's Algorithm (Dijkstra, 1965)": "O(n² · m) worst-case search over all processes on every resource request.",
            "Deadlock-Free Resource Reservation (DFRR - Botlagunta et al. 2022)": "O(m) resource management overhead; O(n) pool estimation."
        },
        {
            "Comparison Dimension": "Unsafe State vs Deadlock",
            "Traditional Banker's Algorithm (Dijkstra, 1965)": "Cautious avoidance: Denies requests entering unsafe states even if deadlock hasn't occurred.",
            "Deadlock-Free Resource Reservation (DFRR - Botlagunta et al. 2022)": "Interventionist: Proactively loans reserved resources to bridge temporary deficits and prevent cyclic waits."
        },
        {
            "Comparison Dimension": "Advance Information Required",
            "Traditional Banker's Algorithm (Dijkstra, 1965)": "Requires exact Maximum claim vector declared in advance for every process.",
            "Deadlock-Free Resource Reservation (DFRR - Botlagunta et al. 2022)": "Requires tuning/sizing the reserved pool to exceed maximum single-process deficit."
        },
        {
            "Comparison Dimension": "Fairness and Comparison Caveats",
            "Traditional Banker's Algorithm (Dijkstra, 1965)": "Benchmark baseline for single-instance/multi-instance safe-state detection.",
            "Deadlock-Free Resource Reservation (DFRR - Botlagunta et al. 2022)": "Cannot be blindly treated as superior; reserving resources reduces immediate free capacity for normal requests."
        }
    ])
    st.table(comp_table)


# =========================================================================
# PAGE 6: VIVA GUIDE & SDG MAPPING
# =========================================================================
elif nav_page == "📚 Viva Guide & SDG Mapping":
    st.markdown('<div class="academic-header"><h2>📚 Viva Voce Guide, Research Synthesis & SDG Mapping</h2></div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🎯 Sustainable Development Goals (SDG) Alignment
    As documented in the SLA-1 report:
    - **SDG 9: Industry, Innovation and Infrastructure**: Operating Systems are fundamental computing infrastructure. Reliable deadlock avoidance prevents system-wide freezes and ensures continuous compute service.
    - **SDG 4: Quality Education**: An interactive simulator allows computer engineering students to witness state transitions, Work vector growth, and rollback operations rather than purely memorizing matrix formulas.
    """)

    st.markdown("---")
    st.markdown("### 🎓 Core Viva Questions & Answers for Second-Year Students")

    with st.expander("Q1: What is the difference between an Unsafe State and a Deadlocked State?"):
        st.markdown("""
        **Answer:**
        - A **deadlocked state** is a state where two or more processes are permanently blocked, each holding resources while waiting for resources held by another process in a circular wait.
        - An **unsafe state** is NOT necessarily deadlocked. It simply means that the Operating System **cannot guarantee** that all processes will finish if each process suddenly requests its full maximum claim.
        - Deadlock Avoidance (Banker's Algorithm) is cautious: it ensures the system **never leaves a safe state**, preventing deadlocks before they can form.
        """)

    with st.expander("Q2: Why is the Banker's Algorithm O(n² · m) in the worst case?"):
        st.markdown("""
        **Answer:**
        - In the worst case, $n$ iterations are needed to finish all $n$ processes (one per pass).
        - In each iteration, the algorithm may scan up to $n$ unfinished processes.
        - For each process, comparing its Need vector against the Work vector takes $m$ comparisons (one per resource type).
        - Total operations: $\\sum_{k=1}^n k \\cdot m = \\frac{n(n+1)}{2} \\cdot m = O(n^2 m)$.
        """)

    with st.expander("Q3: Why is a greedy choice of the first eligible process sufficient?"):
        st.markdown("""
        **Answer:**
        - In Banker's Algorithm, when any eligible process $P_i$ completes, it releases its allocated resources: $\\text{Work} \\leftarrow \\text{Work} + \\text{Allocation}[i]$.
        - Therefore, the Work vector **is monotonically non-decreasing**.
        - A process that was eligible before $P_i$ finished will still have $\\text{Need} \\le \\text{Work}$ after $P_i$ finishes.
        - Thus, the order of eligible process selection can change the specific safe sequence, but **never changes whether the state is safe or unsafe**.
        """)

    with st.expander("Q4: What are the 5 research papers analyzed in SLA-1 and SLA-2?"):
        st.markdown("""
        1. **Madduri & Finkel (1984)**: *Extension of Banker's Algorithm in Distributed OS* (Hierarchical allocators).
        2. **Finkel & Madduri (1987)**: *Efficient Deadlock Avoidance Algorithm* ($O(\\log n)$ test by caching safe sequences).
        3. **Moser & Melliar-Smith (1990)**: *The World Banker's Algorithm* (Concurrent, decentralized decisions).
        4. **Lang (1999)**: *Extended Banker's Algorithm* (Control flow graph tree decomposition for localized claims).
        5. **Botlagunta, Agrawal & Rao (2022)**: *Deadlock-Free Resource Reservation (DFRR)* (Two-tier reserved pool).
        """)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption(
    "Academic SLA-2 Project: Resource Allocation Simulator | "
    "Shah & Anchor Kutchhi Engineering College | "
    "Yash Khapre & Aman Kumar | Guided by Mrs. Vaishali Kosambkar | AY 2026-2027"
)
