import pandas as pd

# load data
df_nvPM = pd.read_excel('edb-emissions-databank_v28c_web.xlsx', sheet_name='nvPM Emissions')
df_gas = pd.read_excel('edb-emissions-databank_v28c_web.xlsx', sheet_name='Gaseous Emissions and Smoke')

# LEAP1A
# Indices for gas sheet
indices = [176, 177, 179, 181]

EIHC_TO = df_gas["HC EI T/O (g/kg)"][indices]
EIHC_CO = df_gas["HC EI C/O (g/kg)"][indices]
EIHC_App = df_gas["HC EI App (g/kg)"][indices]
EIHC_Idle = df_gas["HC EI Idle (g/kg)"][indices]

EINOx_TO = df_gas["NOx EI T/O (g/kg)"][indices]
EINOx_CO = df_gas["NOx EI C/O (g/kg)"][indices]
EINOx_App = df_gas["NOx EI App (g/kg)"][indices]
EINOx_Idle = df_gas["NOx EI Idle (g/kg)"][indices]

EICO_TO = df_gas["CO EI T/O (g/kg)"][indices]
EICO_CO = df_gas["CO EI C/O (g/kg)"][indices]
EICO_App = df_gas["CO EI App (g/kg)"][indices]
EICO_Idle = df_gas["CO EI Idle (g/kg)"][indices]

Thrust_TO = df_gas["Rated Thrust (kN)"][indices]
Thrust_CO = df_gas["Rated Thrust (kN)"][indices] * 0.85
Thrust_App = df_gas["Rated Thrust (kN)"][indices] * 0.3
Thrust_Idle = df_gas["Rated Thrust (kN)"][indices] * 0.07

# Indices for nvPM sheet
# The indices should match to the same Enigne ID
indices = [182, 183, 185, 187]

EImass_TO = df_nvPM["nvPM EImass_SL T/O (mg/kg)"][indices]
EImass_CO = df_nvPM["nvPM EImass_SL C/O (mg/kg)"][indices]
EImass_App = df_nvPM["nvPM EImass_SL App (mg/kg)"][indices]
EImass_Idle = df_nvPM["nvPM EImass_SL Idle (mg/kg)"][indices]

EInum_TO = df_nvPM["nvPM EInum T/O (#/kg)"][indices]
EInum_CO = df_nvPM["nvPM EInum C/O (#/kg)"][indices]
EInum_App = df_nvPM["nvPM Einum App (#/kg)"][indices]
EInum_Idle = df_nvPM["nvPM EInum Idle (#/kg)"][indices]

Wf_TO = df_nvPM["Fuel Flow T/O (kg/sec)"][indices]
Wf_CO = df_nvPM["Fuel Flow C/O (kg/sec)"][indices]
Wf_App = df_nvPM["Fuel Flow App (kg/sec)"][indices]
Wf_Idle = df_nvPM["Fuel Flow Idle (kg/sec)"][indices]

# Combine TO, CO, App, and Idle
frames = [Wf_TO, Wf_CO, Wf_App, Wf_Idle]
Wf = pd.concat(frames, ignore_index=True)

frames = [Thrust_TO, Thrust_CO, Thrust_App, Thrust_Idle]
Thrust = pd.concat(frames, ignore_index=True)

frames = [EINOx_TO, EINOx_CO, EINOx_App, EINOx_Idle]
EINOx = pd.concat(frames, ignore_index=True)

frames = [EIHC_TO, EIHC_CO, EIHC_App, EIHC_Idle]
EIHC = pd.concat(frames, ignore_index=True)

frames = [EICO_TO, EICO_CO, EICO_App, EICO_Idle]
EICO = pd.concat(frames, ignore_index=True)

frames = [EIHC_TO, EIHC_CO, EIHC_App, EIHC_Idle]
EImass = pd.concat(frames, ignore_index=True)

frames = [EInum_TO, EInum_CO, EInum_App, EInum_Idle]
EInum = pd.concat(frames, ignore_index=True)

# Merge
frames = [Thrust, Wf, EINOx, EIHC, EICO, EImass, EInum]
data = pd.concat(frames, axis=1)
data.columns = ["Thrust", "Wf", "EINOx", "EIHC", "EICO", "EImass", "EInum"]

# Sort
data.sort_values(by=['Wf'],kind="mergesort", ignore_index=True, inplace=True)
print(data)

# save to csv
data.to_csv("LEAP1A-ICAO.csv", index=False)