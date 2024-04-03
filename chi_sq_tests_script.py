# this script is intended to run all the chi squared tests. 
# My computer is horrendously slow, so it's for a faster computer.

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats.contingency import crosstab

df = pd.read_csv("survey_results_public.csv")

cat_vars = df.drop(['Respondent', 
                    'Age', 
                    'CompTotal', 
                    'ConvertedComp',
                    'WorkWeekHrs'], 
                    axis=1)

chi_sq_tests = np.zeros((len(cat_vars.columns),len(cat_vars.columns)))
for i, rows in enumerate(cat_vars.columns):
    for j, cols in enumerate(cat_vars.columns):
        
        ctab_result = crosstab(cat_vars[rows], cat_vars[cols],
                               levels=(
                                   cat_vars[rows].unique(),
                                   cat_vars[cols].unique()))

        test_results = stats.chi2_contingency(ctab_result[1])
        chi_sq_tests[i][j] = test_results[1]  # load p-values into the grid
        print(i,j) # progress

# redefine as a DataFrame, to have labels
chi_sq_tests = pd.DataFrame(round(chi_sq_tests,), 
                            columns=cat_vars.columns, 
                            index=cat_vars.columns)
chi_sq_tests.to_csv('chi_sq_tests.csv')