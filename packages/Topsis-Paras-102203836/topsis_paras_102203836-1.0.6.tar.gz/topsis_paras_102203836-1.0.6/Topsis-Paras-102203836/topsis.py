
import pandas as pd
import numpy as np
import sys
import os

def topsis(input_file, weights, impacts, output_file):
    try:
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Error: File '{input_file}' not found.")
        
        if os.stat(input_file).st_size == 0:
            raise ValueError(f"Error: The file '{input_file}' is empty.")
        
        data = pd.read_csv(input_file)

        if data.shape[1] < 3:
            raise ValueError("Error: Input file must contain at least three columns.")
        
        if data.iloc[:, 0].isnull().any():
            raise ValueError("Error: The first column (object/variable names) contains empty values.")
        
        fund_names = data.iloc[:, 0]  
        matrix = data.iloc[:, 1:]  

        if not all(np.issubdtype(matrix[col].dtype, np.number) for col in matrix.columns):
            raise ValueError("Error: All columns from 2nd to last must contain numeric values.")
        
        weights = weights.split(",")
        if len(weights) != matrix.shape[1]:
            raise ValueError("Error: The number of weights must match the number of criteria columns.")
        
        try:
            weights = [float(w) for w in weights]
        except ValueError:
            raise ValueError("Error: All weights must be numeric.")

        impacts = impacts.split(",")
        if len(impacts) != matrix.shape[1]:
            raise ValueError("Error: The number of impacts must match the number of criteria columns.")
        
        if not all(i in ['+', '-'] for i in impacts):
            raise ValueError("Error: Impacts must be either '+' or '-'.")
        
        # Step 1: Normalizing the decision matrix
        norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))

        # Step 2: Weight the normalized decision matrix
        weighted_matrix = norm_matrix * weights

        # Step 3: Determining ideal best and worst values
        ideal_best = []
        ideal_worst = []
        for i in range(len(impacts)):
            if impacts[i] == '+':
                ideal_best.append(weighted_matrix.iloc[:, i].max())
                ideal_worst.append(weighted_matrix.iloc[:, i].min())
            elif impacts[i] == '-':
                ideal_best.append(weighted_matrix.iloc[:, i].min())
                ideal_worst.append(weighted_matrix.iloc[:, i].max())

        ideal_best = np.array(ideal_best)
        ideal_worst = np.array(ideal_worst)

        # Step 4: Calculating the distance from ideal best and worst
        distance_best = np.sqrt(((weighted_matrix - ideal_best)**2).sum(axis=1))
        distance_worst = np.sqrt(((weighted_matrix - ideal_worst)**2).sum(axis=1))

        # Step 5: Calculating the TOPSIS score
        topsis_score = distance_worst / (distance_best + distance_worst)

        # Step 6: Rank the alternatives
        data['Topsis Score'] = topsis_score
        data['Rank'] = data['Topsis Score'].rank(ascending=False, method='min').astype(int)

        # Save to output file
        data.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")

    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Command-line execution
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python <RollNumber>.py <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        print("Example: python 101556.py 101556-data.csv \"1,1,1,2\" \"+,+,-,+\" 101556-result.csv")
    else:
        input_file = sys.argv[1]
        weights = sys.argv[2]
        impacts = sys.argv[3]
        output_file = sys.argv[4]
        
        topsis(input_file, weights, impacts, output_file)
