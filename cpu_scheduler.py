import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

class Process:
    def __init__(self, name, arrival_time, burst_time, priority=0, deadline=None):
        self.name = name
        self.arrival_time = arrival_time  # in seconds
        self.burst_time = burst_time      # in seconds
        self.remaining_time = burst_time
        self.priority = priority
        self.deadline = deadline
        self.start_time = None
        self.completion_time = None
        self.first_response_time = None

def calculate_metrics(processes):
    metrics = []
    total_turnaround = 0
    total_waiting = 0
    total_response = 0
    
    for process in processes:
        if process.completion_time is not None:
            turnaround_time = process.completion_time - process.arrival_time
            waiting_time = turnaround_time - process.burst_time
            response_time = process.first_response_time - process.arrival_time if process.first_response_time is not None else 0
            
            total_turnaround += turnaround_time
            total_waiting += waiting_time
            total_response += response_time
            
            metrics.append({
                'Process': process.name,
                'Turnaround Time (s)': turnaround_time,
                'Waiting Time (s)': waiting_time,
                'Response Time (s)': response_time
            })
    
    n = len(processes)
    if n > 0:
        metrics.append({
            'Process': 'Average',
            'Turnaround Time (s)': total_turnaround / n,
            'Waiting Time (s)': total_waiting / n,
            'Response Time (s)': total_response / n
        })
    
    return pd.DataFrame(metrics)

def create_gantt_chart(schedule):
    if not schedule:
        return None
    
    process_names = sorted(list(set(proc_name for _, _, proc_name in schedule)))
    fig = go.Figure()
    
    for start, end, proc_name in schedule:
        fig.add_trace(go.Bar(
            name=proc_name,
            y=[process_names.index(proc_name)],
            x=[end - start],
            base=[start],
            orientation='h',
            marker=dict(
                color=f'hsl({hash(proc_name) % 360}, 50%, 60%)'
            ),
            showlegend=False,
            hovertemplate=(
                f"Process: {proc_name}<br>" +
                "Start: %{base:d}s<br>" +
                "End: %{base:d}s + %{x:d}s<br>" +
                "Duration: %{x:d}s<extra></extra>"
            )
        ))
    
    fig.update_layout(
        title="Process Schedule Gantt Chart",
        xaxis_title="Time (seconds)",
        yaxis=dict(
            title="Processes",
            tickmode='array',
            tickvals=list(range(len(process_names))),
            ticktext=process_names,
            autorange="reversed"
        ),
        height=max(350, 50 * len(process_names) + 100),
        barmode='overlay',
        bargap=0.2,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)', zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)', zeroline=False)
    
    return fig


def fcfs(processes):
    schedule = []
    current_time = 0
    sorted_processes = sorted(processes, key=lambda x: x.arrival_time)
    
    for process in sorted_processes:
        if current_time < process.arrival_time:
            current_time = process.arrival_time
        
        process.start_time = current_time
        process.first_response_time = current_time
        process.completion_time = current_time + process.burst_time
        
        schedule.append((current_time, process.completion_time, process.name))
        current_time = process.completion_time
    
    return schedule

def sjf(processes):
    schedule = []
    current_time = 0
    remaining_processes = processes.copy()
    
    while remaining_processes:
        available_processes = [p for p in remaining_processes if p.arrival_time <= current_time]
        
        if not available_processes:
            current_time = min(p.arrival_time for p in remaining_processes)
            continue
        
        next_process = min(available_processes, key=lambda x: x.burst_time)
        next_process.start_time = current_time
        next_process.first_response_time = current_time
        next_process.completion_time = current_time + next_process.burst_time
        
        schedule.append((current_time, next_process.completion_time, next_process.name))
        current_time = next_process.completion_time
        remaining_processes.remove(next_process)
    
    return schedule

def srtf(processes):
    schedule = []
    current_time = 0
    remaining_processes = processes.copy()
    current_process = None
    last_process = None
    
    while remaining_processes or current_process:
        available_processes = [p for p in remaining_processes if p.arrival_time <= current_time]
        
        if not available_processes and not current_process:
            current_time = min(p.arrival_time for p in remaining_processes)
            continue
        
        if available_processes:
            next_process = min(available_processes, key=lambda x: x.remaining_time)
        else:
            next_process = current_process
            
        if current_process != next_process:
            if current_process:
                schedule.append((start_time, current_time, current_process.name))
            current_process = next_process
            start_time = current_time
            if current_process.first_response_time is None:
                current_process.first_response_time = current_time
        
        current_process.remaining_time -= 1
        current_time += 1
        
        if current_process.remaining_time == 0:
            schedule.append((start_time, current_time, current_process.name))
            current_process.completion_time = current_time
            remaining_processes.remove(current_process)
            current_process = None
    
    return schedule

def priority_scheduling(processes):
    schedule = []
    current_time = 0
    remaining_processes = processes.copy()
    
    while remaining_processes:
        available_processes = [p for p in remaining_processes if p.arrival_time <= current_time]
        
        if not available_processes:
            current_time = min(p.arrival_time for p in remaining_processes)
            continue
        
        next_process = max(available_processes, key=lambda x: x.priority)
        next_process.start_time = current_time
        next_process.first_response_time = current_time
        next_process.completion_time = current_time + next_process.burst_time
        
        schedule.append((current_time, next_process.completion_time, next_process.name))
        current_time = next_process.completion_time
        remaining_processes.remove(next_process)
    
    return schedule

def round_robin(processes, quantum):
    schedule = []
    current_time = 0
    remaining_processes = processes.copy()
    ready_queue = []
    
    while remaining_processes or ready_queue:
        # Add newly arrived processes to ready queue
        new_arrivals = [p for p in remaining_processes if p.arrival_time <= current_time]
        ready_queue.extend(new_arrivals)
        for p in new_arrivals:
            remaining_processes.remove(p)
        
        if not ready_queue:
            current_time = min(p.arrival_time for p in remaining_processes)
            continue
        
        current_process = ready_queue.pop(0)
        if current_process.first_response_time is None:
            current_process.first_response_time = current_time
        
        execution_time = min(quantum, current_process.remaining_time)
        schedule.append((current_time, current_time + execution_time, current_process.name))
        
        current_process.remaining_time -= execution_time
        current_time += execution_time
        
        # Add newly arrived processes during this quantum
        new_arrivals = [p for p in remaining_processes if p.arrival_time <= current_time]
        ready_queue.extend(new_arrivals)
        for p in new_arrivals:
            remaining_processes.remove(p)
        
        if current_process.remaining_time > 0:
            ready_queue.append(current_process)
        else:
            current_process.completion_time = current_time
    
    return schedule

def earliest_deadline_first(processes):
    schedule = []
    current_time = 0
    remaining_processes = processes.copy()
    
    while remaining_processes:
        available_processes = [p for p in remaining_processes if p.arrival_time <= current_time and p.deadline is not None]
        
        if not available_processes:
            current_time = min(p.arrival_time for p in remaining_processes)
            continue
        
        next_process = min(available_processes, key=lambda x: x.deadline)
        next_process.start_time = current_time
        next_process.first_response_time = current_time
        next_process.completion_time = current_time + next_process.burst_time
        
        schedule.append((current_time, next_process.completion_time, next_process.name))
        current_time = next_process.completion_time
        remaining_processes.remove(next_process)
    
    return schedule

def rate_monotonic(processes):
    # For simplicity, we'll use deadline as period
    schedule = []
    current_time = 0
    remaining_processes = processes.copy()
    
    while remaining_processes:
        available_processes = [p for p in remaining_processes if p.arrival_time <= current_time and p.deadline is not None]
        
        if not available_processes:
            current_time = min(p.arrival_time for p in remaining_processes)
            continue
        
        # In RM, priority is inverse to period (deadline)
        next_process = min(available_processes, key=lambda x: x.deadline)
        next_process.start_time = current_time
        next_process.first_response_time = current_time
        next_process.completion_time = current_time + next_process.burst_time
        
        schedule.append((current_time, next_process.completion_time, next_process.name))
        current_time = next_process.completion_time
        remaining_processes.remove(next_process)
    
    return schedule

def main():
    st.title("CPU Process Scheduling Simulator")
    
    # Process input section in sidebar
    with st.sidebar:
        st.header("Add New Process")
        
        process_name = st.text_input("Process Name", "P1")
        arrival_time = st.number_input("Arrival Time (seconds)", min_value=0, value=0)
        burst_time = st.number_input("Burst Time (seconds)", min_value=1, value=1)
        priority = st.number_input("Priority (higher = higher priority)", min_value=0, value=0)
        deadline = st.number_input("Deadline (seconds, optional)", min_value=0, value=0)
        
        if st.button("Add Process", use_container_width=True):
            if 'processes' not in st.session_state:
                st.session_state.processes = []
            new_process = Process(process_name, arrival_time, burst_time, priority, deadline)
            st.session_state.processes.append(new_process)
            st.success(f"Process {process_name} added successfully!")
        
        if st.button("Clear All Processes", use_container_width=True):
            st.session_state.processes = []
            st.success("All processes cleared!")
    
    # Main area - Current processes table (editable)
    if 'processes' in st.session_state and st.session_state.processes:
        st.header("Current Processes")
        
        # Convert processes to DataFrame
        process_data = [
            {
                "Name": p.name,
                "Arrival Time (s)": p.arrival_time,
                "Burst Time (s)": p.burst_time,
                "Priority": p.priority,
                "Deadline (s)": p.deadline if p.deadline > 0 else 0
            }
            for p in st.session_state.processes
        ]
        
        # Create editable dataframe
        edited_df = st.data_editor(
            pd.DataFrame(process_data),
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Name": st.column_config.TextColumn(
                    "Name",
                    help="Process identifier",
                    required=True,
                ),
                "Arrival Time (s)": st.column_config.NumberColumn(
                    "Arrival Time (s)",
                    help="Time when process arrives",
                    min_value=0,
                    required=True,
                ),
                "Burst Time (s)": st.column_config.NumberColumn(
                    "Burst Time (s)",
                    help="Time required for execution",
                    min_value=1,
                    required=True,
                ),
                "Priority": st.column_config.NumberColumn(
                    "Priority",
                    help="Process priority (higher = more important)",
                    min_value=0,
                    required=True,
                ),
                "Deadline (s)": st.column_config.NumberColumn(
                    "Deadline (s)",
                    help="Optional deadline for the process",
                    min_value=0,
                    required=True,
                ),
            },
            hide_index=True,
        )
        
        # Update processes list from edited dataframe
        if len(edited_df) > 0:
            st.session_state.processes = [
                Process(
                    row["Name"],
                    row["Arrival Time (s)"],
                    row["Burst Time (s)"],
                    row["Priority"],
                    row["Deadline (s)"]
                )
                for _, row in edited_df.iterrows()
            ]
    
    # Algorithm selection
    st.header("Select Scheduling Algorithm")
    algorithm = st.selectbox(
        "Choose the scheduling algorithm to simulate",
        ["First Come First Serve (FCFS)",
         "Shortest Job First (SJF)",
         "Shortest Remaining Time First (SRTF)",
         "Priority Scheduling",
         "Rate Monotonic Scheduling (RMS)",
         "Earliest Deadline First (EDF)",
         "Round Robin (RR)"]
    )
    
    if algorithm == "Round Robin (RR)":
        quantum = st.number_input("Time Quantum (seconds)", min_value=1, value=2)
    
    # Run simulation section
    if 'processes' in st.session_state and st.session_state.processes:
        if st.button("Run Simulation", use_container_width=True, type="primary"):
            simulation_processes = [
                Process(p.name, p.arrival_time, p.burst_time, p.priority, p.deadline)
                for p in st.session_state.processes
            ]
            
            # Run selected algorithm
            schedule = None
            if algorithm == "First Come First Serve (FCFS)":
                schedule = fcfs(simulation_processes)
            elif algorithm == "Shortest Job First (SJF)":
                schedule = sjf(simulation_processes)
            elif algorithm == "Shortest Remaining Time First (SRTF)":
                schedule = srtf(simulation_processes)
            elif algorithm == "Priority Scheduling":
                schedule = priority_scheduling(simulation_processes)
            elif algorithm == "Rate Monotonic Scheduling (RMS)":
                schedule = rate_monotonic(simulation_processes)
            elif algorithm == "Earliest Deadline First (EDF)":
                schedule = earliest_deadline_first(simulation_processes)
            elif algorithm == "Round Robin (RR)":
                schedule = round_robin(simulation_processes, quantum)
            
            if schedule:
                # Display Gantt chart
                st.subheader("Gantt Chart")
                gantt_chart = create_gantt_chart(schedule)
                st.plotly_chart(gantt_chart, use_container_width=True)
                
                # Display metrics
                st.subheader("Process Metrics")
                metrics_df = calculate_metrics(simulation_processes)
                st.dataframe(metrics_df, use_container_width=True)
    else:
        st.info("Add processes using the sidebar to begin simulation")

if __name__ == "__main__":
    main()