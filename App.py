import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os

# Load trained classification model
with open(r'C:\Users\Sheraz\Documents\pythontest\project_all_ml\Mini Project\model.pkl', 'rb') as f:
    model = pickle.load(f)

st.title("📦 Automatic Box Size Classifier from Sensor Data")

# File uploader
uploaded_file = st.file_uploader("Upload your 3D point cloud data (.csv)", type=['csv'])

if uploaded_file is not None:
    # Load data and compute dimensions
    df = pd.read_csv(uploaded_file, header=None)
    df.columns = ['x', 'y', 'z']

    # Calculate bounding box dimensions
    breadth = df['x'].max() - df['x'].min()
    width   = df['z'].max() - df['z'].min()
    height  = df['y'].max() - df['y'].min()

    st.markdown("### 📏 Extracted Dimensions (in cm):")
    st.write(f"- Breadth: **{breadth:.2f} cm**")
    st.write(f"- Width: **{width:.2f} cm**")
    st.write(f"- Height: **{height:.2f} cm**")

    # Predict using model
    input_data = np.array([[breadth, width, height]])
    prediction = model.predict(input_data)[0]

    st.success(f"✅ Predicted Box Size: **{prediction}**")

    # Optional: Show 3D plot
    with st.expander("📊 Show 3D Point Cloud"):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(df['x'], df['y'], df['z'], c='blue', s=3)

        ax.set_xlabel('X (Breadth)')
        ax.set_ylabel('Y (Height)')
        ax.set_zlabel('Z (Width)')
        ax.set_title('3D Point Cloud of Object')

        st.pyplot(fig)

