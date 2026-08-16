# Physics-Based Electro-Thermal Modeling of a Lithium-Ion Battery Cell

> **Python-based simulation of CC-CV fast charging, battery thermal behavior, and cooling requirements of a lithium-ion cell.**

## Project Highlights

| Parameter | Result |
|---|---:|
| Charging rates studied | 0.5C, 1.5C, 2.5C |
| Maximum temperature at 2.5C | **45.05 °C** |
| Charging time at 2.5C | **29.95 min** |
| Charging-time reduction vs 0.5C | **72.60%** |
| Model error at 2.5C vs literature | **0.56%** |
| Cooling coefficient studied | 5–100 W/m²K |

### Key Engineering Insight

Increasing the charging rate significantly reduces charging time but increases the thermal load on the cell. At 2.5C, the model predicts a maximum temperature of **45.05 °C**, compared with **27.85 °C at 0.5C**.

The cooling analysis shows that increasing the convective heat-transfer coefficient can significantly reduce the maximum cell temperature, demonstrating the importance of thermal management during fast charging.

---

## Overview

This project develops a Python-based physics-informed electro-thermal model of a lithium-ion battery cell to study the trade-off between charging speed and thermal behavior during CC-CV charging.

The model evaluates battery response at different charging rates and investigates how cooling conditions affect the maximum cell temperature.

The objective is to identify charging conditions that reduce charging time while maintaining acceptable thermal performance.

---

## Engineering Problem

Fast charging reduces charging time but increases heat generation inside the battery.

Excessive temperature rise can negatively affect:

- Battery performance
- Cycle life
- Safety
- Charging efficiency
- Thermal management requirements

Therefore, an important battery engineering problem is:

> **How can charging time be reduced without causing excessive temperature rise?**

This project addresses this problem using a simplified physics-based electro-thermal model.

---

## Model Scope

The model considers:

- Lithium-ion cylindrical cell
- Constant-current (CC) charging
- Constant-voltage (CV) charging
- State of charge (SOC)
- Electrical polarization
- Heat generation
- Convective heat dissipation
- Cell surface area
- Different C-rates
- Cooling optimization

The model was implemented in Python using NumPy, SciPy and Matplotlib.

---

## Charging Conditions

Three charging rates were investigated:

| C-rate | Charging Current |
|-------:|-----------------:|
|  0.5C  |     1.45 A       |
|  1.5C  |     4.35 A       |
|  2.5C  |     7.25 A       |

The CC-CV charging strategy was implemented by first charging at constant current and subsequently switching to constant-voltage operation.

---

## Results

### Thermal and Charging Performance

| C-rate | CC-CV Transition SOC | Maximum Temperature | Total Charging Time |
|-------:|---------------------:|--------------------:|--------------------:|
|  0.5C  |        97.75%        |     27.85 °C        |    109.31 min       |
|  1.5C  |        87.90%        |     34.31 °C        |    41.59 min        |
|  2.5C  |        75.78%        |     45.05 °C        |    29.95 min        |

### Key Observation

Increasing the charging rate significantly reduces charging time but increases the thermal load on the cell.

Compared with 0.5C:

- 1.5C reduces charging time by approximately **61.95%**
- 2.5C reduces charging time by approximately **72.60%**
- Temperature increases by approximately **6.47 °C** at 1.5C
- Temperature increases by approximately **17.20 °C** at 2.5C

This demonstrates the fundamental **fast-charging vs thermal-management trade-off**.

---

## Model Validation

The model was compared with selected temperature values obtained from literature.

| C-rate | Model Tmax | Literature Tmax | Absolute Error | Error |
|-------:|-----------:|----------------:|---------------:|------:|
|  1.5C  |  34.31 °C  |     39.20 °C    |    4.89 °C     | 12.47%|
|  2.5C  |  45.05 °C  |     45.30 °C    |    0.25 °C     | 0.56% |

The 2.5C case shows close agreement with the selected literature reference, while the 1.5C case indicates that further model refinement and parameter calibration could improve predictive accuracy.

---

## Cooling Optimization

The effect of the convective heat-transfer coefficient was investigated at 2.5C charging.

| h (W/m²K) | Maximum Temperature |
|----------:|--------------------:|
|     5     |      64.99 °C       |
|    10     |      56.34 °C       |
|    15     |      50.65 °C       |
|    20     |      46.62 °C       |
|    22.46  |      45.05 °C       |
|    30     |      41.38 °C       |
|    40     |      38.21 °C       |
|    50     |      36.15 °C       |
|    75     |      33.25 °C       |
|   100     |      31.75 °C       |

The analysis demonstrates that increasing the heat-transfer coefficient substantially reduces the predicted maximum cell temperature.

This provides a simple engineering framework for investigating the thermal-management requirement associated with fast charging.

## Skills Demonstrated

### Battery Engineering
- CC-CV charging analysis
- C-rate analysis
- SOC modeling
- Battery thermal management
- Heat-generation analysis
- Fast-charging analysis

### Computational Engineering
- Physics-based modeling
- Numerical simulation
- Parametric analysis
- Model validation against literature
- Cooling-system analysis

### Programming
- Python
- NumPy
- SciPy
- Matplotlib
- Pandas

---

## Project Workflow

```text
Literature Parameters
        ↓
Battery Cell Parameters
        ↓
Electrical Model
        ↓
Heat Generation Model
        ↓
Thermal Model
        ↓
CC-CV Charging Simulation
        ↓
Different C-rates
        ↓
Temperature & Charging-Time Analysis
        ↓
Cooling Optimization
        ↓
Literature Comparison
---
## References

1. D. M. Bernardi, E. M. Pawlikowski, and J. Newman,
   "A General Energy Balance for Battery Systems,"
   Journal of The Electrochemical Society, 132(1), 5–12, 1985.
   DOI: https://doi.org/10.1149/1.2113792

2. G. Joshi, L. N. Valluru, and A. P. Khade,
   "Two RC model and parameter estimation of lithium-ion battery,"
   Indonesian Journal of Electrical Engineering and Computer Science,
   Vol. 37, No. 2, pp. 730–739.
   DOI: https://doi.org/10.11591/ijeecs.v37.i2.pp730-739

3. "A Novel Electro-Thermal Model of Lithium-Ion Batteries
   Using Power as the Input,"
   Electronics, 10(22), 2753, 2021.
   https://doi.org/10.3390/electronics10222753

4. Literature sources used for the Panasonic NCR18650PF
   electrical and thermal characterization parameters.
