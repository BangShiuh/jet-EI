# This script calculates the mvPM emission index at
# cruise using Mission Emissions Evaluation Methodology
# (MEEM)
# by Bang-Shiuh Chen
# Dec 7, 2021

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
# from scipy.interpolate import BarycentricInterpolator
from ambiance import Atmosphere
import pint
ureg = pint.UnitRegistry()

# -----------------------------------------------------
# Step 1 Thermodynamic conditions in each flight phase
# -----------------------------------------------------
# Flight height
height = np.array([35000]) * ureg.meter
h_meter = height.to(ureg.meter)
h_feet = height.to(ureg.feet)

# Flight Mach number
M = np.array([0.78])

# sealevel properties
SL = Atmosphere(0)
T0_SL = SL.temperature[0]
P0_SL = SL.pressure[0]

# cruise properties
Alt = Atmosphere(h_meter.magnitude)
T0_Alt = Alt.temperature
P0_Alt = Alt.pressure

# Total pressure
Pt_Alt = P0_Alt * (1 + 0.2 * M*M)**3.5

# Total temperature
Tt_Alt = T0_Alt * (1 + 0.2 * M*M)

# OPR
# General Electric GE9X 60:1
# Rolls-Royce Trent XWB 52:1
# General Electric GE90 42:1
# General Electric CF6  30.5:1
# General Electric F110 30:1 
Pi_00 = 60

# Flight phase pressure coefficient
phase = "cruise"
Pi_Alt = 0.95 # for cruise
cruise_h = 35000 # cruise height [ft]
if phase == "climb":
    Pi_Alt = 0.85 + (1.15 - 0.85) / (cruise_h - 3000) * (height - 3000)

# Flight phase compressor efficiency for climb and cruise
eta_comp = 0.88

# P3 computation
P3_Alt = Pt_Alt * (1 + Pi_Alt * (Pi_00 - 1))

# T3 computation
gamma = 1.4
r = (gamma-1)/gamma
T3_Alt = (1.0 + ((P3_Alt / Pt_Alt)**r - 1) /
         eta_comp) * Tt_Alt

# ---------------------------------------------------------------------
# Step 2: Estimating P3 and thrust at ground reference (GR) condition.
# ---------------------------------------------------------------------
T3_SL = T3_Alt
P3_SL = P0_SL * (1.0 + eta_comp * (T3_SL / T0_SL - 1.0)) ** (1/r)
F00 = np.linspace(12, 27, 27-12+1)
F00 = np.linspace(0.5, 0.7, 11)
F_SL = F00 * (P3_SL / P0_Alt - 1.0) / (Pi_00 - 1.0) # F_SL/F_00

# ---------------------------------------------------------------------
# Step 3: Interpolation
# ---------------------------------------------------------------------
EBD_data = pd.read_csv("EDB.csv")
MaxF_edb = 121.4 #kN
F00_edb = EBD_data["F00"] * MaxF_edb  # %F00
EImass_edb = EBD_data["EImass"]
EInum_edb = EBD_data["EInum"]

# LTO fit
EImass_fit = interp1d(F00_edb, EImass_edb)
EInum_fit = interp1d(F00_edb, EInum_edb)

# ----------------------------------------------
# Step 4: Correction
# ----------------------------------------------
# Soot
# Enrichment Factor (EF)

EF = 1.1
EImass_SL = EImass_fit(F_SL)
EInum_SL = EInum_fit(F_SL)
EImass_Alt = EImass_SL * (P3_Alt / P3_SL)**1.35 * EF**2.5
EInum_Alt = EImass_Alt * EInum_SL / EImass_SL

# save CSV
data = pd.DataFrame({"F00": F00, "EImass": EImass_Alt, "EInum": EInum_Alt})
data.to_csv("nvPM-Alt.csv")
