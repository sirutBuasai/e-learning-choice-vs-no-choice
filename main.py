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

def get_percentile_data(allData):
    listOfFrames = []
    for data in list(allData.values()):
        listOfFrames.append(data['priors'])

    concatFrame = pd.concat(listOfFrames, keys=['student_id', 'student_prior_average_correctness'])
    concatFrame.drop_duplicates(subset='student_id', inplace=True)
    concatFrame.dropna(inplace=True)
    values = concatFrame['student_prior_average_correctness'].to_numpy()
    return np.percentile(values, [0, 25, 50, 75, 100])

if __name__ == "__main__":
    experiment_path = 'experiment_data/'
    allData = {}

    for dir in os.listdir(experiment_path):
        exp_dir = os.path.join(experiment_path, dir)
        data = load_experiment(exp_dir)
        allData[exp_dir] = data

    print(f"Total Experiments percentile values (0, 25, 50, 75, 100): {get_percentile_data(allData)}")
