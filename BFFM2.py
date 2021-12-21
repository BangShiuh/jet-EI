# This script calculates the NOx emission index at
# cruise using Boening Flow Fuel Method 2 (BFFM2)
# by Bang-Shiuh Chen
# Nov 3, 2021
# reference:
# [1] Schaefer, M., & Bartosch, S. (2013). Overview 
# on fuel flow correlation methods for the
# calculation of NOx, CO and HC emissions and their 
# implementation into aircraft performance software.
# Institut für Antriebstechnik, Köln.

import numpy as np
from scipy.interpolate import interp1d
from scipy.interpolate import BarycentricInterpolator
from scipy.interpolate import KroghInterpolator
from ambiance import Atmosphere
import pint
ureg = pint.UnitRegistry()
import pandas as pd

# ----------------------------------------------
#                    Step 1
# ----------------------------------------------
# Flight height
height = 35000 * ureg.feet
h_meter = height.to(ureg.meter)
h_feet = height.to(ureg.feet)

# Flight Mach number
M = 0.78

# Cruise fuel flow rate
Wf_Alt = np.array([0.477, 0.38, 0.36, 0.339, 0.314, 0.198])

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

# The non-dimensional ambiant temperature
theta0 = T0_Alt / T0_SL

# Total pressure
Pt_Alt = P0_Alt * (1 + 0.2 * M*M)**3.5

# Total temperature
Tt_Alt = T0_Alt * (1 + 0.2 * M*M)

# The non-dimensional ambiant pressure
delta = Pt_Alt / P0_SL

# The non-dimensional ambiant temperature
theta = Tt_Alt / T0_SL

# The fuel flow rate at sealevel
Wf_SL = Wf_Alt / delta0 * theta0**3.8 * np.exp(0.2*M*M)

# ----------------------------------------------
#             Step 2 Reference function
# ----------------------------------------------
# EDB data
# take off: 1.01
# climb-out: 1.013
# Approach: 1.02
# Idle: 1.1
# [take off, climb-out, Approach, Idle]
r = np.array([1.01, 1.013, 1.02, 1.1])
EBD_data = pd.read_csv("EDB.csv")
Wf_edb = EBD_data["Wf"]
# Validation data
# Wf_edb = np.array([3.91, 3.1, 1.0, 0.3])

Wf_ref = Wf_edb * r
EINOx_edb = EBD_data["EINOx"]

# Validation data
# EINOx_edb = np.array([45.7, 33.3, 11.58, 5.33])


# LTO fit
EINOx_log10 = interp1d(np.log10(Wf_ref),
                        np.log10(EINOx_edb))
# EICO_log10 = interp1d(np.log10(Wf_ref),
#                        np.log10(EICO_edb))

# SL NOxEI
EINOx_SL = 10.0**(EINOx_log10(np.log10(Wf_SL)))

# SL EICO
# EICO_SL = 10.0**(EICO_log10(np.log10(Wf_SL)))

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
H = -19.0 * (omega - 0.00634)

# Determine cruise EINOx
EINOx_Alt = EINOx_SL * (delta0**1.02 / 
            theta0**3.3) ** 0.5 * np.exp(H)
# Determine cruise EICO
# EICO_Alt = EICO_SL * theta0**3.3 / delta0**1.02

print(
f'''
{'-'*40}
BFFM2 result:
height = {height}
Temperature = {T0_Alt}
Pressure = {P0_Alt}
Mach number = {M}
Cruise fuel flow rate:
Wf_Alt = {Wf_Alt}
Sealevel fuel flow rate:
Wf_SL = {Wf_SL}
Sealevel NOx Emission Index:
EINOx_SL = {EINOx_SL}
Cruise NOx Emission Index:
EINOx_Alt = {EINOx_Alt}
{'-'*40}
''')

# save CSV
data = pd.DataFrame({"Wf": Wf_Alt, "EINOx": EINOx_Alt})
data.to_csv("BFFM2-Alt.csv")
