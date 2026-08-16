# Physics-Based Electro-Thermal Modeling of a Lithium-Ion Battery Cell

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
