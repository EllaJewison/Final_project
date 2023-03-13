"""
main script to run pipline and models
"""

# packages
import os
import sys

SCRIPT_PATH = os.path.realpath(__file__)

# seats in the main entry to the repo, removing only file name
SCRIPT_NAME = "main.py"
PROJECT_DIR = SCRIPT_PATH[:-len(SCRIPT_NAME)]

sys.path.append(os.path.join(PROJECT_DIR, "src"))
from imports import *

def main():
    """program skeleton"""

    args = get_args()
    # args = {"clip":True, "derive":True, "scale":True, "reduce":True, "fourier":True, "model":random_forest}

    # load cleaned data
    labels, features = load_data(PROJECT_DIR)

    # split train test
    x_train, y_train, x_test, y_test = split(labels, features)

    # unsupervised preps
    pre_preps = ["scale", "clip", "derive", "fourier"]
    for key, value in args.items():
        if key in pre_preps and value:
            x_train = eval(f"{key}(x_train)")
            x_test = eval(f"{key}(x_test)")

    # supervised preps
    post_preps = ["reduce"]
    for key, value in args.items():
        if key in post_preps and value:
            x_train = eval(f"{key}(y_train, x_train)")
            x_test = eval(f"{key}(y_test, x_test)")

    # modeling
    model = args['model']
    report = eval(f"{model}(x_train, y_train, x_test, y_test)")

    # saving metrics
    log_metrics(report, args, PROJECT_DIR)
    report_summary = summeries_multiclass_report(report)
    return report_summary

if __name__ == "__main__":
    print(main())
