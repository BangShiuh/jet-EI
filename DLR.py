# This script calculates the NOx emission index at
# cruise using the method developed by Deutsches
# Zentrum für Luft- und Raumfahrt (DLR)
# by Bang-Shiuh Chen
# Nov 3, 2021
# reference:
# [1] Schaefer, M., & Bartosch, S. (2013). Overview 
# on fuel flow correlation methods for the
# calculation of NOx, CO and HC emissions and their 
# implementation into aircraft performance software.
# Institut für Antriebstechnik, Köln.

import numpy as np
from scipy.interpolate import BarycentricInterpolator
from ambiance import Atmosphere
import pint
ureg = pint.UnitRegistry()

# ----------------------------------------------
#                    Step 1
# ----------------------------------------------
# Flight height
height = np.array([1000, 2000]) * ureg.meter
h_meter = height.to(ureg.meter)
h_feet = height.to(ureg.feet)

# Flight Mach number
M = np.array([0.5, 0.6])

# Cruise fuel flow rate
Wf_Alt = np.array([20, 15])

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

# The non-dimensional ambiant pressure
delta = Pt_Alt / P0_SL

# The non-dimensional ambiant temperature
theta = Tt_Alt / T0_SL

# The fuel flow rate at sealevel
Wf_SL = Wf_Alt / delta / np.sqrt(theta)

# ----------------------------------------------
#                    Step 2
# ----------------------------------------------
# take off: 1.01
# climb-out: 1.013
# Approach: 1.02
# Idle: 1.1
# [take off, climb-out, Approach, Idle]
r = np.array([1.01, 1.013, 1.02, 1.1])
Wf_edb = np.array([30, 40, 10, 5])
Wf_ref = Wf_edb * r
EINOx_edb = np.array([1.2, 1.4, 1.6, 1.7])

# LTO fit
EINOx = BarycentricInterpolator(Wf_ref, EINOx_edb)

# SL NOxEI
EINOx_SL = EINOx(Wf_SL)

# ----------------------------------------------
#                    Step 3
# ----------------------------------------------
# Determine humidity correction
omega = 0.001 * np.exp(-0.0001426 * 
        (h_feet.magnitude - 12900.0))
H = -19.0 * (omega - 0.00634)

# Determine cruise NOxEI
EINOx_Alt = EINOx_SL * delta**0.4 * theta**3 * np.exp(H)

print(
f'''
{'-'*40}
DLR NOx emission result:
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
