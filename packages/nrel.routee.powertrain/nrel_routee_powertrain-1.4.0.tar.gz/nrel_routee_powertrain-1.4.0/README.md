# <img src="docs/images/routeelogo.png" alt="Routee Powertrain" width="100"/>

<div align="left">
    <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue"/>
  <a href="https://pypi.org/project/nrel.routee.powertrain/">
    <img src="https://img.shields.io/pypi/v/nrel.routee.powertrain" alt="PyPi Latest Release"/>
  </a>
</div>

## Overview

RouteE-Powertrain is a Python package that allows users to work with a set of pre-trained mesoscopic vehicle energy prediction models for a varity of vehicle types. Additionally, users can train their own models if "ground truth" energy consumption and driving data are available. RouteE-Powertrain models predict vehicle energy consumption over links in a road network, so the features considered for prediction often include traffic speeds, road grade, turns, etc.

The typical user will utilize RouteE's catalog of pre-trained models. Currently, the
catalog consists of light-duty vehicle models, including conventional gasoline, diesel,
hybrid electric (HEV), plugin hybrid electric (PHEV) and battery electric (BEV). These models can be applied to link-level driving data (in the form
of [pandas](https://pandas.pydata.org/) dataframes) to output energy consumption predictions.

Users that wish to train new RouteE models can do so. The model training function of RouteE enables users to use their
own drive-cycle data, powertrain modeling system, and road network data to train custom models.

## Quickstart

RouteE Powertrain is available on PyPI and can be installed with `pip`:

```bash
pip install pip --upgrade
pip install nrel.routee.powertrain
```

If `pip` is unavailable, use `pip3`:
```bash
pip3 install pip --upgrade
pip3 install nrel.routee.powertrain
```

(For more detailed instructions, see [here](https://nrel.github.io/routee-powertrain/installation.html))

Then, you can import the package and use a pre-trained model from the RouteE model catalog:

```python
import pandas as pd
import nrel.routee.powertrain as pt

# Print the available pre-trained models
print(pt.list_available_models(local=True, external=True))

# [
#   '2016_TOYOTA_Camry_4cyl_2WD',
#   '2017_CHEVROLET_Bolt',
#   '2012_Ford_Focus',
#   ...
# ]

# Load a pre-trained model
model = pt.load_model("2016_TOYOTA_Camry_4cyl_2WD")

# Inspect the model to see what it expects for input
print(model)

# ========================================
# Model Summary
# --------------------
# Vehicle description: 2016_TOYOTA_Camry_4cyl_2WD
# Powertrain type: ICE
# Number of estimators: 2
# ========================================
# Estimator Summary
# --------------------
# Feature: speed_mph (mph)
# Distance: miles (miles)
# Target: gge (gallons_gasoline)
# Raw Predicted Consumption: 29.856 (miles/gallons_gasoline)
# Real World Predicted Consumption: 25.606 (miles/gallons_gasoline)
# ========================================
# Estimator Summary
# --------------------
# Feature: speed_mph (mph)
# Feature: grade_dec (decimal)
# Distance: miles (miles)
# Target: gge (gallons_gasoline)
# Raw Predicted Consumption: 29.845 (miles/gallons_gasoline)
# Real World Predicted Consumption: 25.596 (miles/gallons_gasoline)
# ========================================

# Predict energy consumption for a set of road links
links_df = pd.DataFrame(
    {
        "distance": [0.1, 0.2, 0.3], # miles
        "speed_mph": [30, 40, 50], # mph
        "grade_percent": [-0.5, 0, 0.5], # percent
    }
)

energy_result = model.predict(links_df)
```
