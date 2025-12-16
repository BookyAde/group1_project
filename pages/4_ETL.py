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
import uuid

# Apply theme
try:
    from frontend.components.theme import WarehouseTheme
    WarehouseTheme.apply_theme()
except:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from frontend.components.theme import WarehouseTheme
    from frontend.components.sidebar import render_sidebar
    from frontend.utils.config import BACKEND_URL, TIMEOUT, SUPABASE_CREDS
except ImportError:
    class WarehouseTheme:
        @staticmethod
        def apply_global_styles(): pass
    def render_sidebar():
        with st.sidebar:
            st.write("🔄 ETL Monitor")
    BACKEND_URL = "http://localhost:8000/api/v1"
    TIMEOUT = 30
    SUPABASE_CREDS = {'available': False, 'url': '', 'key': ''}

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
# Helper Functions for Supabase
# --------------------------------------------------
def fetch_datasets_from_supabase():
    """Fetch datasets from Supabase for ETL sources"""
    try:
        if SUPABASE_CREDS.get('available'):
            headers = {
                'apikey': SUPABASE_CREDS['key'],
                'Authorization': f'Bearer {SUPABASE_CREDS["key"]}'
            }
            
            response = requests.get(
                f"{SUPABASE_CREDS['url']}/rest/v1/datasets",
                headers=headers,
                params={'select': '*', 'order': 'uploaded_at.desc'},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        st.error(f"Error fetching datasets: {str(e)[:100]}")
    return []

def simulate_etl_job(pipeline_type, sources=None):
    """Simulate ETL job for demo"""
    job_id = f"ETL-{str(uuid.uuid4())[:8]}"
    
    job = {
        'id': job_id,
        'name': f'{pipeline_type.title()} Pipeline',
        'type': pipeline_type,
        'status': 'running',
        'progress': 10,
        'started': datetime.now().isoformat(),
        'sources': sources or [],
        'triggered_by': st.session_state.user_email,
        'rows_processed': 0,
        'estimated_completion': (datetime.now() + timedelta(minutes=5)).isoformat()
    }
    
    # Add to session state
    if 'etl_jobs' not in st.session_state:
        st.session_state.etl_jobs = []
    st.session_state.etl_jobs.append(job)
    
    return job_id

def get_etl_jobs():
    """Get ETL jobs from session state"""
    return st.session_state.get('etl_jobs', [])

def get_etl_metrics():
    """Generate demo ETL metrics"""
    jobs = st.session_state.get('etl_jobs', [])
    
    completed = sum(1 for j in jobs if j.get('status') == 'completed')
    failed = sum(1 for j in jobs if j.get('status') == 'failed')
    running = sum(1 for j in jobs if j.get('status') == 'running')
    total = len(jobs)
    
    success_rate = (completed / total * 100) if total > 0 else 100
    
    # Calculate data volume based on jobs
    data_volume = sum(j.get('rows_processed', 0) * 0.000001 for j in jobs)  # Approx GB
    
    return {
        'jobs_today': total,
        'success_rate': round(success_rate, 1),
        'avg_processing_minutes': 3.5,
        'data_volume_gb': round(data_volume, 2),
        'active_jobs': running,
        'completed_jobs': completed,
        'failed_jobs': failed
    }

def simulate_job_progress():
    """Simulate progress for running jobs"""
    if 'etl_jobs' in st.session_state:
        for job in st.session_state.etl_jobs:
            if job.get('status') == 'running' and job.get('progress', 0) < 100:
                # Increment progress
                increment = np.random.randint(5, 25)
                job['progress'] = min(100, job.get('progress', 0) + increment)
                
                # Add rows processed
                if 'rows_processed' not in job:
                    job['rows_processed'] = 0
                job['rows_processed'] += increment * 100
                
                # Complete if reached 100%
                if job['progress'] == 100:
                    job['status'] = 'completed'
                    job['completed_at'] = datetime.now().isoformat()
                    # Ensure rows_processed is realistic
                    job['rows_processed'] = np.random.randint(5000, 50000)

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
        simulate_job_progress()
        st.rerun()
with col_refresh3:
    last_refresh = st.empty()

# Dashboard metrics
try:
    etl_metrics = get_etl_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        jobs_today = etl_metrics.get('jobs_today', 0)
        success_rate = etl_metrics.get('success_rate', 100)
        st.metric("Jobs Today", f"{jobs_today}", f"{success_rate}% success")
    
    with col2:
        active_jobs = etl_metrics.get('active_jobs', 0)
        st.metric("Active Jobs", f"{active_jobs}", "running")
    
    with col3:
        avg_time = etl_metrics.get('avg_processing_minutes', 3.5)
        st.metric("Avg Process Time", f"{avg_time:.1f}m", "per job")
    
    with col4:
        data_volume = etl_metrics.get('data_volume_gb', 0)
        st.metric("Data Processed", f"{data_volume:.2f} GB", "total")
        
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
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("▶️ Run Full Pipeline", use_container_width=True, type="primary"):
            datasets = fetch_datasets_from_supabase()
            source_names = [d.get('filename') for d in datasets[:3]] if datasets else ["Sample Data"]
            
            job_id = simulate_etl_job('full', source_names)
            st.success("✅ Full pipeline simulation started!")
            st.info(f"Processing {len(source_names)} datasets")
            st.rerun()
    
    with col_q2:
        if st.button("🔄 Incremental Update", use_container_width=True):
            job_id = simulate_etl_job('incremental', ['Recent Data Updates'])
            st.success("✅ Incremental update started!")
            st.rerun()
    
    with col_q3:
        if st.button("🧹 Data Cleanup", use_container_width=True):
            job_id = simulate_etl_job('cleanup', ['All Datasets'])
            st.success("✅ Data cleanup started!")
            st.rerun()
    
    with col_q4:
        if st.button("🎲 Demo Data", use_container_width=True):
            # Create demo ETL jobs
            demo_jobs = [
                {
                    'id': f'ETL-DEMO-{i}',
                    'name': f'Demo Pipeline {i}',
                    'type': ['full', 'incremental', 'cleanup'][i % 3],
                    'status': ['completed', 'failed', 'running'][i % 3],
                    'progress': [100, 45, 75][i % 3],
                    'started': (datetime.now() - timedelta(hours=i)).isoformat(),
                    'sources': ['sales_data.csv', 'user_logs.xlsx'][:i % 2 + 1],
                    'rows_processed': i * 10000,
                    'triggered_by': 'demo'
                }
                for i in range(1, 6)
            ]
            
            st.session_state.etl_jobs = demo_jobs
            st.success("✅ Generated 5 demo ETL jobs")
            st.rerun()

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
    
    # Fetch datasets from Supabase
    with st.spinner("Loading data sources from Supabase..."):
        datasets = fetch_datasets_from_supabase()
    
    if datasets:
        st.success(f"✅ Found {len(datasets)} datasets in Supabase")
        
        source_options = {d.get('filename', f"Dataset {d.get('id')}"): d.get('id') for d in datasets}
        
        selected_sources = st.multiselect(
            "Select data sources for ETL",
            list(source_options.keys()),
            default=list(source_options.keys())[:min(2, len(source_options))] if source_options else []
        )
        
        # Display selected sources
        if selected_sources:
            with st.expander("📋 Selected Sources", expanded=False):
                for source in selected_sources:
                    source_id = source_options[source]
                    source_data = next((d for d in datasets if d.get('id') == source_id), {})
                    st.markdown(f"**{source}**")
                    st.caption(f"Rows: {source_data.get('rows', 'N/A')} | Size: {source_data.get('size_mb', 'N/A')} MB | Uploaded: {source_data.get('uploaded_at', 'N/A')[:10]}")
        
        # ETL action for selected sources
        if selected_sources and st.button("🔄 Process Selected Sources", use_container_width=True, type="primary"):
            job_id = simulate_etl_job('selected', selected_sources)
            st.success(f"✅ Started ETL job for {len(selected_sources)} datasets")
            st.rerun()
            
    else:
        st.info("No datasets found in Supabase")
        st.markdown("""
        **To add data sources:**
        1. Go to **📁 Data Management** page
        2. Upload CSV/Excel files
        3. They will appear here as ETL sources
        """)
        
        if st.button("📁 Go to Data Management", use_container_width=True):
            st.switch_page("pages/2_Data.py")

st.markdown("---")

# --------------------------------------------------
# Active Jobs & History
# --------------------------------------------------
st.markdown("## ⚡ Job Execution History")

# Fetch ETL jobs
etl_jobs = get_etl_jobs()

if not etl_jobs:
    st.info("No ETL jobs found. Run a pipeline to see execution details.")
    st.markdown("""
    **Try these actions:**
    - Click **▶️ Run Full Pipeline** to start a demo job
    - Click **🎲 Demo Data** to generate sample ETL jobs
    - Upload datasets first, then process them
    """)
else:
    # Filter options
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Running", "Completed", "Failed", "Queued"]
        )
    
    with filter_col2:
        job_type_filter = st.selectbox(
            "Filter by type",
            ["All", "Full", "Incremental", "Cleanup", "Selected"]
        )
    
    with filter_col3:
        if st.button("🔄 Update Progress", use_container_width=True):
            simulate_job_progress()
            st.rerun()
    
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
                if job.get('sources'):
                    st.caption(f"Sources: {', '.join(job.get('sources', [])[:2])}{'...' if len(job.get('sources', [])) > 2 else ''}")
                
                # Format time
                started = job.get('started', '')
                if started and 'T' in started:
                    time_part = started.split('T')[1][:5]
                    date_part = started.split('T')[0]
                    st.caption(f"Started: {date_part} {time_part}")
            
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
                progress = job.get('progress', 0)
                st.progress(progress / 100, text=f"{progress}%")
            
            with col5:
                # Job info
                if job.get('rows_processed'):
                    st.caption(f"Rows: {job.get('rows_processed'):,}")
                if job.get('type'):
                    st.caption(f"Type: {job.get('type').title()}")
            
            with col6:
                # Action buttons
                if job.get('status', '').lower() == 'running':
                    if st.button("✅", key=f"complete_{job.get('id')}", help="Mark complete"):
                        for j in st.session_state.etl_jobs:
                            if j.get('id') == job.get('id'):
                                j['status'] = 'completed'
                                j['progress'] = 100
                                break
                        st.rerun()
                elif job.get('status', '').lower() == 'failed':
                    if st.button("🔄", key=f"retry_{job.get('id')}", help="Retry job"):
                        new_job = job.copy()
                        new_job['status'] = 'running'
                        new_job['progress'] = 10
                        new_job['started'] = datetime.now().isoformat()
                        st.session_state.etl_jobs.append(new_job)
                        st.rerun()
                elif job.get('status', '').lower() == 'completed':
                    if st.button("🗑️", key=f"remove_{job.get('id')}", help="Remove"):
                        st.session_state.etl_jobs = [j for j in st.session_state.etl_jobs if j.get('id') != job.get('id')]
                        st.rerun()
            
            st.markdown("---")

# --------------------------------------------------
# Performance Analytics
# --------------------------------------------------
st.markdown("## 📈 Performance Analytics")

# Get metrics
metrics_data = get_etl_metrics()

if st.session_state.etl_jobs:
    analytic_col1, analytic_col2 = st.columns(2)
    
    with analytic_col1:
        # Success rate chart
        jobs_by_status = {}
        for job in st.session_state.etl_jobs:
            status = job.get('status', 'unknown').title()
            jobs_by_status[status] = jobs_by_status.get(status, 0) + 1
        
        if jobs_by_status:
            fig1 = go.Figure(data=[
                go.Pie(
                    labels=list(jobs_by_status.keys()),
                    values=list(jobs_by_status.values()),
                    hole=.3,
                    marker_colors=['#28A745', '#17A2B8', '#DC3545', '#FFC107']
                )
            ])
            fig1.update_layout(
                title="Job Status Distribution",
                height=300
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with analytic_col2:
        # Processing time trend
        recent_jobs = st.session_state.etl_jobs[-min(8, len(st.session_state.etl_jobs)):]
        job_names = [j.get('id')[:8] for j in recent_jobs]
        progress_values = [j.get('progress', 0) for j in recent_jobs]
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=job_names,
            y=progress_values,
            name='Progress %',
            marker_color='#FFD700'
        ))
        fig2.update_layout(
            title="Recent Job Progress",
            height=300,
            yaxis_title="Progress %",
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig2, use_container_width=True)
else:
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

# Get failed jobs
failed_jobs = [j for j in st.session_state.get('etl_jobs', []) if j.get('status') == 'failed']

if failed_jobs:
    error_count = len(failed_jobs)
    st.warning(f"Found {error_count} failed job(s)")
    
    # Show failed jobs
    for job in failed_jobs[:3]:
        with st.expander(f"❌ {job.get('id', 'Unknown')} - {job.get('name', 'Unknown Job')}", expanded=False):
            st.error(f"**Job failed at {job.get('progress', 0)}% progress**")
            
            st.caption(f"Type: {job.get('type', 'Unknown')}")
            st.caption(f"Started: {job.get('started', 'Unknown')}")
            
            if job.get('sources'):
                st.caption(f"Sources: {', '.join(job.get('sources'))}")
            
            # Retry button
            if st.button("🔄 Retry This Job", key=f"retry_failed_{job.get('id')}"):
                new_job = job.copy()
                new_job['status'] = 'running'
                new_job['progress'] = 10
                new_job['started'] = datetime.now().isoformat()
                st.session_state.etl_jobs.append(new_job)
                st.success(f"Retrying job {job.get('id')}")
                st.rerun()
    
    if error_count > 3:
        st.info(f"... and {error_count - 3} more failed jobs")
else:
    st.success("✅ No failed jobs!")

st.markdown("---")

# --------------------------------------------------
# System Health
# --------------------------------------------------
st.markdown("## 🏥 System Health Status")

health_col1, health_col2, health_col3, health_col4 = st.columns(4)

with health_col1:
    # Supabase connection check
    try:
        if SUPABASE_CREDS.get('available'):
            headers = {
                'apikey': SUPABASE_CREDS['key'],
                'Authorization': f'Bearer {SUPABASE_CREDS["key"]}'
            }
            
            response = requests.get(
                f"{SUPABASE_CREDS['url']}/rest/v1/datasets",
                headers=headers,
                params={'limit': '1'},
                timeout=3
            )
            
            if response.status_code == 200:
                supabase_status = "🟢 Online"
                datasets = fetch_datasets_from_supabase()
                supabase_msg = f"{len(datasets)} datasets"
            else:
                supabase_status = "🔴 Error"
                supabase_msg = f"HTTP {response.status_code}"
        else:
            supabase_status = "⚪ Offline"
            supabase_msg = "Not configured"
            
    except:
        supabase_status = "🔴 Offline"
        supabase_msg = "Connection failed"
    
    st.metric("Supabase", supabase_status, supabase_msg)

with health_col2:
    # ETL service status
    active_jobs = sum(1 for j in st.session_state.get('etl_jobs', []) if j.get('status') == 'running')
    total_jobs = len(st.session_state.get('etl_jobs', []))
    
    if active_jobs > 0:
        etl_status = "🟢 Active"
        etl_msg = f"{active_jobs} running"
    elif total_jobs > 0:
        etl_status = "🟡 Idle"
        etl_msg = f"{total_jobs} total"
    else:
        etl_status = "⚪ Inactive"
        etl_msg = "No jobs"
    
    st.metric("ETL Service", etl_status, etl_msg)

with health_col3:
    # Simulated CPU
    cpu_usage = np.random.randint(20, 60)
    cpu_trend = np.random.choice(['-', '+']) + str(np.random.randint(1, 5))
    st.metric("CPU Usage", f"{cpu_usage}%", cpu_trend)

with health_col4:
    # Simulated Memory
    memory_usage = np.random.randint(40, 80)
    memory_trend = np.random.choice(['-', '+']) + str(np.random.randint(1, 10))
    st.metric("Memory Usage", f"{memory_usage}%", memory_trend)

# Auto-refresh logic
if auto_refresh:
    simulate_job_progress()
    time.sleep(30)
    st.rerun()
else:
    last_refresh.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")

st.markdown("---")
st.caption(f"🔄 ETL Monitor • {len(st.session_state.get('etl_jobs', []))} jobs • User: {st.session_state.user_email} • {datetime.now().strftime('%H:%M:%S')}")