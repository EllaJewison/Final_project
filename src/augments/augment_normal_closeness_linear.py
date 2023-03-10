"""
augments the data and stores it as such
"""

# packages
import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal

SCRIPT_PATH = os.path.realpath(__file__)

def get_project_dir(script_path):
    project_dir = script_path[:-script_path[::-1].find("crs")-3]
    return project_dir

PROJECT_DIR = get_project_dir(SCRIPT_PATH)

sys.path.append(os.path.join(PROJECT_DIR, "src", "utils"))
from cmd_parse import get_args

def get_weight_matrix(n):
    """
    Generates a square matrix where the diagonal values are 1 and the off-diagonal values decay linearly
    from 1 to 0.
    """
    # Create an n x n identity matrix
    matrix = np.eye(n)
    
    # Compute the off-diagonal values using a linear decay function
    for i in range(n):
        for j in range(i+1, n):
            decay = 1 - (j - i) / (n - 1)
            matrix[i,j] = decay
            matrix[j,i] = decay
    
    return matrix

def augment(df, num):
    """
    generate signals based on multivariate normal distribution
    """
    # calculating covariance matrix and mean for distribution esstimation
    avg = np.mean(df, axis=0)
    cov = np.cov(df, rowvar=0)
    
    weight_matrix = get_weight_matrix(len(avg))
    cov_modify = np.multiply(cov, weight_matrix)
    
    multivar_norm = multivariate_normal(mean=avg, cov=cov_modify, allow_singular=True)
    samples = multivar_norm.rvs(size=num)
    
    samples_df = pd.DataFrame(samples, columns=df.columns)
    
    return samples_df
    

def main():
    """program skeleton"""
    args = get_args()
    
    # loading cleaned data
    features_file = os.path.join(PROJECT_DIR,"data", "splitted", "train", "features.csv")
        
    features = pd.read_csv(features_file)
    
    labels_file = os.path.join(PROJECT_DIR,"data", "splitted", "train", "labels.csv")
    labels = pd.read_csv(labels_file)
    
    # set id index
    features.set_index("ID", inplace=True)

    for label in labels["label"].unique():
        print(f"augmenting {label}")
        new_index = labels["ID"].max() + 1
        label_indice = labels["label"] == label
        label_features = features[label_indice]
        sample_features = augment(label_features, args["number"])
        sample_label = pd.DataFrame({"ID":new_index, "label":label}, index=range(args["number"]))
        sample_features.index = sample_features.index + new_index

        # append new row
        labels = pd.concat([labels, sample_label], axis=0, ignore_index=True)
        features = pd.concat([features, sample_features], axis=0)

    labels.to_csv(os.path.join(PROJECT_DIR,"data", "splitted", "train", "augmented", "labels.csv"), index=False)
    
    features.reset_index(inplace=True)
    features.rename(columns={"index":"ID"}, inplace=True)
    
    features.to_csv(os.path.join(PROJECT_DIR,"data", "splitted", "train", "augmented", "features.csv"), index=False)
        

if __name__ == "__main__":
    main()