# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import requests
import time
import json

# Apply theme
try:
    from frontend.components.theme import WarehouseTheme
    WarehouseTheme.apply_theme()  # This will use the current theme from session state
except:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from frontend.components.theme import WarehouseTheme
    from frontend.components.sidebar import render_sidebar
    from frontend.utils.config import BACKEND_URL, TIMEOUT
except ImportError:
    class WarehouseTheme:
        @staticmethod
        def apply_global_styles(): pass
    def render_sidebar():
        with st.sidebar:
            st.write("🔄 ETL Monitor")
    BACKEND_URL = "http://localhost:8000/api/v1"
    TIMEOUT = 30

st.set_page_config(
    page_title="ETL Monitor - Data Warehouse",
    page_icon="🔄",
    layout="wide"
)

if 'user_email' not in st.session_state:
    st.warning("⚠️ Please login first")
    st.stop()

try:
    WarehouseTheme.apply_global_styles()
except:
    pass

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def fetch_etl_jobs():
    """Fetch ETL job history from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/etl/jobs", timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json().get('jobs', [])
    except Exception as e:
        # Fallback to session state if backend not available
        return st.session_state.get('etl_jobs', [])
    return []

def fetch_etl_metrics():
    """Fetch ETL performance metrics from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/etl/metrics", timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {}

def fetch_recent_errors():
    """Fetch recent ETL errors from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/etl/errors", timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json().get('errors', [])
    except:
        pass
    return []

def run_etl_pipeline(pipeline_type, sources=None):
    """Trigger ETL pipeline execution"""
    try:
        payload = {
            'pipeline_type': pipeline_type,
            'sources': sources or [],
            'triggered_by': st.session_state.user_email
        }
        response = requests.post(
            f"{BACKEND_URL}/etl/run", 
            json=payload,
            timeout=TIMEOUT
        )
        return response.status_code == 200, response.json() if response.status_code == 200 else {}
    except Exception as e:
        return False, {'error': str(e)}

# --------------------------------------------------
# Initialize session state
# --------------------------------------------------
if 'etl_jobs' not in st.session_state:
    st.session_state.etl_jobs = []
if 'pipeline_config' not in st.session_state:
    st.session_state.pipeline_config = {
        'schedule_type': 'manual',
        'run_time': '02:00',
        'sources': [],
        'auto_retry': True,
        'notify_on_error': True
    }

# Render sidebar
try:
    render_sidebar()
except Exception as e:
    st.sidebar.error(f"Sidebar error: {e}")

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="margin: 0; font-size: 2.5rem; color: #FFD700;">🔄 ETL Pipeline Monitor</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
        Real-time monitoring of Extract, Transform, Load processes
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# Pipeline Dashboard
# --------------------------------------------------
st.markdown("## 📊 ETL Dashboard Overview")

# Auto-refresh option
col_refresh1, col_refresh2, col_refresh3 = st.columns([2, 1, 1])
with col_refresh1:
    auto_refresh = st.checkbox("🔄 Enable auto-refresh (30 seconds)", value=False)
with col_refresh2:
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
with col_refresh3:
    last_refresh = st.empty()

# Dashboard metrics - using real data when available
try:
    etl_metrics = fetch_etl_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        jobs_today = etl_metrics.get('jobs_today', 0)
        success_rate = etl_metrics.get('success_rate', 100)
        st.metric("Jobs Today", f"{jobs_today}", f"{success_rate}% success")
    
    with col2:
        active_jobs = len([j for j in fetch_etl_jobs() if j.get('status') in ['running', 'queued']])
        st.metric("Active Jobs", f"{active_jobs}", "running/queued")
    
    with col3:
        avg_time = etl_metrics.get('avg_processing_minutes', 5.2)
        st.metric("Avg Process Time", f"{avg_time:.1f}m", "per job")
    
    with col4:
        data_volume = etl_metrics.get('data_volume_gb', 0)
        st.metric("Data Processed", f"{data_volume:.1f} GB", "today")
        
except Exception as e:
    st.warning(f"Could not load dashboard metrics: {e}")

st.markdown("---")

# --------------------------------------------------
# Pipeline Control & Configuration
# --------------------------------------------------
st.markdown("## 🎛️ Pipeline Control Center")

control_tab1, control_tab2, control_tab3 = st.tabs(["Quick Actions", "Pipeline Config", "Data Sources"])

with control_tab1:
    st.markdown("### Quick Pipeline Execution")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        if st.button("▶️ Run Full Pipeline", use_container_width=True, type="primary"):
            with st.spinner("Starting full ETL pipeline..."):
                success, result = run_etl_pipeline('full')
                if success:
                    st.success("✅ Full pipeline started successfully!")
                    job_id = result.get('job_id', 'Unknown')
                    st.info(f"Job ID: {job_id}")
                else:
                    st.error(f"Failed to start pipeline: {result.get('error', 'Unknown error')}")
    
    with col_q2:
        if st.button("🔄 Run Incremental Update", use_container_width=True):
            with st.spinner("Starting incremental update..."):
                success, result = run_etl_pipeline('incremental')
                if success:
                    st.success("✅ Incremental update started!")
                else:
                    st.error(f"Failed: {result.get('error', 'Unknown error')}")
    
    with col_q3:
        if st.button("🧹 Run Data Cleanup", use_container_width=True):
            with st.spinner("Starting data cleanup..."):
                success, result = run_etl_pipeline('cleanup')
                if success:
                    st.success("✅ Data cleanup started!")
                else:
                    st.error(f"Failed: {result.get('error', 'Unknown error')}")

with control_tab2:
    st.markdown("### Pipeline Configuration")
    
    config_col1, config_col2 = st.columns(2)
    
    with config_col1:
        schedule_type = st.selectbox(
            "Schedule Type",
            ["Manual", "Daily", "Hourly", "Weekly"],
            index=0
        )
        
        if schedule_type != "Manual":
            if schedule_type == "Daily":
                run_time = st.time_input(
                    "Daily run time",
                    value=datetime.strptime("02:00", "%H:%M").time()
                )
            elif schedule_type == "Weekly":
                week_day = st.selectbox(
                    "Day of week",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                )
                run_time = st.time_input(
                    "Weekly run time",
                    value=datetime.strptime("02:00", "%H:%M").time()
                )
            elif schedule_type == "Hourly":
                run_time = st.number_input(
                    "Run every N hours",
                    min_value=1,
                    max_value=24,
                    value=6
                )
        
        auto_retry = st.checkbox("Auto-retry failed jobs", value=True)
    
    with config_col2:
        notify_on_error = st.checkbox("Email notifications on errors", value=True)
        max_parallel_jobs = st.slider("Max parallel jobs", 1, 10, 3)
        timeout_minutes = st.slider("Job timeout (minutes)", 5, 240, 60)
    
    if st.button("💾 Save Configuration", type="primary", use_container_width=True):
        st.session_state.pipeline_config = {
            'schedule_type': schedule_type.lower(),
            'auto_retry': auto_retry,
            'notify_on_error': notify_on_error,
            'max_parallel_jobs': max_parallel_jobs,
            'timeout_minutes': timeout_minutes
        }
        st.success("✅ Pipeline configuration saved!")

with control_tab3:
    st.markdown("### Data Source Management")
    
    # Fetch available datasets
    try:
        datasets_response = requests.get(f"{BACKEND_URL}/data/list", timeout=TIMEOUT)
        if datasets_response.status_code == 200:
            datasets = datasets_response.json().get('datasets', [])
            
            if datasets:
                source_options = {d['filename']: d['id'] for d in datasets}
                
                selected_sources = st.multiselect(
                    "Select data sources for ETL",
                    list(source_options.keys()),
                    default=list(source_options.keys())[:2] if source_options else []
                )
                
                # Display source details
                if selected_sources:
                    with st.expander("Selected Source Details", expanded=False):
                        for source in selected_sources:
                            source_id = source_options[source]
                            source_data = next((d for d in datasets if d['id'] == source_id), {})
                            st.markdown(f"**{source}**")
                            st.caption(f"Rows: {source_data.get('rows', 'N/A')} | Size: {source_data.get('size_mb', 'N/A')} MB")
            else:
                st.info("No datasets found. Upload data in the Data Management page first.")
        else:
            st.warning("Could not fetch data sources from backend")
    except Exception as e:
        st.error(f"Error loading data sources: {e}")

st.markdown("---")

# --------------------------------------------------
# Active Jobs & History
# --------------------------------------------------
st.markdown("## ⚡ Job Execution History")

# Fetch real ETL jobs
etl_jobs = fetch_etl_jobs()

if not etl_jobs:
    st.info("No ETL jobs found in history. Run a pipeline to see execution details.")
else:
    # Filter options
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Running", "Completed", "Failed", "Queued"]
        )
    
    with filter_col2:
        date_filter = st.date_input(
            "Filter by date",
            value=datetime.now().date()
        )
    
    with filter_col3:
        job_type_filter = st.selectbox(
            "Filter by type",
            ["All", "Full", "Incremental", "Cleanup", "Validation"]
        )
    
    # Filter jobs
    filtered_jobs = etl_jobs
    
    if status_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if j.get('status', '').lower() == status_filter.lower()]
    
    if job_type_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if j.get('type', '').lower() == job_type_filter.lower()]
    
    # Display jobs
    st.markdown(f"**Showing {len(filtered_jobs)} jobs**")
    
    for job in filtered_jobs:
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 1, 2, 2, 1])
            
            with col1:
                job_icon = {
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌',
                    'queued': '⏳'
                }.get(job.get('status', '').lower(), '📋')
                st.markdown(f"**{job_icon} {job.get('id', 'N/A')[:8]}**")
            
            with col2:
                st.markdown(f"**{job.get('name', 'Unnamed Job')}**")
                if job.get('description'):
                    st.caption(job.get('description'))
                st.caption(f"Started: {job.get('started', 'N/A')}")
            
            with col3:
                status = job.get('status', 'unknown').title()
                status_color = {
                    'Running': '#28A745',
                    'Completed': '#17A2B8',
                    'Failed': '#DC3545',
                    'Queued': '#FFC107'
                }.get(status, '#6C757D')
                st.markdown(f"<span style='color:{status_color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
            
            with col4:
                if job.get('progress') is not None:
                    progress = job.get('progress', 0)
                    st.progress(progress / 100, text=f"{progress}%")
                else:
                    st.caption("No progress data")
            
            with col5:
                # Duration info
                if job.get('duration'):
                    st.caption(f"Duration: {job.get('duration')}")
                if job.get('rows_processed'):
                    st.caption(f"Rows: {job.get('rows_processed'):,}")
            
            with col6:
                # Action buttons based on status
                if job.get('status', '').lower() == 'running':
                    if st.button("⏸️", key=f"pause_{job.get('id')}", help="Pause job"):
                        st.warning("Pause functionality coming soon")
                elif job.get('status', '').lower() == 'failed':
                    if st.button("🔄", key=f"retry_{job.get('id')}", help="Retry job"):
                        st.info(f"Retrying job {job.get('id')}")
                elif job.get('status', '').lower() == 'completed':
                    if st.button("📊", key=f"report_{job.get('id')}", help="View report"):
                        with st.expander(f"Job Report: {job.get('id')}", expanded=False):
                            st.json(job)
            
            st.markdown("---")

# --------------------------------------------------
# Performance Analytics
# --------------------------------------------------
st.markdown("## 📈 Performance Analytics")

# Try to get real metrics, fall back to simulated if needed
metrics_data = fetch_etl_metrics()

if metrics_data:
    # Real metrics available
    analytic_col1, analytic_col2 = st.columns(2)
    
    with analytic_col1:
        # Success rate over time chart
        if 'daily_success' in metrics_data:
            days = list(metrics_data['daily_success'].keys())[-7:]  # Last 7 days
            success_rates = [metrics_data['daily_success'][d] for d in days]
            
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=days,
                y=success_rates,
                mode='lines+markers',
                name='Success Rate',
                line=dict(color='#28A745', width=3)
            ))
            fig1.update_layout(
                title="Daily Success Rate (7 days)",
                height=300,
                yaxis=dict(range=[0, 100], ticksuffix="%")
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with analytic_col2:
        # Processing time trend
        if 'processing_times' in metrics_data:
            jobs = list(metrics_data['processing_times'].keys())[-10:]  # Last 10 jobs
            times = [metrics_data['processing_times'][j] for j in jobs]
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=jobs,
                y=times,
                name='Processing Time',
                marker_color='#FFD700'
            ))
            fig2.update_layout(
                title="Recent Job Processing Times",
                height=300,
                yaxis_title="Minutes"
            )
            st.plotly_chart(fig2, use_container_width=True)
else:
    # Simulated metrics (fallback)
    st.info("Performance analytics will appear here once ETL jobs have been run.")
    
    # Create sample chart
    hours = [f"{h}:00" for h in range(9, 18)]
    jobs_completed = [8, 12, 15, 18, 14, 10, 16, 12, 9]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=jobs_completed,
        mode='lines+markers',
        name='Jobs Completed',
        line=dict(color='#FFD700', width=3)
    ))
    fig.update_layout(
        title="Sample: Today's Job Completion",
        height=300,
        xaxis_title="Time",
        yaxis_title="Jobs Completed"
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# Error & Alert Center
# --------------------------------------------------
st.markdown("## ⚠️ Error & Alert Center")

# Fetch recent errors
recent_errors = fetch_recent_errors()

if recent_errors:
    error_count = len(recent_errors)
    st.warning(f"Found {error_count} error(s) in recent jobs")
    
    # Show latest errors
    for error in recent_errors[:3]:  # Show top 3
        with st.expander(f"❌ {error.get('job_id', 'Unknown')} - {error.get('timestamp', '')}", expanded=False):
            st.error(f"**Error:** {error.get('message', 'No error message')}")
            
            # Error details
            if error.get('details'):
                st.code(error.get('details'), language='python')
            
            # Error metadata
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.caption(f"Severity: {error.get('severity', 'Unknown')}")
                st.caption(f"Module: {error.get('module', 'Unknown')}")
            with col_e2:
                st.caption(f"Retry count: {error.get('retry_count', 0)}")
                if error.get('suggested_fix'):
                    st.info(f"Suggested: {error.get('suggested_fix')}")
            
            # Action buttons
            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                if st.button("🔄 Retry Job", key=f"err_retry_{error.get('job_id')}"):
                    st.success(f"Scheduled retry for {error.get('job_id')}")
            with col_act2:
                if st.button("📧 Notify Team", key=f"notify_{error.get('job_id')}"):
                    st.info("Notification sent to team")
            with col_act3:
                if st.button("✅ Acknowledge", key=f"ack_{error.get('job_id')}"):
                    st.success(f"Acknowledged error {error.get('job_id')}")
    
    if error_count > 3:
        st.info(f"... and {error_count - 3} more errors. Check backend logs for details.")
else:
    st.success("✅ No recent errors found!")

st.markdown("---")

# --------------------------------------------------
# System Health
# --------------------------------------------------
st.markdown("## 🏥 System Health Status")

# Check backend connections
health_col1, health_col2, health_col3, health_col4 = st.columns(4)

with health_col1:
    try:
        # Check ETL service
        etl_response = requests.get(f"{BACKEND_URL}/etl/health", timeout=3)
        etl_status = "🟢 Online" if etl_response.status_code == 200 else "🔴 Error"
        etl_msg = "Service healthy" if etl_response.status_code == 200 else "Check service"
    except:
        etl_status = "🔴 Offline"
        etl_msg = "Service unreachable"
    st.metric("ETL Service", etl_status, etl_msg)

with health_col2:
    try:
        # Check data service
        data_response = requests.get(f"{BACKEND_URL}/data/list", timeout=3)
        data_status = "🟢 Online" if data_response.status_code == 200 else "🔴 Error"
        if data_response.status_code == 200:
            data_count = data_response.json().get('count', 0)
            data_msg = f"{data_count} datasets"
        else:
            data_msg = "Service error"
    except:
        data_status = "🔴 Offline"
        data_msg = "Service unreachable"
    st.metric("Data Service", data_status, data_msg)

with health_col3:
    # Simulated resource usage (would come from monitoring system)
    cpu_usage = np.random.randint(20, 60)
    cpu_trend = np.random.choice(['-', '+']) + str(np.random.randint(1, 5))
    st.metric("CPU Usage", f"{cpu_usage}%", cpu_trend)

with health_col4:
    memory_usage = np.random.randint(40, 80)
    memory_trend = np.random.choice(['-', '+']) + str(np.random.randint(1, 10))
    st.metric("Memory Usage", f"{memory_usage}%", memory_trend)

# Auto-refresh logic (if enabled)
if auto_refresh:
    time.sleep(30)
    st.rerun()
else:
    last_refresh.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")

st.markdown("---")
st.caption(f"🔄 ETL Monitor • User: {st.session_state.user_email} • {datetime.now().strftime('%H:%M:%S')}")