import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Smart Production Dashboard Visualizer", layout="wide")

# -------------------------------
# CUSTOM STYLE (including calendar fix)
# -------------------------------
st.markdown("""
    <style>
    /* Main layout padding */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }

    /* Header alignment */
    h1 {
        margin-top: 10px !important;
        margin-bottom: 25px !important;
        text-align: center !important;
    }

    /* KPI layout spacing */
    .metric-section {
        margin-top: 0px !important;
        margin-bottom: 25px !important;
    }

    /* Chart title */
    .chart-title {
        font-size: 16px !important;
        font-weight: 600 !important;
        margin-bottom: 8px !important;
        margin-top: 12px !important;
        color: #E5E7EB !important;
    }

    footer {visibility: hidden;}
    .gear-icon {cursor: pointer; color: #ccc; font-size: 18px; transition: color 0.2s;}
    .gear-icon:hover {color: white;}

    /* Sidebar Maintenance */
    .maintenance-box {
        background: #1f2937;
        color: white;
        border-radius: 12px;
        padding: 10px;
        margin-top: 15px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.4);
        font-size: 14px;
    }
    .maintenance-title {
        color: #facc15;
        font-weight: bold;
        font-size: 15px;
        text-align: center;
        margin-bottom: 6px;
    }
    .maintenance-item {
        background: #374151;
        padding: 6px 8px;
        border-radius: 10px;
        margin-top: 5px;
    }
    .maintenance-item.good {color: #10B981;}
    .maintenance-item.warn {color: #F59E0B;}
    .maintenance-item.bad {color: #EF4444;}

    /* Calendar fix for dark mode */
    [data-baseweb="calendar"] div[role="heading"] {
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        text-transform: uppercase;
        text-align: center !important;
        margin-bottom: 4px !important;
    }
    [data-baseweb="calendar"] button {
        color: white !important;
    }
    .stDateInput label, .stDateInput span {
        color: white !important;
    }
    .stDateInput div[data-baseweb="calendar"] {
        background-color: #1E293B !important;
        color: white !important;
        border-radius: 8px;
    }
    .stDateInput button {
        color: white !important;
    }
    .stDateInput input {
        color: white !important;
        background-color: #111827 !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# LOAD DATA
# -------------------------------
st.cache_data.clear()  # reload updated CSV every time

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df.columns = df.columns.str.strip()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Machine"] = df["Machine"].astype(str).str.strip()
    return df

df = load_data()

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
st.sidebar.title("🎛️ Control Panel")

machines = ["All"] + sorted(df["Machine"].unique().tolist())
products = ["All"] + sorted(df["Product"].unique().tolist())
selected_machine = st.sidebar.selectbox("Select Machine", machines)
selected_product = st.sidebar.selectbox("Select Product", products)
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["Timestamp"].min().date(), df["Timestamp"].max().date()],
)

filtered_df = df[
    (df["Timestamp"].dt.date >= date_range[0])
    & (df["Timestamp"].dt.date <= date_range[-1])
]
if selected_machine != "All":
    filtered_df = filtered_df[filtered_df["Machine"] == selected_machine]
if selected_product != "All":
    filtered_df = filtered_df[filtered_df["Product"] == selected_product]

# -------------------------------
# SMART MAINTENANCE ALERTS
# -------------------------------
avg_def = filtered_df["Defects"].mean()
avg_down = filtered_df["Downtime"].mean()
avg_eff = (filtered_df["Units_Produced"].sum() - filtered_df["Defects"].sum()) / filtered_df["Units_Produced"].sum() * 100

maintenance_msgs = []
if avg_def > 5:
    worst_def_machine = filtered_df.groupby("Machine")["Defects"].mean().idxmax()
    maintenance_msgs.append(f"🧰 {worst_def_machine}: Quality degrading — inspection required.")
if avg_down > 2:
    worst_down_machine = filtered_df.groupby("Machine")["Downtime"].mean().idxmax()
    maintenance_msgs.append(f"🔧 {worst_down_machine}: Frequent downtime — schedule maintenance.")
if avg_eff < 70:
    low_eff_machine = filtered_df.groupby("Machine")["Efficiency"].mean().idxmin()
    maintenance_msgs.append(f"⚠️ {low_eff_machine}: Efficiency dropping — calibration needed.")
if not maintenance_msgs:
    maintenance_msgs.append("✅ All systems running optimally.")

st.sidebar.markdown("<div class='maintenance-box'>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='maintenance-title'>🧠 Smart Maintenance Alerts</div>", unsafe_allow_html=True)
for msg in maintenance_msgs:
    if "✅" in msg:
        st.sidebar.markdown(f"<div class='maintenance-item good'>{msg}</div>", unsafe_allow_html=True)
    elif "⚠️" in msg:
        st.sidebar.markdown(f"<div class='maintenance-item warn'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"<div class='maintenance-item bad'>{msg}</div>", unsafe_allow_html=True)
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1>🏭 Smart Production Dashboard Visualizer</h1>", unsafe_allow_html=True)

# -------------------------------
# SEMICIRCLE KPI GAUGES
# -------------------------------
def semicircle_gauge(title, value, min_val, max_val, color_scale, bg_contrast, suffix=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': suffix, 'font': {'color': 'white', 'size': 20}},
        title={'text': title, 'font': {'color': 'white', 'size': 15}},
        gauge={
            'axis': {'range': [min_val, max_val], 'visible': False},
            'bar': {'color': color_scale[-1], 'thickness': 0.35},
            'steps': [{'range': [min_val, max_val], 'color': bg_contrast}],
            'shape': 'angular',
        },
        domain={'x': [0, 1], 'y': [0, 0.5]}
    ))
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        height=160,
        paper_bgcolor="#0E1117",
        font={'color': 'white'}
    )
    return fig

# KPI Calculations
total_records = len(filtered_df)
avg_down = round(filtered_df["Downtime"].mean(), 2)
avg_def = round(filtered_df["Defects"].mean(), 2)
avg_eff = round(avg_eff, 2)
avg_prod = round(filtered_df["Units_Produced"].mean(), 2)

# KPI Gauges
st.markdown("<div class='metric-section'>", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.plotly_chart(semicircle_gauge("Total Records", total_records, 0, 100, ["#2563EB", "#3B82F6", "#60A5FA"], "#1E3A8A"), use_container_width=True)
with col2:
    st.plotly_chart(semicircle_gauge("Avg Efficiency", avg_eff, 0, 100, ["#10B981", "#34D399", "#6EE7B7"], "#064E3B", "%"), use_container_width=True)
with col3:
    st.plotly_chart(semicircle_gauge("Avg Downtime", avg_down, 0, 10, ["#EAB308", "#FACC15", "#CA8A04"], "#78350F", " min"), use_container_width=True)
with col4:
    st.plotly_chart(semicircle_gauge("Avg Defects", avg_def, 0, 10, ["#F87171", "#EF4444", "#DC2626"], "#7F1D1D"), use_container_width=True)
with col5:
    st.plotly_chart(semicircle_gauge("Avg Production", avg_prod, 0, 500, ["#2563EB", "#3B82F6", "#60A5FA"], "#1E3A8A"), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# MACHINE BREAKDOWN VIEW
# -------------------------------
if selected_machine != "All":
    st.markdown("### 🧩 Machine Breakdown Overview")
    machine_df = filtered_df[filtered_df["Machine"] == selected_machine]
    total_records = len(machine_df)
    total_defects = (machine_df["Defects"] > 0).sum()
    downtime_alerts = (machine_df["Downtime"] > 2).sum()
    service_needed = ((machine_df["Defects"] > 0) | (machine_df["Downtime"] > 2)).sum()

    breakdown = pd.DataFrame({
        "Metric": ["Total Records", "Defective Units", "Downtime Alerts", "Service Needed"],
        "Count": [total_records, total_defects, downtime_alerts, service_needed]
    })

    colA, colB = st.columns([1.2, 1])
    with colA:
        st.dataframe(breakdown, hide_index=True, use_container_width=True)
    with colB:
        st.bar_chart(breakdown.set_index("Metric"))

# -------------------------------
# CHART FUNCTIONS
# -------------------------------
def render_chart(df, x, y, color, chart_type):
    if chart_type == "Line":
        fig = px.line(df, x=x, y=y, color=color, markers=True)
    elif chart_type == "Bar":
        fig = px.bar(df, x=x, y=y, color=color)
    elif chart_type == "Area":
        fig = px.area(df, x=x, y=y, color=color)
    elif chart_type == "Scatter":
        fig = px.scatter(df, x=x, y=y, color=color)
    elif chart_type == "Pie":
        fig = px.pie(df, values=y, names=color)
    else:
        fig = px.line(df, x=x, y=y, color=color, markers=True)
    fig.update_layout(
        height=300,
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font_color="white",
        legend_title="Machine",
        margin=dict(t=30, l=10, r=10, b=10)
    )
    return fig

# -------------------------------
# CHART BLOCK FUNCTION
# -------------------------------
chart_types = ["Line", "Bar", "Area", "Scatter", "Pie"]

def chart_block(key, df, x, y, color, title):
    default_chart = st.session_state.get(f"{key}_type", "Line")
    header_col1, header_col2 = st.columns([8, 1])
    with header_col1:
        st.markdown(f"<div class='chart-title'>{title}</div>", unsafe_allow_html=True)
    with header_col2:
        with st.popover("", icon="⚙️", use_container_width=False):
            new_type = st.radio("Choose Chart Type", chart_types, index=chart_types.index(default_chart), key=f"charttype_{key}")
            if new_type != default_chart:
                st.session_state[f"{key}_type"] = new_type
                st.rerun()
    chart_type = st.session_state.get(f"{key}_type", default_chart)
    fig = render_chart(df, x, y, color, chart_type)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# DISPLAY CHARTS
# -------------------------------
chart1, chart2 = st.columns(2)
with chart1:
    chart_block("chart1", filtered_df, "Timestamp", "Units_Produced", "Machine", "Production Over Time")
with chart2:
    chart_block("chart2", filtered_df, "Timestamp", "Downtime", "Machine", "Downtime Trend")

chart3, chart4 = st.columns(2)
with chart3:
    chart_block("chart3", filtered_df, "Timestamp", "Efficiency", "Machine", "Efficiency Over Time")
with chart4:
    chart_block("chart4", filtered_df, "Timestamp", "Defects", "Machine", "Defects Over Time")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Developed by Team [Your Team Name] | MachDatum Hackathon 2025 ⚙️")
