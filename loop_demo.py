#!/usr/bin/env python3
"""
loop_demo.py — core simulation

Closed-loop life-support toy model:
  - CO₂ production & scrubbing
  - O₂ regeneration
  - Temperature control (radiator)
  - Humidity control (condenser)
"""

from __future__ import annotations
import numpy as np

def simulate_loop(
    duration: int = 3600,
    dt: float = 1.0,
    metabolic_rate: float = 0.0005,   # mol CO2/s
    scrub_efficiency: float = 0.3,    # fraction/s (lower = more visible CO2)
    photosynthesis_yield: float = 1.0,# mol O2 per mol CO2 scrubbed
    heat_coeff: float = 0.5,          # °C per mol CO2 delta
    rad_coeff: float = 0.01,          # radiator pull toward setpoint (per step)
    hum_coeff: float = 0.5,           # humidity per mol CO2 delta (a.u.)
    cond_coeff: float = 0.001,        # condenser removal per step
    temp_setpoint: float = 22.0,      # °C
):
    n = int(duration / dt)
    t = np.arange(n) * dt

    co2  = np.zeros(n)
    o2   = np.zeros(n)
    temp = np.full(n, temp_setpoint)
    hum  = np.zeros(n)

    for i in range(1, n):
        # CO₂ production
        co2[i] = co2[i-1] + metabolic_rate * dt
        # scrub some fraction of what's present
        scrubbed = scrub_efficiency * co2[i] * dt
        co2[i]  -= scrubbed
        # O₂ regen 1:1 with scrubbed CO₂ (toy stoichiometry)
        o2[i]    = o2[i-1] + scrubbed * photosynthesis_yield

        # Temperature loop: add heat ~ CO₂ delta, remove toward setpoint
        temp[i]  = temp[i-1] + heat_coeff * (co2[i] - co2[i-1])
        temp[i] -= rad_coeff * (temp[i-1] - temp_setpoint)

        # Humidity loop: add moisture ~ CO₂ delta, condenser removes proportionally
        hum[i]   = hum[i-1] + hum_coeff * (co2[i] - co2[i-1])
        hum[i]  -= cond_coeff * hum[i-1]

    return t, co2, o2, temp, hum

