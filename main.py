# Native libraries
import os
# External libraries
import pandas as pd
import numpy as np
from statsmodels.stats.weightstats import ttest_ind

#High and Low knowledge constants
lowKnowledge = 0.55366019
highKnowledge = 0.78819488

def get_dependent_variable(id):
    match id:
        case "PSA59TP":
            return "posttest_correct"
        case "PSA98J7":
            return "posttest_correct"
        case "PSARZX2":
            return "condition_total_correct"
        case "PSATZEJ":
            return "condition_problem_count"
        case "PSAU4JD":
            return "condition_total_correct"
        case "PSAUTWT":
            return "end_time"
        case "PSAUTWU":
            return "condition_total_correct"
        case "PSAUUKY":
            return "condition_total_correct"
        case "PSAWHF4":
            return "condition_problem_count"
        case "PSAYN42":
            return "posttest_correct"
        case "PSAZ2G4":
            return "posttest_correct"
        case _:
            return "Error name did not match"
        


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
    print(f"Total Experiments percentile values (0, 25, 50, 75, 100): {np.percentile(values, [0, 25, 50, 75, 100])}")
    return np.percentile(values, [0, 25, 50, 75, 100])

def per_experiment_tests(data, id):
    print(id)
    #Check choice vs no choice for all
    control = data["alogs"][data['alogs']['assigned_condition'].str.contains("Control")][get_dependent_variable(id)]
    control = control.dropna()
    
    treatment = data["alogs"][data['alogs']['assigned_condition'].str.contains("Treatment")][get_dependent_variable(id)]
    treatment = treatment.dropna()
  
    results = ttest_ind(control, treatment)
    print(f'p-value for experiment {id}: {results[1]}')

    #Seperate into covariate groups (high/low knowledge, oz and no oz zone)

    #Find correlation between covriate groups. If there is then just do the prior knowledge level tests

    #Perform two sample t-tests

    #Report p-values in table

if __name__ == "__main__":
    experiment_path = 'experiment_data/'
    allData = {}

    #Perform tests per experiment in this loop:
    for dir in os.listdir(experiment_path):
        exp_dir = os.path.join(experiment_path, dir)
        data = load_experiment(exp_dir)
        allData[exp_dir] = data

        if dir != "PSAUTWT" and dir != "PSAZ2G4":
            per_experiment_tests(data, dir)

    #Perform tests on all the experiments here:
    #get_percentile_data(allData)

    
