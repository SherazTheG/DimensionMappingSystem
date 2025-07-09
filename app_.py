import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pickle
import serial
import serial.tools.list_ports
import threading
import time
from collections import deque

# Load trained model
with open(r'C:\Users\Sheraz\Documents\pythontest\project_all_ml\Mini Project\model.pkl', 'rb') as f:
    model = pickle.load(f)

st.set_page_config(page_title="Box Size Classifier", layout="wide")
st.title("📦 Real-Time Box Size Classifier from 3D Sensor Data")

# UI: Serial port selection
st.markdown("### 🔌 Serial Port Setup")
ports = [port.device for port in serial.tools.list_ports.comports()]
selected_port = st.selectbox("Select from available ports", ports, index=0 if ports else -1)
custom_port = st.text_input("Or manually enter port (e.g., COM20)", "")
active_port = custom_port if custom_port else selected_port

start_button = st.button("🚀 Start Streaming")
stop_button = st.button("🛑 Stop Streaming")

# Setup session state
if "stop_flag" not in st.session_state:
    st.session_state["stop_flag"] = threading.Event()
if "thread" not in st.session_state:
    st.session_state["thread"] = None
if "point_buffer" not in st.session_state:
    st.session_state["point_buffer"] = deque(maxlen=1000)

stop_flag = st.session_state["stop_flag"]
point_buffer = st.session_state["point_buffer"]

# Serial reader thread
def serial_reader(port):
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        while not stop_flag.is_set():
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("Point:"):
                try:
                    parts = line.replace("Point:", "").split()
                    x = float(parts[0].split('=')[1])
                    y = float(parts[1].split('=')[1])
                    z = float(parts[2].split('=')[1])
                    point_buffer.append([x, y, z])
                except:
                    continue
        ser.close()
    except Exception as e:
        st.error(f"❌ Error reading from serial port: {e}")

# Handle Start
if start_button and active_port:
    if st.session_state["thread"] is None or not st.session_state["thread"].is_alive():
        stop_flag.clear()
        t = threading.Thread(target=serial_reader, args=(active_port,), daemon=True)
        t.start()
        st.session_state["thread"] = t
        st.success(f"✅ Streaming started on {active_port}")

# Handle Stop
if stop_button:
    stop_flag.set()
    st.success("🛑 Streaming stopped.")

# Live display and prediction
if point_buffer:
    df = pd.DataFrame(list(point_buffer), columns=['x', 'y', 'z'])

    if len(df) >= 30:
        # 3D Point Cloud Plot
        fig = go.Figure(data=[go.Scatter3d(
            x=df['x'], y=df['y'], z=df['z'],
            mode='markers',
            marker=dict(size=3, color='blue')
        )])
        fig.update_layout(
            scene=dict(
                xaxis_title='X (Breadth)',
                yaxis_title='Y (Height)',
                zaxis_title='Z (Width)'
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

        # Calculate Dimensions
        breadth = df['x'].max() - df['x'].min()
        width   = df['z'].max() - df['z'].min()
        height  = df['y'].max() - df['y'].min()

        st.markdown(f"""
        ### 📏 Calculated Dimensions:
        - Breadth: **{breadth:.2f} cm**
        - Width: **{width:.2f} cm**
        - Height: **{height:.2f} cm**
        """)

        # Prediction
        input_data = np.array([[breadth, width, height]])
        prediction = model.predict(input_data)[0]
        st.success(f"✅ Predicted Box Size: **{prediction}**")
    else:
        st.info("⏳ Waiting for more sensor data (≥ 30 points)...")
else:
    st.warning("📡 No sensor data received yet. Is your Arduino sending 'Point: X=... Y=... Z=...'?")
