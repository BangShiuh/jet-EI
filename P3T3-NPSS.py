# This script calculates the NOx emission index at
# cruise using P3T3 method
# by Bang-Shiuh Chen

import numpy as np
from scipy.interpolate import interp1d
from scipy.interpolate import BarycentricInterpolator
from scipy.interpolate import KroghInterpolator
from ambiance import Atmosphere
import pint
ureg = pint.UnitRegistry()
import pandas as pd

# ----------------------------------------------
#          Step 1 get EDB and NPSS data
# ----------------------------------------------
# Cruise total T3 P3
cruise_data = pd.read_csv("L1A_climb_outSweepOutPutTot.csv")
T3_Alt = cruise_data[" T3(K)"]
P3_Alt = cruise_data[" P3(Pa)"]

# Flight height
height = np.array(cruise_data["height"]) * ureg.feet
h_meter = height.to(ureg.meter)
h_feet = height.to(ureg.feet)

# Flight Mach number
M = cruise_data["Mach"]

# sealevel properties
SL = Atmosphere(0)
T0_SL = SL.temperature[0]
P0_SL = SL.pressure[0]

# cruise properties
Alt = Atmosphere(h_meter.magnitude)
T0_Alt = Alt.temperature
P0_Alt = Alt.pressure

# The non-dimensional ambiant pressure
delta0 = P0_Alt / P0_SL

# ----------------------------------------------
#             Step 2 Reference function
# ----------------------------------------------
# Sea level data
SL_data = pd.read_csv("NPSS-L1A-SL.csv")
EINOx_SL = SL_data["EINOx"]
T3_SL = SL_data["T3[K]"]
P3_SL = SL_data["P3[pa]"]

EINOx_fit = interp1d(T3_SL, EINOx_SL)
EINOx_SL = EINOx_fit(T3_Alt)
P3_SL_fit = interp1d(T3_SL, P3_SL)
P3_SL = P3_SL_fit(T3_Alt)
# ----------------------------------------------
#                    Step 3
# ----------------------------------------------
# Determine humidity correction
relative_humidity = 0.6
tau = 373.16 / T0_Alt
beta = (7.90298 * (1.0 - tau) + 3.00571 + 
        5.02808 * np.log10(tau) +
        1.3816E-7 * (1.0 - (10.0 ** ( 11.344 * (1. - 1./tau)))) +
        8.1328E-3 * (10. ** (3.49149 * ( 1. - tau)) - 1.0))

Pv = 0.014504 * 10**beta
P0_Alt_psi = delta0 * 14.696
omega = (0.62197058 * relative_humidity * Pv / 
        (P0_Alt_psi - relative_humidity * Pv))
omega = 0.0
H = -19.0 * (omega - 0.00634)

# Re-correct to cruise conditions
EINOx_Alt = EINOx_SL * (P3_Alt / P3_SL)**0.4 * np.exp(H)

# print((P3_Alt / P3_SL)**0.4 * np.exp(H))

# print(
# f'''
# {'-'*40}
# P3T3 result:
# height = {height}
# Temperature = {T0_Alt}
# Pressure = {P0_Alt}
# Mach number = {M}
# Sealevel NOx Emission Index:
# EINOx_SL = {EINOx_SL}
# Cruise NOx Emission Index:
# EINOx_Alt = {EINOx_Alt}
# {'-'*40}
# ''')

# save CSV
data = pd.DataFrame({"T3": T3_Alt, "EINOx_Alt": EINOx_Alt, "EINOx_SL": EINOx_SL})
data.to_csv("P3T3-L1A-climb.csv")