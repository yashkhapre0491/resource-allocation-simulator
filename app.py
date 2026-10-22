"""
Resource Allocation Simulator — Banker's Algorithm
Single-page, clean, interactive simulator strictly conforming to Figure 6 Wireframe.
"""

from typing import List, Dict, Any, Optional, Tuple
import streamlit as st
import numpy as np
import pandas as pd
import copy

from algorithms.banker import compute_need_matrix, run_safety_algorithm

# ---------------------------------------------------------
# Page Setup & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Resource Allocation Simulator — Banker's Algorithm",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS directly implementing Figure 6 wireframe layout and colors
st.markdown("""
<style>
    /* Hide default Streamlit header and reduce padding */
    header[data-testid="stHeader"] {
        display: none;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1.5rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 1400px;
    }

    /* Top wireframe window bar */
    .window-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #f8fafc;
        border: 2px solid #cbd5e1;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        margin-bottom: 12px;
    }
    .window-dots {
        display: flex;
        gap: 6px;
        align-items: center;
    }
    .dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-red { background-color: #ef4444; }
    .dot-yellow { background-color: #f59e0b; }
    .dot-green { background-color: #10b981; }
    .window-title {
        font-weight: 700;
        font-size: 1.05rem;
        color: #0f172a;
        letter-spacing: -0.01em;
    }
    .window-badge {
        background-color: #b91c1c;
        color: white;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 4px;
        letter-spacing: 0.05em;
    }

    /* Dashed wireframe cards */
    .card-box {
        border: 2px dashed #93c5fd;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 12px;
        background-color: #ffffff;
    }
    .card-box-purple {
        border: 2px dashed #c084fc;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 12px;
        background-color: #ffffff;
    }

    /* Numbered section badge */
    .sec-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        background-color: #0f172a;
        color: #ffffff;
        border-radius: 50%;
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 8px;
    }
    .sec-heading {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0f172a;
        display: inline-flex;
        align-items: center;
    }

    /* System Status Badges */
    .status-container {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 6px 0;
    }
    .badge-safe-active {
        background-color: #16a34a;
        color: #ffffff;
        font-weight: 800;
        font-size: 1.15rem;
        padding: 8px 36px;
        border-radius: 6px;
        display: inline-block;
        letter-spacing: 0.05em;
    }
    .badge-safe-inactive {
        background-color: #ffffff;
        border: 2px solid #86efac;
        color: #86efac;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 6px 30px;
        border-radius: 6px;
        display: inline-block;
    }
    .badge-unsafe-active {
        background-color: #dc2626;
        color: #ffffff;
        font-weight: 800;
        font-size: 1.15rem;
        padding: 8px 32px;
        border-radius: 6px;
        display: inline-block;
        letter-spacing: 0.05em;
    }
    .badge-unsafe-inactive {
        background-color: #ffffff;
        border: 2px solid #ef4444;
        color: #dc2626;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 6px 26px;
        border-radius: 6px;
        display: inline-block;
    }
    .status-subtext {
        font-size: 0.8rem;
        color: #64748b;
        font-style: italic;
    }

    /* Safe sequence chip pills */
    .sequence-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin: 6px 0;
    }
    .proc-chip {
        border: 2px solid #16a34a;
        background-color: #f0fdf4;
        color: #15803d;
        font-weight: 700;
        font-family: monospace;
        font-size: 0.95rem;
        padding: 4px 18px;
        border-radius: 20px;
    }
    .proc-arrow {
        color: #16a34a;
        font-weight: 900;
        font-size: 1.15rem;
    }
    .proc-none {
        color: #94a3b8;
        font-style: italic;
        font-size: 0.9rem;
    }

    /* Message line styling */
    .msg-display {
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 0.88rem;
        font-family: monospace;
        font-weight: 600;
    }
    .msg-display-red {
        background-color: #fee2e2;
        color: #b91c1c;
        border: 1px solid #f87171;
    }
    .msg-display-green {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
    }
    .msg-display-neutral {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Default Data Setup (Section 6)
# ---------------------------------------------------------
DEFAULT_N = 3
DEFAULT_M = 3
DEFAULT_ALLOCATION = [
    [1, 0, 1],
    [1, 1, 0],
    [1, 1, 1]
]
DEFAULT_MAXIMUM = [
    [2, 1, 1],
    [1, 2, 2],
    [2, 1, 2]
]
DEFAULT_AVAILABLE = [1, 1, 1]

# Session State Initialization
if "n" not in st.session_state:
    st.session_state.n = DEFAULT_N
if "m" not in st.session_state:
    st.session_state.m = DEFAULT_M
if "allocation" not in st.session_state:
    st.session_state.allocation = copy.deepcopy(DEFAULT_ALLOCATION)
if "maximum" not in st.session_state:
    st.session_state.maximum = copy.deepcopy(DEFAULT_MAXIMUM)
if "available" not in st.session_state:
    st.session_state.available = copy.deepcopy(DEFAULT_AVAILABLE)
if "need_matrix" not in st.session_state:
    st.session_state.need_matrix = None
if "safety_result" not in st.session_state:
    st.session_state.safety_result = None
if "message" not in st.session_state:
    st.session_state.message = ("Ready. Enter inputs and click 'Calculate Need' or 'Run Safety Check'.", "neutral")
if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0

# ---------------------------------------------------------
# Header Bar (Wireframe Top Bar)
# ---------------------------------------------------------
st.markdown("""
<div class="window-header">
    <div class="window-dots">
        <span class="dot dot-red"></span>
        <span class="dot dot-yellow"></span>
        <span class="dot dot-green"></span>
    </div>
    <div class="window-title">Resource Allocation Simulator — Banker's Algorithm</div>
    <div class="window-badge">BANKER'S ALGORITHM SIMULATOR</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2-Column Responsive Layout
# ---------------------------------------------------------
col_left, col_right = st.columns([1, 1], gap="medium")

n = st.session_state.n
m = st.session_state.m
res_cols = [f"R{j}" for j in range(m)]
proc_rows = [f"P{i}" for i in range(n)]

# =========================================================
# LEFT COLUMN: Inputs & Actions
# =========================================================
with col_left:
    # 1. Configuration
    st.markdown("""
    <div class="card-box">
        <div class="sec-heading"><span class="sec-badge">1</span> Configuration</div>
    </div>
    """, unsafe_allow_html=True)

    c_cfg1, c_cfg2, c_cfg3 = st.columns([1.5, 1.5, 1.2])
    with c_cfg1:
        cfg_n = st.number_input("Processes (n)", min_value=1, max_value=10, value=st.session_state.n, step=1, key="in_n")
    with c_cfg2:
        cfg_m = st.number_input("Resource types (m)", min_value=1, max_value=10, value=st.session_state.m, step=1, key="in_m")
    with c_cfg3:
        st.write("")
        st.write("")
        if st.button("Generate", use_container_width=True):
            new_n = int(cfg_n)
            new_m = int(cfg_m)

            # Safely resize Allocation & Maximum
            new_alloc = []
            new_max = []
            for i in range(new_n):
                a_row = []
                m_row = []
                for j in range(new_m):
                    if i < st.session_state.n and j < st.session_state.m:
                        a_row.append(st.session_state.allocation[i][j])
                        m_row.append(st.session_state.maximum[i][j])
                    else:
                        a_row.append(0)
                        m_row.append(0)
                new_alloc.append(a_row)
                new_max.append(m_row)

            # Safely resize Available
            new_avail = []
            for j in range(new_m):
                if j < st.session_state.m:
                    new_avail.append(st.session_state.available[j])
                else:
                    new_avail.append(1)

            st.session_state.n = new_n
            st.session_state.m = new_m
            st.session_state.allocation = new_alloc
            st.session_state.maximum = new_max
            st.session_state.available = new_avail
            st.session_state.need_matrix = None
            st.session_state.safety_result = None
            st.session_state.editor_version += 1
            st.session_state.message = (f"Generated input matrices for {new_n} processes and {new_m} resource types.", "neutral")
            st.rerun()

    # 2. Allocation Matrix (editable)
    st.markdown("""
    <div class="card-box">
        <div class="sec-heading"><span class="sec-badge">2</span> Allocation Matrix (editable)</div>
    </div>
    """, unsafe_allow_html=True)

    alloc_df = pd.DataFrame(st.session_state.allocation, index=proc_rows, columns=res_cols)
    edited_alloc = st.data_editor(
        alloc_df,
        key=f"alloc_ed_{st.session_state.editor_version}",
        use_container_width=True,
        num_rows="fixed"
    )

    # 3. Maximum Matrix (editable)
    st.markdown("""
    <div class="card-box">
        <div class="sec-heading"><span class="sec-badge">3</span> Maximum Matrix (editable)</div>
    </div>
    """, unsafe_allow_html=True)

    max_df = pd.DataFrame(st.session_state.maximum, index=proc_rows, columns=res_cols)
    edited_max = st.data_editor(
        max_df,
        key=f"max_ed_{st.session_state.editor_version}",
        use_container_width=True,
        num_rows="fixed"
    )

    # 4. Available Vector (editable)
    st.markdown("""
    <div class="card-box">
        <div class="sec-heading"><span class="sec-badge">4</span> Available Vector (editable)</div>
    </div>
    """, unsafe_allow_html=True)

    avail_df = pd.DataFrame([st.session_state.available], index=["Available"], columns=res_cols)
    edited_avail = st.data_editor(
        avail_df,
        key=f"avail_ed_{st.session_state.editor_version}",
        use_container_width=True,
        num_rows="fixed"
    )

    # 5. Actions (Buttons)
    st.markdown("""
    <div class="card-box">
        <div class="sec-heading"><span class="sec-badge">5</span> Actions</div>
    </div>
    """, unsafe_allow_html=True)

    # Validation and Extraction Helper
    def extract_and_validate() -> Tuple[Optional[List[List[int]]], Optional[List[List[int]]], Optional[List[int]], Optional[str]]:
        try:
            alloc_vals = edited_alloc.values.astype(int).tolist()
            max_vals = edited_max.values.astype(int).tolist()
            avail_vals = edited_avail.iloc[0].values.astype(int).tolist()
        except Exception as e:
            return None, None, None, f"Input error: {str(e)}"

        # Validate non-negativity
        for i in range(n):
            for j in range(m):
                if alloc_vals[i][j] < 0:
                    return None, None, None, f"Allocation for P{i}, R{j} must be a non-negative integer."
                if max_vals[i][j] < 0:
                    return None, None, None, f"Maximum for P{i}, R{j} must be a non-negative integer."

        for j in range(m):
            if avail_vals[j] < 0:
                return None, None, None, f"Available for R{j} must be a non-negative integer."

        # Validate Allocation <= Maximum
        for i in range(n):
            for j in range(m):
                if alloc_vals[i][j] > max_vals[i][j]:
                    return None, None, None, f"Allocation exceeds Maximum for P{i}, R{j} (Allocation={alloc_vals[i][j]} > Maximum={max_vals[i][j]})"

        return alloc_vals, max_vals, avail_vals, None

    btn1, btn2, btn3 = st.columns(3)
    with btn1:
        if st.button("Calculate Need", use_container_width=True, type="primary"):
            a_v, m_v, av_v, err = extract_and_validate()
            if err:
                st.session_state.message = (err, "red")
                st.session_state.need_matrix = None
            else:
                st.session_state.allocation = a_v
                st.session_state.maximum = m_v
                st.session_state.available = av_v
                st.session_state.need_matrix = compute_need_matrix(a_v, m_v)
                st.session_state.message = ("Need Matrix calculated successfully (Need = Maximum - Allocation).", "green")
            st.rerun()

    with btn2:
        if st.button("Run Safety Check", use_container_width=True):
            a_v, m_v, av_v, err = extract_and_validate()
            if err:
                st.session_state.message = (err, "red")
                st.session_state.need_matrix = None
                st.session_state.safety_result = None
            else:
                st.session_state.allocation = a_v
                st.session_state.maximum = m_v
                st.session_state.available = av_v
                need_m = compute_need_matrix(a_v, m_v)
                st.session_state.need_matrix = need_m

                # Execute Banker's safety check
                res = run_safety_algorithm(a_v, m_v, av_v, compute_all_sequences=False)
                st.session_state.safety_result = res

                if res.is_safe:
                    seq_str = " -> ".join([f"P{p}" for p in res.safe_sequence])
                    st.session_state.message = (f"Safe sequence established: {seq_str}", "green")
                else:
                    unfin_str = ", ".join([f"P{p}" for p in res.unfinished_processes])
                    st.session_state.message = (f"No safe sequence found. Unfinished: {unfin_str}", "red")
            st.rerun()

    with btn3:
        if st.button("Reset", use_container_width=True):
            st.session_state.n = DEFAULT_N
            st.session_state.m = DEFAULT_M
            st.session_state.allocation = copy.deepcopy(DEFAULT_ALLOCATION)
            st.session_state.maximum = copy.deepcopy(DEFAULT_MAXIMUM)
            st.session_state.available = copy.deepcopy(DEFAULT_AVAILABLE)
            st.session_state.need_matrix = None
            st.session_state.safety_result = None
            st.session_state.editor_version += 1
            st.session_state.message = ("Reset to default 3-process, 3-resource example.", "neutral")
            st.rerun()


# =========================================================
# RIGHT COLUMN: Outputs & Trace
# =========================================================
with col_right:
    # 6. Need Matrix (calculated, read-only)
    st.markdown("""
    <div class="card-box-purple">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="sec-heading"><span class="sec-badge">6</span> Need Matrix (calculated, read-only)</div>
            <div style="font-size: 0.8rem; font-style: italic; color: #64748b;">Need = Maximum - Allocation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.need_matrix is not None:
        need_df = pd.DataFrame(st.session_state.need_matrix, index=proc_rows, columns=res_cols)
        st.dataframe(need_df, use_container_width=True)
    else:
        empty_need = pd.DataFrame([["-"] * m for _ in range(n)], index=proc_rows, columns=res_cols)
        st.dataframe(empty_need, use_container_width=True)

    # 7. System Status
    st.markdown("""
    <div class="card-box">
        <div class="sec-heading"><span class="sec-badge">7</span> System Status</div>
    </div>
    """, unsafe_allow_html=True)

    safety = st.session_state.safety_result
    if safety is None:
        st.markdown("""
        <div class="status-container">
            <span class="badge-safe-inactive">SAFE</span>
            <span style="color: #94a3b8; font-style: italic;">or</span>
            <span class="badge-unsafe-inactive">UNSAFE</span>
            <span class="status-subtext">one is shown per run</span>
        </div>
        """, unsafe_allow_html=True)
    elif safety.is_safe:
        st.markdown("""
        <div class="status-container">
            <span class="badge-safe-active">SAFE</span>
            <span class="status-subtext">one is shown per run</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-container">
            <span class="badge-unsafe-active">UNSAFE</span>
            <span class="status-subtext">one is shown per run</span>
        </div>
        """, unsafe_allow_html=True)

    # 8. Safe Sequence
    st.markdown("""
    <div class="card-box">
        <div class="sec-heading"><span class="sec-badge">8</span> Safe Sequence</div>
    </div>
    """, unsafe_allow_html=True)

    if safety is None:
        st.markdown('<div class="sequence-row"><span class="proc-none">"No safe sequence"</span></div>', unsafe_allow_html=True)
    elif safety.is_safe and safety.safe_sequence:
        chips_html = ' <span class="proc-arrow">➔</span> '.join(
            [f'<span class="proc-chip">P{p}</span>' for p in safety.safe_sequence]
        )
        st.markdown(f'<div class="sequence-row">{chips_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sequence-row"><span style="color: #dc2626; font-weight: 700; font-family: monospace;">No safe sequence exists</span></div>', unsafe_allow_html=True)

    # 9. Step-by-Step Trace
    st.markdown("""
    <div class="card-box">
        <div class="sec-heading"><span class="sec-badge">9</span> Step-by-Step Trace</div>
    </div>
    """, unsafe_allow_html=True)

    if safety is not None and len(safety.step_trace) > 1:
        trace_data = []
        for s in safety.step_trace:
            if s.step_number > 0:
                work_str = "(" + ",".join(map(str, s.work_after)) + ")"
                trace_data.append({
                    "Step": int(s.step_number),
                    "Process": f"P{s.candidate_process}",
                    "Need ≤ Work": "yes" if s.is_eligible else "no",
                    "Work after": work_str
                })
        if not safety.is_safe and safety.unfinished_processes:
            trace_data.append({
                "Step": len(trace_data) + 1,
                "Process": f"P{', P'.join(map(str, safety.unfinished_processes))}",
                "Need ≤ Work": "no",
                "Work after": f"({','.join(map(str, safety.final_work))}) [Stalled]"
            })
        st.dataframe(pd.DataFrame(trace_data), use_container_width=True, hide_index=True)
    else:
        # Placeholder matching wireframe
        placeholder_df = pd.DataFrame([
            {"Step": "-", "Process": "-", "Need ≤ Work": "-", "Work after": "-"}
        ])
        st.dataframe(placeholder_df, use_container_width=True, hide_index=True)

    # 10. Message line
    st.markdown("""
    <div class="card-box">
        <div class="sec-heading"><span class="sec-badge">10</span> Message line</div>
    </div>
    """, unsafe_allow_html=True)

    msg_str, msg_style = st.session_state.message
    if msg_style == "red":
        st.markdown(f'<div class="msg-display msg-display-red">{msg_str}</div>', unsafe_allow_html=True)
    elif msg_style == "green":
        st.markdown(f'<div class="msg-display msg-display-green">{msg_str}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-display msg-display-neutral">{msg_str}</div>', unsafe_allow_html=True)
