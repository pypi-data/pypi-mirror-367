# statzy

A simple Python library for:
- get quick data overview 
- detecting and visualizing outliers in datasets
- etc.

## Installation

```bash
pip install statzy

## Usage
import statzy as st
import pandas as pd

data = pd.DataFrame({'value': [10, 12, 14, 110, 15]})
outliers, low, high = st.detect_outliers_iqr(data, 'value')
print(outliers)
