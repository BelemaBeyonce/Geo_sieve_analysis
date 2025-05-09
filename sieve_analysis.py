import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis

st.set_page_config(page_title="GeoSieve Analyzer", layout="centered")
st.title("🌍 GeoSieve Analyzer")
st.write("Choose to use sample data or upload your sieve analysis CSV file.")

# --- Toggle Switch ---
use_sample = st.toggle("Use sample data (uncheck to upload your CSV)", value=True)

# --- Sample or Upload ---
if use_sample:
    st.subheader("🧪 Using Sample Sieve Analysis Data")
    data = {
        "Sieve Size (mm)": [4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.075, 0],
        "Weight Retained (g)": [100, 150, 180, 120, 90, 40, 10, 5]
    }
    df = pd.DataFrame(data)
else:
    st.subheader("📤 Upload Your Sieve Analysis CSV")
    with st.expander("📄 Expected Format"):
        st.code("Sieve Size (mm),Weight Retained (g)\n4.75,100\n2.36,150\n...\nPan,5")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = ["Sieve Size (mm)", "Weight Retained (g)"]
            df["Sieve Size (mm)"] = df["Sieve Size (mm)"].replace({"Pan": 0}).astype(float)
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.stop()
    else:
        st.warning("Please upload a file or enable sample data.")
        st.stop()

# --- Analysis ---
df = df.sort_values("Sieve Size (mm)", ascending=False)
total_weight = df["Weight Retained (g)"].sum()
df["% Retained"] = (df["Weight Retained (g)"] / total_weight) * 100
df["Cumulative % Retained"] = df["% Retained"].cumsum()
df["% Passing"] = 100 - df["Cumulative % Retained"]

def get_d_value(percent):
    return np.interp(percent, df["% Passing"][::-1], df["Sieve Size (mm)"][::-1])

D10 = get_d_value(10)
D30 = get_d_value(30)
D60 = get_d_value(60)
Cu = D60 / D10
Cc = (D30 ** 2) / (D10 * D60)

# --- Classification ---
if Cu > 4 and 1 < Cc < 3:
    classification = "Well-graded gravel (GW)"
elif Cu > 6 and 1 < Cc < 3:
    classification = "Well-graded sand (SW)"
else:
    classification = "Poorly graded (GP/SP)"

# --- Skewness & Kurtosis ---
skewness = skew(df["% Passing"])
kurt = kurtosis(df["% Passing"])

# --- Plot ---
fig, ax = plt.subplots()
ax.plot(df["Sieve Size (mm)"], df["% Passing"], marker="o", linestyle="-")
ax.set_xscale("log")
ax.invert_xaxis()
ax.set_xlabel("Sieve Size (mm)")
ax.set_ylabel("% Passing")
ax.grid(True)
ax.set_title("Grain-Size Distribution Curve")

# --- Display ---
st.dataframe(df)
st.pyplot(fig)
st.markdown(f"**D10:** {D10:.3f} mm")
st.markdown(f"**D30:** {D30:.3f} mm")
st.markdown(f"**D60:** {D60:.3f} mm")
st.markdown(f"**Cu (Uniformity Coefficient):** {Cu:.2f}")
st.markdown(f"**Cc (Coefficient of Gradation):** {Cc:.2f}")
st.markdown(f"**Skewness:** {skewness:.2f}")
st.markdown(f"**Kurtosis:** {kurt:.2f}")
st.markdown(f"**Soil Classification:** {classification}")
