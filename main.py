# Native libraries
import os
# External libraries
import pandas as pd


def load_experiment(experiment_dir):
    """Load experiment csv files and convert them to pandas dataframe
        experiment_dir (os.path): experiment directory name
    """
    alogs = pd.read_csv(os.path.join(experiment_dir, 'exp_alogs.csv'))
    plogs = pd.read_csv(os.path.join(experiment_dir, 'exp_plogs.csv'))
    slogs = pd.read_csv(os.path.join(experiment_dir, 'exp_slogs.csv'))
    priors = pd.read_csv(os.path.join(experiment_dir, 'priors.csv'))



if __name__ == "__main__":
    experiment_path = 'experiment_data/'
    for dir in os.listdir(experiment_path):
        exp_dir = os.path.join(experiment_path, dir)
