# TOPSIS

This script calculates the **TOPSIS** (Technique for Order Preference by Similarity to Ideal Solution) score and ranks alternatives based on the provided decision matrix, weights, and impacts. It uses the weights and impacts to determine the ideal best and worst values, then calculates the distance of each alternative from these values to derive the final score and ranking.

## Installation

There are no external dependencies, but you need to have **Python** and **pandas** installed to run the script.

```pip install Topsis-Paras-102203836```

## How to use it?
### Step 1: Prepare the Data
The input data should be a CSV file containing the following columns:

The first column should contain the fund names.
The remaining columns should contain the criteria values for each alternative (row).

### Step 2: Run the Script
To run the script, use the following command in the terminal:


<!-- python topsis.py data.csv "1,1,1,2,1" "+,+,-,+,-" results.csv( agar mereko chalana hai to ) -->
python -m Topsis-Paras-102203836.topsis data.csv "1,1,1,2,1" "+,+,-,+,-" results.csv

Where:

data.csv is your input CSV file (e.g., data.csv).

"1,1,1,2,1" is a comma-separated string of weights for each criterion (e.g., "1,1,1,2,1").

"+,+,-,+,-" is a comma-separated string of impacts for each criterion (e.g., "+,+,-,+,-").

results.csv is the file where the results will be saved (e.g., results.csv).

### Step 3: Output
The output will be a CSV file with the calculated TOPSIS scores and ranks for each alternative.
...

## Link to my package
### https://pypi.org/project/Topsis-Paras-102203836/