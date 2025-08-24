#!/usr/bin/env python3
# streamlit_app.py - interactive UI for the NovaCore loop

import io
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

from loop_demo import simulate_loop

st.set_page_config(page_title="NovaCore Life-Support Simulator", layout="centered")
st.title("🛰️ NovaCore: Closed-Loop Life-Support Simulator")

with st.sidebar:
    st.header("Parameters")
    duration_min = st.slider("Duration (minutes)", 10, 240, 60, step=5)
    dt = 1.0

    st.subheader("Gas Loop")
    # Show the true small number (was rounding to 0.00 before)
    metabolic_rate = st.slider(
        "Metabolic CO₂ rate (mol/s)",
        min_value=0.0000, max_value=0.0020, value=0.0005, step=0.0001,
        format="%.5f",
    )
    st.caption(f"Metabolic CO₂: **{metabolic_rate:.6f} mol/s** ({metabolic_rate*60:.4f} mol/min)")

    scrub_eff = st.slider("Scrubber efficiency (fraction/s)", 0.05, 0.90, 0.30, step=0.05)
    o2_yield  = st.slider("O₂ yield per CO₂ scrubbed", 0.5, 1.5, 1.0, step=0.1)

    st.subheader("Environment")
    temp_setpoint = st.slider("Temp setpoint (°C)", 18.0, 26.0, 22.0, step=0.5)
    heat_coeff    = st.slider("Heat gain coeff", 0.0, 1.0, 0.5, step=0.05)
    rad_coeff     = st.slider("Radiator coeff", 0.0, 0.2, 0.01, step=0.01)
    hum_coeff     = st.slider("Humidity gain coeff", 0.0, 1.0, 0.5, step=0.05)
    cond_coeff    = st.slider("Condenser coeff", 0.0, 0.05, 0.001, step=0.001)

    st.subheader("Display")
    log_scale = st.checkbox("Log scale for gas axis (helps show tiny CO₂)", value=True)
    show_csv  = st.checkbox("Show/export telemetry CSV", value=False)

# Run simulation
t, co2, o2, temp, hum = simulate_loop(
    duration=int(duration_min * 60),
    dt=dt,
    metabolic_rate=metabolic_rate,
    scrub_efficiency=scrub_eff,
    photosynthesis_yield=o2_yield,
    heat_coeff=heat_coeff,
    rad_coeff=rad_coeff,
    hum_coeff=hum_coeff,
    cond_coeff=cond_coeff,
    temp_setpoint=temp_setpoint,
)

# Plot
fig, ax1 = plt.subplots(figsize=(9, 4.8))

# Gas axis (CO2 & O2)
if log_scale:
    ax1.set_yscale("symlog", linthresh=1e-4)
    ax1.set_ylabel("Gas (log mol)")
else:
    ax1.set_ylabel("Gas (mol)")

ax1.plot(t/60, co2, label="CO₂ (mol)")
ax1.plot(t/60, o2,  label="O₂ (mol)")
ax1.set_xlabel("Time (minutes)")
ax1.grid(True, which="both")

# Env axis (Temp/Humidity)
ax2 = ax1.twinx()
ax2.plot(t/60, temp, "--", label="Temp (°C)")
ax2.plot(t/60, hum,  "--", label="Humidity (a.u.)")
ax2.set_ylabel("Temp / Humidity")

# Combined legend
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left")

st.pyplot(fig, clear_figure=True)

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Final CO₂ (mol)", f"{co2[-1]:.6f}")
col2.metric("Final O₂ (mol)",  f"{o2[-1]:.3f}")
col3.metric("Final Temp (°C)", f"{temp[-1]:.2f}")
col4.metric("Final Humidity",  f"{hum[-1]:.3f}")

# Telemetry export
if show_csv:
    df = pd.DataFrame({
        "time_s": t,
        "time_min": t/60,
        "co2_mol": co2,
        "o2_mol": o2,
        "temp_c": temp,
        "humidity_au": hum,
    })
    st.dataframe(df.head(200), use_container_width=True)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button("⬇️ Export telemetry CSV", data=buf.getvalue(),
                       file_name="telemetry.csv", mime="text/csv")
