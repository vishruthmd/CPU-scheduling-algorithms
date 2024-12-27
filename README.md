# CPU Process Scheduling Simulator

This project is a **Streamlit-based web application** designed to simulate various CPU process scheduling algorithms. It allows users to define custom processes with attributes like arrival time, burst time, priority, and deadlines. The application runs simulations using popular scheduling algorithms and visualizes the results through a Gantt chart and performance metrics.

## Features

- **Interactive Process Input:** Add, edit, and clear processes using an intuitive sidebar and data editor.
- **Scheduling Algorithms Supported:**
  - First Come First Serve (FCFS)
  - Shortest Job First (SJF)
  - Shortest Remaining Time First (SRTF)
  - Priority Scheduling
  - Rate Monotonic Scheduling (RMS)
  - Earliest Deadline First (EDF)
  - Round Robin (RR) with customizable quantum.
- **Gantt Chart Visualization:** Displays the execution timeline of processes.
- **Metrics Calculation:** Provides process-level and average performance metrics:
  - Turnaround Time
  - Waiting Time
  - Response Time

## Requirements

- **Python 3.8 or above**
- **Packages:**
  - `streamlit`
  - `pandas`
  - `plotly`
  - `numpy`

Install the required packages using the command:

```bash
pip install -r requirements.txt
```

## How to Run

1. Clone this repository and navigate to the project directory.
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. Open the provided URL (default: `http://localhost:8501`) in a web browser.

## Steps

1. Add processes using the interactive sidebar.
2. Edit or clear processes as needed.
3. Choose a scheduling algorithm from the dropdown menu.
4. For Round Robin, specify the quantum.
5. Run the simulation and view the Gantt chart and metrics.
6. Analyze results to understand scheduling performance.

---

Enjoy using the CPU Process Scheduling Simulator! For questions or contributions, feel free to raise an issue or submit a pull request.

