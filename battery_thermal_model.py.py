import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


# ============================================================
# 1. LITERATURE PARAMETERS
# ============================================================

capacity_Ah = 2.9
mass = 0.0475
diameter = 18.5e-3
length = 65.3e-3

Cp = 859
h = 22.46

T_ambient = 27.0
T_initial = 27.0

V_max = 4.20
SOC_initial = 0.10

# C-rates to study
C_rates = [0.5, 1.5, 2.5]


# ============================================================
# 2. CELL GEOMETRY
# ============================================================

radius = diameter / 2

area = (
    2 * np.pi * radius * length
    + 2 * np.pi * radius**2
)

print("Cell surface area =", area, "m^2")


# ============================================================
# 3. SOC-DEPENDENT INTERNAL RESISTANCE
# ============================================================

soc_data = np.array([
    0.1, 0.2, 0.3, 0.4, 0.5,
    0.6, 0.7, 0.8, 0.9
])

Ri_data = np.array([
    0.007715236,
    0.004936539,
    0.004642974,
    0.000533031,
    0.004500052,
    0.003762231,
    0.004269876,
    0.005758057,
    0.007765269
])


# ============================================================
# 4. POLARIZATION PARAMETERS
# ============================================================

RD_data = np.array([
    0.037086746,
    0.036015296,
    0.029939776,
    0.032518208,
    0.028981830,
    0.032604564,
    0.036168348,
    0.032518208,
    0.030551706
])

CD_data = np.array([
    175.1891996,
    190.8128138,
    173.9061123,
    78.58233779,
    218.8730953,
    172.3249851,
    225.2169223,
    283.1958433,
    205.2736912
])


# ============================================================
# 5. OCV-SOC MODEL
# ============================================================

def calculate_ocv(soc):

    soc = np.clip(soc, 0.1, 1.0)

    return (
        3.4290 * soc**6
        - 4.4888 * soc**5
        - 6.3228 * soc**4
        + 14.9681 * soc**3
        - 9.7608 * soc**2
        + 3.2527 * soc
        + 3.0984
    )


# ============================================================
# 6. BATTERY PARAMETERS
# ============================================================

def get_parameters(soc):

    soc_lookup = np.clip(
        soc,
        0.1,
        0.9
    )

    Ri = np.interp(
        soc_lookup,
        soc_data,
        Ri_data
    )

    RD = np.interp(
        soc_lookup,
        soc_data,
        RD_data
    )

    CD = np.interp(
        soc_lookup,
        soc_data,
        CD_data
    )

    return Ri, RD, CD


# ============================================================
# 7. STORE RESULTS
# ============================================================

results = {}


# ============================================================
# 8. RUN EACH C-RATE
# ============================================================

for C_rate in C_rates:

    print()
    print("========================================")
    print(f"Running {C_rate}C")
    print("========================================")

    I_CC = C_rate * capacity_Ah

    I_cutoff = 0.1 * capacity_Ah

    # --------------------------------------------------------
    # CC MODEL
    # --------------------------------------------------------

    def cc_model(t, y):

        T = y[0]
        UD = y[1]
        SOC = y[2]

        I = I_CC

        Ri, RD, CD = get_parameters(SOC)

        dUD_dt = (
            -UD / (RD * CD)
            + I / CD
        )

        dSOC_dt = (
            I /
            (capacity_Ah * 3600)
        )

        Q_ohmic = I**2 * Ri

        Q_polarization = (
            UD**2 / RD
        )

        Q_total = (
            Q_ohmic
            + Q_polarization
        )

        Q_loss = (
            h
            * area
            * (T - T_ambient)
        )

        dT_dt = (
            Q_total - Q_loss
        ) / (mass * Cp)

        return [
            dT_dt,
            dUD_dt,
            dSOC_dt
        ]


    # --------------------------------------------------------
    # VOLTAGE EVENT
    # --------------------------------------------------------

    def voltage_event(t, y):

        T = y[0]
        UD = y[1]
        SOC = y[2]

        Ri, RD, CD = get_parameters(SOC)

        OCV = calculate_ocv(SOC)

        voltage = (
            OCV
            + UD
            + I_CC * Ri
        )

        return voltage - V_max


    voltage_event.terminal = True
    voltage_event.direction = 1


    # --------------------------------------------------------
    # RUN CC
    # --------------------------------------------------------

    cc_solution = solve_ivp(
        cc_model,
        [0, 7200],
        [
            T_initial,
            0.0,
            SOC_initial
        ],
        events=voltage_event,
        max_step=1.0
    )


    if len(cc_solution.t_events[0]) == 0:

        print("WARNING: 4.2 V not reached during CC.")

        continue


    # --------------------------------------------------------
    # CC-CV TRANSITION
    # --------------------------------------------------------

    t_CC_end = cc_solution.t[-1]

    T_CC_end = cc_solution.y[0, -1]

    UD_CC_end = cc_solution.y[1, -1]

    SOC_CC_end = cc_solution.y[2, -1]


    # --------------------------------------------------------
    # CV MODEL
    # --------------------------------------------------------

    def cv_model(t, y):

        T = y[0]
        UD = y[1]
        SOC = min(y[2], 1.0)

        Ri, RD, CD = get_parameters(SOC)

        OCV = calculate_ocv(SOC)

        I = (
            V_max
            - OCV
            - UD
        ) / Ri

        I = max(I, 0.0)

        dUD_dt = (
            -UD / (RD * CD)
            + I / CD
        )

        if SOC >= 1.0:

            dSOC_dt = 0.0

        else:

            dSOC_dt = (
                I /
                (capacity_Ah * 3600)
            )

        Q_ohmic = I**2 * Ri

        Q_polarization = (
            UD**2 / RD
        )

        Q_total = (
            Q_ohmic
            + Q_polarization
        )

        Q_loss = (
            h
            * area
            * (T - T_ambient)
        )

        dT_dt = (
            Q_total - Q_loss
        ) / (mass * Cp)

        return [
            dT_dt,
            dUD_dt,
            dSOC_dt
        ]


    # --------------------------------------------------------
    # FULL SOC EVENT
    # --------------------------------------------------------

    def soc_full_event(t, y):

        return y[2] - 1.0


    soc_full_event.terminal = True
    soc_full_event.direction = 1


    # --------------------------------------------------------
    # CURRENT EVENT
    # --------------------------------------------------------

    def current_event(t, y):

        T = y[0]
        UD = y[1]
        SOC = min(y[2], 1.0)

        Ri, RD, CD = get_parameters(SOC)

        OCV = calculate_ocv(SOC)

        I = (
            V_max
            - OCV
            - UD
        ) / Ri

        I = max(I, 0.0)

        return I - I_cutoff


    current_event.terminal = True
    current_event.direction = -1


    # --------------------------------------------------------
    # RUN CV
    # --------------------------------------------------------

    cv_solution = solve_ivp(
        cv_model,
        [
            t_CC_end,
            t_CC_end + 7200
        ],
        [
            T_CC_end,
            UD_CC_end,
            SOC_CC_end
        ],
        events=[
            soc_full_event,
            current_event
        ],
        max_step=1.0
    )


    # --------------------------------------------------------
    # COMBINE RESULTS
    # --------------------------------------------------------

    time = np.concatenate([
        cc_solution.t,
        cv_solution.t[1:]
    ])

    temperature = np.concatenate([
        cc_solution.y[0],
        cv_solution.y[0, 1:]
    ])

    UD = np.concatenate([
        cc_solution.y[1],
        cv_solution.y[1, 1:]
    ])

    SOC = np.concatenate([
        cc_solution.y[2],
        cv_solution.y[2, 1:]
    ])

    SOC = np.clip(
        SOC,
        0.0,
        1.0
    )


    # --------------------------------------------------------
    # CURRENT / VOLTAGE / HEAT
    # --------------------------------------------------------

    current_array = []
    voltage_array = []
    ohmic_heat = []
    polarization_heat = []
    total_heat = []


    for i in range(len(time)):

        soc_now = SOC[i]

        ud_now = UD[i]

        Ri, RD, CD = get_parameters(
            soc_now
        )

        OCV = calculate_ocv(
            soc_now
        )

        if time[i] <= t_CC_end:

            I = I_CC

        else:

            I = (
                V_max
                - OCV
                - ud_now
            ) / Ri

            I = max(I, 0.0)


        voltage = (
            OCV
            + ud_now
            + I * Ri
        )

        Q_ohmic = (
            I**2 * Ri
        )

        Q_polarization = (
            ud_now**2 / RD
        )

        Q_total = (
            Q_ohmic
            + Q_polarization
        )

        current_array.append(I)
        voltage_array.append(voltage)

        ohmic_heat.append(
            Q_ohmic
        )

        polarization_heat.append(
            Q_polarization
        )

        total_heat.append(
            Q_total
        )


    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    results[C_rate] = {

        "time": time,

        "temperature": temperature,

        "SOC": SOC,

        "current": np.array(
            current_array
        ),

        "voltage": np.array(
            voltage_array
        ),

        "UD": UD,

        "ohmic_heat": np.array(
            ohmic_heat
        ),

        "polarization_heat": np.array(
            polarization_heat
        ),

        "total_heat": np.array(
            total_heat
        ),

        "cc_time": t_CC_end,

        "cc_soc": SOC_CC_end
    }


    # --------------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------------

    print(
        "CC-CV transition =",
        t_CC_end / 60,
        "min"
    )

    print(
        "SOC at transition =",
        SOC_CC_end * 100,
        "%"
    )

    print(
        "Maximum temperature =",
        np.max(temperature),
        "°C"
    )

    print(
        "Total charging time =",
        time[-1] / 60,
        "min"
    )

    print(
        "Final SOC =",
        SOC[-1] * 100,
        "%"
    )

    print(
        "Final current =",
        current_array[-1],
        "A"
    )


# ============================================================
# 9. SUMMARY TABLE
# ============================================================

print()
print("======================================================")
print("                FINAL SUMMARY")
print("======================================================")

print(
    "C-rate | CC-CV SOC | Tmax (°C) | "
    "Charge Time (min) | Final Current (A)"
)

print("------------------------------------------------------")

for C_rate in C_rates:

    r = results[C_rate]

    print(
        f"{C_rate:5.1f}C | "
        f"{r['cc_soc']*100:8.2f}% | "
        f"{np.max(r['temperature']):9.2f} | "
        f"{r['time'][-1]/60:16.2f} | "
        f"{r['current'][-1]:16.3f}"
    )


# ============================================================
# 10. TEMPERATURE COMPARISON
# ============================================================

plt.figure(figsize=(9, 6))

for C_rate in C_rates:

    r = results[C_rate]

    plt.plot(
        r["time"] / 60,
        r["temperature"],
        label=f"{C_rate}C"
    )

plt.xlabel("Time (min)")
plt.ylabel("Temperature (°C)")

plt.title(
    "NCR18650PF Temperature During CC-CV Charging"
)

plt.legend()
plt.grid(True)

plt.show()


# ============================================================
# 11. CURRENT COMPARISON
# ============================================================

plt.figure(figsize=(9, 6))

for C_rate in C_rates:

    r = results[C_rate]

    plt.plot(
        r["time"] / 60,
        r["current"],
        label=f"{C_rate}C"
    )

plt.xlabel("Time (min)")
plt.ylabel("Charging Current (A)")

plt.title(
    "Charging Current During CC-CV Operation"
)

plt.legend()
plt.grid(True)

plt.show()


# ============================================================
# 12. VOLTAGE COMPARISON
# ============================================================

plt.figure(figsize=(9, 6))

for C_rate in C_rates:

    r = results[C_rate]

    plt.plot(
        r["time"] / 60,
        r["voltage"],
        label=f"{C_rate}C"
    )

plt.axhline(
    V_max,
    linestyle="--",
    label="4.2 V limit"
)

plt.xlabel("Time (min)")
plt.ylabel("Terminal Voltage (V)")

plt.title(
    "Terminal Voltage During CC-CV Charging"
)

plt.legend()
plt.grid(True)

plt.show()


# ============================================================
# 13. MAXIMUM TEMPERATURE vs C-RATE
# ============================================================

max_temperatures = []

for C_rate in C_rates:

    max_temperatures.append(
        np.max(
            results[C_rate]["temperature"]
        )
    )


plt.figure(figsize=(8, 5))

plt.plot(
    C_rates,
    max_temperatures,
    marker="o"
)

plt.xlabel("C-rate")

plt.ylabel(
    "Maximum Temperature (°C)"
)

plt.title(
    "Maximum Cell Temperature vs Charging Rate"
)

plt.grid(True)

plt.show()


# ============================================================
# 14. HEAT GENERATION AT EACH C-RATE
# ============================================================

plt.figure(figsize=(9, 6))

for C_rate in C_rates:

    r = results[C_rate]

    plt.plot(
        r["time"] / 60,
        r["total_heat"],
        label=f"{C_rate}C"
    )

plt.xlabel("Time (min)")

plt.ylabel(
    "Total Heat Generation (W)"
)

plt.title(
    "Heat Generation During CC-CV Charging"
)

plt.legend()
plt.grid(True)

plt.show()

# ============================================================
# 15. VALIDATION AND ENGINEERING ANALYSIS
# ============================================================

print()
print("======================================================")
print("           MODEL VALIDATION ANALYSIS")
print("======================================================")

# Literature reference temperatures
# 0.5C: exact numerical maximum not reported
# 1.5C: 27 + 12.2 = 39.2 °C
# 2.5C: approximately 45.3 °C

literature_temperature = {
    0.5: np.nan,
    1.5: 39.2,
    2.5: 45.3
}


# ============================================================
# CALCULATE VALIDATION METRICS
# ============================================================

validation_results = []

for C_rate in C_rates:

    model_temperature = np.max(
        results[C_rate]["temperature"]
    )

    ambient = T_ambient

    temperature_rise = (
        model_temperature
        - ambient
    )

    literature_temperature_value = (
        literature_temperature[C_rate]
    )

    if np.isnan(
        literature_temperature_value
    ):

        absolute_error = np.nan
        percentage_error = np.nan

    else:

        absolute_error = abs(
            model_temperature
            - literature_temperature_value
        )

        percentage_error = (
            absolute_error
            / literature_temperature_value
            * 100
        )

    charging_time = (
        results[C_rate]["time"][-1]
        / 60
    )

    validation_results.append([
        C_rate,
        model_temperature,
        temperature_rise,
        literature_temperature_value,
        absolute_error,
        percentage_error,
        charging_time
    ])


# ============================================================
# PRINT VALIDATION TABLE
# ============================================================

print()
print(
    "C-rate | Model Tmax | ΔT | Literature | "
    "Abs Error | Error % | Charge Time"
)

print(
    "       | (°C)       | °C | Tmax (°C) | "
    "(°C)      |         | (min)"
)

print("-" * 85)


for row in validation_results:

    C_rate = row[0]
    model_T = row[1]
    delta_T = row[2]
    literature_T = row[3]
    error = row[4]
    error_percent = row[5]
    charge_time = row[6]

    if np.isnan(literature_T):

        literature_text = "N/A"
        error_text = "N/A"
        error_percent_text = "N/A"

    else:

        literature_text = f"{literature_T:.2f}"
        error_text = f"{error:.2f}"
        error_percent_text = (
            f"{error_percent:.2f}%"
        )

    print(
        f"{C_rate:5.1f}C | "
        f"{model_T:9.2f} | "
        f"{delta_T:5.2f} | "
        f"{literature_text:10} | "
        f"{error_text:9} | "
        f"{error_percent_text:8} | "
        f"{charge_time:10.2f}"
    )


# ============================================================
# 16. CHARGING TIME REDUCTION
# ============================================================

time_05C = (
    results[0.5]["time"][-1] / 60
)

time_15C = (
    results[1.5]["time"][-1] / 60
)

time_25C = (
    results[2.5]["time"][-1] / 60
)


reduction_15C = (
    (time_05C - time_15C)
    / time_05C
    * 100
)

reduction_25C = (
    (time_05C - time_25C)
    / time_05C
    * 100
)


print()
print("======================================================")
print("             CHARGING TIME ANALYSIS")
print("======================================================")

print(
    f"0.5C charging time = "
    f"{time_05C:.2f} min"
)

print(
    f"1.5C charging time = "
    f"{time_15C:.2f} min"
)

print(
    f"2.5C charging time = "
    f"{time_25C:.2f} min"
)

print()
print(
    f"Time reduction at 1.5C = "
    f"{reduction_15C:.2f}%"
)

print(
    f"Time reduction at 2.5C = "
    f"{reduction_25C:.2f}%"
)


# ============================================================
# 17. TEMPERATURE PENALTY
# ============================================================

T_05C = np.max(
    results[0.5]["temperature"]
)

T_15C = np.max(
    results[1.5]["temperature"]
)

T_25C = np.max(
    results[2.5]["temperature"]
)


thermal_increase_15C = (
    T_15C - T_05C
)

thermal_increase_25C = (
    T_25C - T_05C
)


print()
print("======================================================")
print("             THERMAL PENALTY ANALYSIS")
print("======================================================")

print(
    f"Temperature increase from "
    f"0.5C → 1.5C = "
    f"{thermal_increase_15C:.2f} °C"
)

print(
    f"Temperature increase from "
    f"0.5C → 2.5C = "
    f"{thermal_increase_25C:.2f} °C"
)


# ============================================================
# 18. TEMPERATURE vs C-RATE
# ============================================================

max_temperature_values = [
    T_05C,
    T_15C,
    T_25C
]

plt.figure(figsize=(8, 5))

plt.plot(
    C_rates,
    max_temperature_values,
    marker="o"
)

plt.axhline(
    45,
    linestyle="--",
    label="45°C reference"
)

plt.xlabel(
    "Charging Rate (C-rate)"
)

plt.ylabel(
    "Maximum Temperature (°C)"
)

plt.title(
    "Maximum Temperature vs Charging Rate"
)

plt.legend()

plt.grid(True)

plt.show()


# ============================================================
# 19. CHARGING TIME vs C-RATE
# ============================================================

charging_times = [
    time_05C,
    time_15C,
    time_25C
]

plt.figure(figsize=(8, 5))

plt.plot(
    C_rates,
    charging_times,
    marker="o"
)

plt.xlabel(
    "Charging Rate (C-rate)"
)

plt.ylabel(
    "Charging Time (min)"
)

plt.title(
    "Charging Time vs Charging Rate"
)

plt.grid(True)

plt.show()


# ============================================================
# 20. TEMPERATURE vs CHARGING TIME
# ============================================================

plt.figure(figsize=(8, 5))

plt.plot(
    charging_times,
    max_temperature_values,
    marker="o"
)

plt.xlabel(
    "Charging Time (min)"
)

plt.ylabel(
    "Maximum Temperature (°C)"
)

plt.title(
    "Thermal Penalty vs Charging Time"
)

plt.grid(True)

plt.show()

# ============================================================
# 21. COOLING OPTIMIZATION
# ============================================================

h_values = [
    5,
    10,
    15,
    20,
    22.46,
    30,
    40,
    50,
    75,
    100
]

cooling_results = []

print()
print("======================================================")
print("              COOLING OPTIMIZATION")
print("======================================================")

print("h (W/m²K) | Maximum Temperature (°C)")
print("------------------------------------")

for h_test in h_values:

    # Use the same 2.5C charging case
    C_rate = 2.5

    I_CC = C_rate * capacity_Ah

    # --------------------------------------------------------
    # CC MODEL
    # --------------------------------------------------------

    def cc_cooling_model(t, y):

        T = y[0]
        UD = y[1]
        SOC = y[2]

        I = I_CC

        Ri, RD, CD = get_parameters(SOC)

        dUD_dt = (
            -UD / (RD * CD)
            + I / CD
        )

        dSOC_dt = (
            I /
            (capacity_Ah * 3600)
        )

        Q_ohmic = I**2 * Ri

        Q_polarization = (
            UD**2 / RD
        )

        Q_total = (
            Q_ohmic
            + Q_polarization
        )

        Q_loss = (
            h_test
            * area
            * (T - T_ambient)
        )

        dT_dt = (
            Q_total - Q_loss
        ) / (mass * Cp)

        return [
            dT_dt,
            dUD_dt,
            dSOC_dt
        ]


    # --------------------------------------------------------
    # CC → CV EVENT
    # --------------------------------------------------------

    def voltage_cooling_event(t, y):

        T = y[0]
        UD = y[1]
        SOC = y[2]

        Ri, RD, CD = get_parameters(SOC)

        OCV = calculate_ocv(SOC)

        voltage = (
            OCV
            + UD
            + I_CC * Ri
        )

        return voltage - V_max


    voltage_cooling_event.terminal = True
    voltage_cooling_event.direction = 1


    # --------------------------------------------------------
    # RUN CC
    # --------------------------------------------------------

    cc = solve_ivp(
        cc_cooling_model,
        [0, 7200],
        [
            T_initial,
            0.0,
            SOC_initial
        ],
        events=voltage_cooling_event,
        max_step=1.0
    )


    if len(cc.t_events[0]) == 0:
        continue


    t_transition = cc.t[-1]

    T_transition = cc.y[0, -1]

    UD_transition = cc.y[1, -1]

    SOC_transition = cc.y[2, -1]


    # --------------------------------------------------------
    # CV MODEL
    # --------------------------------------------------------

    def cv_cooling_model(t, y):

        T = y[0]
        UD = y[1]
        SOC = min(y[2], 1.0)

        Ri, RD, CD = get_parameters(SOC)

        OCV = calculate_ocv(SOC)

        I = (
            V_max
            - OCV
            - UD
        ) / Ri

        I = max(I, 0.0)

        dUD_dt = (
            -UD / (RD * CD)
            + I / CD
        )

        if SOC >= 1.0:
            dSOC_dt = 0.0
        else:
            dSOC_dt = (
                I /
                (capacity_Ah * 3600)
            )

        Q_ohmic = I**2 * Ri

        Q_polarization = (
            UD**2 / RD
        )

        Q_total = (
            Q_ohmic
            + Q_polarization
        )

        Q_loss = (
            h_test
            * area
            * (T - T_ambient)
        )

        dT_dt = (
            Q_total - Q_loss
        ) / (mass * Cp)

        return [
            dT_dt,
            dUD_dt,
            dSOC_dt
        ]


    # --------------------------------------------------------
    # SOC = 100% EVENT
    # --------------------------------------------------------

    def cooling_soc_event(t, y):

        return y[2] - 1.0


    cooling_soc_event.terminal = True
    cooling_soc_event.direction = 1


    # --------------------------------------------------------
    # RUN CV
    # --------------------------------------------------------

    cv = solve_ivp(
        cv_cooling_model,
        [
            t_transition,
            t_transition + 7200
        ],
        [
            T_transition,
            UD_transition,
            SOC_transition
        ],
        events=cooling_soc_event,
        max_step=1.0
    )


    # --------------------------------------------------------
    # COMBINE TEMPERATURE
    # --------------------------------------------------------

    temperature_combined = np.concatenate([
        cc.y[0],
        cv.y[0, 1:]
    ])


    Tmax = np.max(
        temperature_combined
    )

    cooling_results.append([
        h_test,
        Tmax
    ])

    print(
        f"{h_test:10.2f} | "
        f"{Tmax:10.3f}"
    )


# ============================================================
# COOLING PLOT
# ============================================================

cooling_results = np.array(
    cooling_results
)

plt.figure(figsize=(8, 5))

plt.plot(
    cooling_results[:, 0],
    cooling_results[:, 1],
    marker="o"
)

plt.axhline(
    45,
    linestyle="--",
    label="45°C reference"
)

plt.xlabel(
    "Convection Coefficient h (W/m²K)"
)

plt.ylabel(
    "Maximum Temperature (°C)"
)

plt.title(
    "Cooling Requirement for 2.5C Fast Charging"
)

plt.legend()

plt.grid(True)

plt.show()