# Native libraries
import os
# External libraries
import pandas as pd
import numpy as np


def load_experiment(experiment_dir):
    """Load experiment csv files and convert them to pandas dataframe
        experiment_dir (os.path): experiment directory name
    """

    data = {}

    data["alogs"] = pd.read_csv(os.path.join(experiment_dir, 'exp_alogs.csv'))
    data["plogs"] = pd.read_csv(os.path.join(experiment_dir, 'exp_plogs.csv'))
    data["slogs"] = pd.read_csv(os.path.join(experiment_dir, 'exp_slogs.csv'))
    data["priors"] = pd.read_csv(os.path.join(experiment_dir, 'priors.csv'))

    return data

def get_percentile_data(data):
        dropna = data["priors"]['student_prior_average_correctness'].dropna()
        values = dropna.to_numpy()
        return np.percentile(values, [0, 25, 50, 75, 100])

if __name__ == "__main__":
    experiment_path = 'experiment_data/'
    for dir in os.listdir(experiment_path):
        exp_dir = os.path.join(experiment_path, dir)
        data = load_experiment(exp_dir)

        print(f"Experiment: {exp_dir} percentile values (0, 25, 50, 75, 100): {get_percentile_data(data)}")
