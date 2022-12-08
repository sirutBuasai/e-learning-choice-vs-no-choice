# Native libraries
import os
# External libraries
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from statsmodels.stats.weightstats import ttest_ind

#High and Low knowledge constants
lowKnowledgeBoundary = 0.55366019
highKnowledgeBoundary = 0.78819488

FALSE_DISCOVERY_RATE = 0.05

#list of pvalues for the bh procedure
listOfBHObjects = []

class BHObject:
    def __init__(self, experimentId, columnTitle, pvalue):
        self.experimentId = experimentId
        self.columnTitle = columnTitle
        self.pvalue = pvalue
        self.procedureValue = None

def computeBHProcedure():
    global listOfBHObjects

    BHProcedureTable = pd.DataFrame(columns=["experiment_id", "pvalue_type", "pvalue", "bh_procedure_value"])
    listOfBHObjects.sort(key=lambda o: o.pvalue)
    for i in range(len(listOfBHObjects)):
        listOfBHObjects[i].procedureValue = ((i+1)/len(listOfBHObjects))*FALSE_DISCOVERY_RATE
        BHProcedureTable.loc[len(BHProcedureTable.index)] =  [listOfBHObjects[i].experimentId, listOfBHObjects[i].columnTitle, listOfBHObjects[i].pvalue, listOfBHObjects[i].procedureValue]
    
    return BHProcedureTable

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
    print(f"Total number of studets in experiment: {len(concatFrame)}")
    values = concatFrame['student_prior_average_correctness'].to_numpy()
    print(f"Total Experiments percentile values (0, 25, 50, 75, 100): {np.percentile(values, [0, 25, 50, 75, 100])}")
    return np.percentile(values, [0, 25, 50, 75, 100])

def per_experiment_tests(data, id):
    global listOfBHObjects
    print(id)

    #For experiment PSAUTWT, we need to convert the end_time column to either a 1 or 0 depending on if it has a value (no value means not completed, value means it was completed)
    if id == "PSAUTWT":
        data["alogs"]["end_time"] = data["alogs"]["end_time"].apply(lambda value: 0 if pd.isnull(value) else 1)

    #Check choice vs no choice for all
    control = data["alogs"][data['alogs']['assigned_condition'].str.contains("Control")][get_dependent_variable(id)]
    control = control.dropna()
    
    treatment = data["alogs"][data['alogs']['assigned_condition'].str.contains("Treatment")][get_dependent_variable(id)]
    treatment = treatment.dropna()
  
    baseline_meanDifference = np.mean(treatment) - np.mean(control)
    basline_pvalue = ttest_ind(control, treatment)[1]

    print(f'mean difference for baseline: {baseline_meanDifference}')
    print(f'p-value for baseline: {basline_pvalue}')

    #Seperate into covariate groups (high/low knowledge, oz and no oz zone)

        #Lambda helper functions
    def highKnowledgeLabel(id, highKnowledgeIDList):
        if id in highKnowledgeIDList:
            return 1
        else:
            return 0

    def lowKnowledgeLabel(id, lowKnowledgeIDList):
        if id in lowKnowledgeIDList:
            return 1
        else:
            return 0

    def opportunityZoneLabel(id, opportunityZoneIDs):
        if id in opportunityZoneIDs:
            return 1
        else:
            return 0

    highKnowledgeStudentIDs = data["priors"][data["priors"]['student_prior_average_correctness'] >= highKnowledgeBoundary]['student_id']
    highKnowledgeStudentIDs = highKnowledgeStudentIDs.dropna().to_numpy()
    data["alogs"]['highKnowledge'] = data["alogs"]['student_id'].apply(lambda id: highKnowledgeLabel(id, highKnowledgeStudentIDs))
    highKnowledgeControl = data["alogs"].loc[(data["alogs"]['assigned_condition'].str.contains("Control")) & (data["alogs"]['highKnowledge'] == 1)][get_dependent_variable(id)].dropna()
    highKnowledgeTreatment = data["alogs"].loc[(data["alogs"]['assigned_condition'].str.contains("Treatment")) & (data["alogs"]['highKnowledge'] == 1)][get_dependent_variable(id)].dropna()


    lowKnowledgeStudentIDs = data["priors"][data["priors"]['student_prior_average_correctness'] <= lowKnowledgeBoundary]['student_id']
    lowKnowledgeStudentIDs = lowKnowledgeStudentIDs.dropna().to_numpy()
    data["alogs"]['lowKnowledge'] = data["alogs"]['student_id'].apply(lambda id: lowKnowledgeLabel(id, lowKnowledgeStudentIDs))
    lowKnowledgeControl = data["alogs"].loc[(data["alogs"]['assigned_condition'].str.contains("Control")) & (data["alogs"]['lowKnowledge'] == 1)][get_dependent_variable(id)].dropna()
    lowKnowledgeTreatment = data["alogs"].loc[(data["alogs"]['assigned_condition'].str.contains("Treatment")) & (data["alogs"]['lowKnowledge'] == 1)][get_dependent_variable(id)].dropna()


    opportunityZoneStudentIDs = data["priors"][data["priors"]['opportunity_zone'] == "Yes"]['student_id']
    opportunityZoneStudentIDs = opportunityZoneStudentIDs.dropna().to_numpy()
    data["alogs"]['opportunityZone'] = data["alogs"]['student_id'].apply(lambda id: opportunityZoneLabel(id, opportunityZoneStudentIDs))

    opportunityZoneControl = data["alogs"].loc[(data["alogs"]['assigned_condition'].str.contains("Control")) & (data["alogs"]['opportunityZone'] == 1)][get_dependent_variable(id)].dropna()
    opportunityZoneTreatment = data["alogs"].loc[(data["alogs"]['assigned_condition'].str.contains("Treatment")) & (data["alogs"]['opportunityZone'] == 1)][get_dependent_variable(id)].dropna()

    nonOpportunityZoneControl = data["alogs"].loc[(data["alogs"]['assigned_condition'].str.contains("Control")) & (data["alogs"]['opportunityZone'] == 0)][get_dependent_variable(id)].dropna()
    nonOpportunityZoneTreatment = data["alogs"].loc[(data["alogs"]['assigned_condition'].str.contains("Treatment")) & (data["alogs"]['opportunityZone'] == 0)][get_dependent_variable(id)].dropna()

    #Find correlation between covriate groups. If there is then just do the prior knowledge level tests
    highKnowledgeLables = data["alogs"]['highKnowledge'].to_numpy()
    lowKnowledgeLables = data["alogs"]['lowKnowledge'].to_numpy()
    opportunityZoneLables = data["alogs"]['opportunityZone'].to_numpy()
    correlation_highKnowledgeOpportunityZone, _ = pearsonr(highKnowledgeLables, opportunityZoneLables)
    correlation_lowKnowledgeOpportunityZone, _ = pearsonr(lowKnowledgeLables, opportunityZoneLables)

    print(f'Correlation for high knowledge and OZ: {correlation_highKnowledgeOpportunityZone}')
    print(f'Correlation for low knowledge and OZ: {correlation_lowKnowledgeOpportunityZone}')

    #Perform two sample t-tests
    highKnowledge_pvalue = ttest_ind(highKnowledgeControl, highKnowledgeTreatment)[1]
    highKnowledge_meanDifference = np.mean(highKnowledgeControl.to_numpy()) - np.mean(highKnowledgeTreatment.to_numpy())
    lowKnowledge_pvalue = ttest_ind(lowKnowledgeControl, lowKnowledgeTreatment)[1]
    lowKnowledge_meanDifference = np.mean(lowKnowledgeControl.to_numpy()) - np.mean(lowKnowledgeTreatment.to_numpy())
    opportunityZone_pvalue = ttest_ind(opportunityZoneControl, opportunityZoneTreatment)[1]
    opportunityZone_meanDifference = np.mean(opportunityZoneControl.to_numpy()) - np.mean(opportunityZoneTreatment.to_numpy())
    nonOpportunityZone_pvalue = ttest_ind(nonOpportunityZoneControl, nonOpportunityZoneTreatment)[1]
    nonOpportunityZone_meanDifference = np.mean(nonOpportunityZoneControl.to_numpy()) - np.mean(nonOpportunityZoneTreatment.to_numpy())

    print(f'Mean difference for High Knowledge: {highKnowledge_meanDifference}')
    print(f'p-value for High Knowledge: {highKnowledge_pvalue}')
    print(f'Mean difference for Low Knowledge: {lowKnowledge_meanDifference}')
    print(f'p-value for Low Knowledge: {lowKnowledge_pvalue}')
    print(f'Mean difference for Opportunity Zone: {opportunityZone_meanDifference}')
    print(f'p-value for Opportunity Zone: {opportunityZone_pvalue}')
    print(f'Mean difference Non Opportunity Zone: {nonOpportunityZone_meanDifference}')
    print(f'p-value for Non Opportunity Zone: {nonOpportunityZone_pvalue}')


    #Add pvalues to list for BH procedure
    listOfBHObjects.append(BHObject(id, "baseline_pvalue", basline_pvalue))
    listOfBHObjects.append(BHObject(id, "highknowledge_pvalue", highKnowledge_pvalue))
    listOfBHObjects.append(BHObject(id, "lowknowledge_pvalue", lowKnowledge_pvalue))
    listOfBHObjects.append(BHObject(id, "opportunityzone_pvalue", opportunityZone_pvalue))
    listOfBHObjects.append(BHObject(id, "nonopportunityzone_pvalue", nonOpportunityZone_pvalue))

    #Report date in a table
    return [id,
    baseline_meanDifference, basline_pvalue, correlation_highKnowledgeOpportunityZone, correlation_lowKnowledgeOpportunityZone,
    highKnowledge_meanDifference, highKnowledge_pvalue,
    lowKnowledge_meanDifference, lowKnowledge_pvalue,
    opportunityZone_meanDifference, opportunityZone_pvalue,
    nonOpportunityZone_meanDifference, nonOpportunityZone_pvalue]

def main():
    experiment_path = 'experiment_data/'
    allData = {}
    experimentResults = pd.DataFrame(columns=['experiment_id', 
    'baseline_treatmenteffect', 'baseline_pvalue', 'correlation_highKnowledgeOpportunityZone', 'correlation_lowKnowledgeOpportunityZone', 
    'highknowledge_treatmenteffect', 'highknowledge_pvalue',
    'lowknowledge_treatmenteffect', 'lowknowledge_pvalue',
    'opportunityzone_treatmenteffect', 'opportunityzone_pvalue',
    'nonopportunityzone_treatmenteffect', 'nonopportunityzone_pvalue',])

    #Perform tests per experiment in this loop:
    for dir in os.listdir(experiment_path):
        exp_dir = os.path.join(experiment_path, dir)
        data = load_experiment(exp_dir)
        allData[exp_dir] = data
        experimentResults.loc[len(experimentResults.index)] =  per_experiment_tests(data, dir)

    #Perform tests on all the experiments here:
    get_percentile_data(allData)
    print("Performing BH procedure on pvalues")
    bhDataFrame = computeBHProcedure()

    print("Outputting to file")
    experimentResults.to_csv("experimentResults.csv", index=False)
    bhDataFrame.to_csv("bhProcedureResults.csv", index=False)

if __name__ == "__main__":
    main()
