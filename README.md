# CS 565 User Modeling Final Project
## Choice vs. No Choice in E-Learning Environment
#### Sirut Buasai, sbuasai2@wpi.edu; Christopher Guerrette, cjgourrette@wpi.edu; Conor McKevitt, cmmckevitt@wpi.edu


### Data Gathering process
1. Load datasets
2. Perform a baseline test on whether choice/no-choice has an impact
    * Compare two sample t-test on choice/no-choice groups for each experiment
2. Separate the students based on covariates
    * Create one table each for high/low knowledge and rich/poor students (4 separate tables for each experiment)
    * Check correlation between high/low knowledge and rich/poor students
4. Perform two sample t-test on the choice/no-choice conditions for each of the covariate groups and report the p-values
5. Repeat the two sample t-test on the choice groups with the covariate groups
    * Find how choice 1 or choice 2 affect group 1 and group 2 separately
6. Perform Benjamini–Hochberg procedure when reporting multiple p-values
