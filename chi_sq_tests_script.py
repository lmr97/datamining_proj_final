# this script is intended to run all the chi squared tests. 
# My computer is horrendously slow, so it's for a faster computer.

print("\nImporting packages...")
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats.contingency import crosstab
import threading

global NUM_THREADS
global LOCK

NUM_THREADS = 4   # this can be changed to suit your machine
LOCK = threading.Lock()

def thread_worker():
    global CURR_COL
    global CURR_ROW
    while(CURR_ROW < len(cat_vars.columns)):
        LOCK.acquire()
        thread_row = CURR_ROW
        thread_col = CURR_COL
        CURR_ROW += 1               
        LOCK.release() 
        
        ctab_result = crosstab(cat_vars.iloc[:, thread_row], 
                               cat_vars.iloc[:, thread_col],
                                levels=(
                                    cat_vars.iloc[:, thread_row].unique(),
                                    cat_vars.iloc[:, thread_col].unique()))

        test_results = stats.chi2_contingency(ctab_result[1])
        chi_sq_tests[thread_row][thread_col] = test_results[1]  # load p-values into the grid
        # progress
        amount_completed = 100*((len(cat_vars.columns)*CURR_COL+CURR_ROW)/len(cat_vars.columns)**2)
        print(" row:", CURR_ROW, 
              "col:", CURR_COL, 
              "Progress: {:.2f}%".format(amount_completed),
              end="\r") 


print("Loading data...")
df = pd.read_csv("survey_results_public.csv")

cat_vars = df.drop(['Respondent', 
                    'Age', 
                    'CompTotal', 
                    'ConvertedComp',
                    'WorkWeekHrs'], 
                    axis=1)
cat_vars = pd.DataFrame(cat_vars, dtype=str)  

chi_sq_tests = np.zeros((len(cat_vars.columns),len(cat_vars.columns)))

print("Calculating chi-squared values...\n")
# multithreading
for i, label in enumerate(cat_vars.columns):

    # tell the interpreter that this is, in fact the global variables
    # I am using
    global CURR_COL
    global CURR_ROW

    # reset variables
    CURR_COL = i
    CURR_ROW = 0
    all_threads = []

    for j in range(NUM_THREADS):
        all_threads.append(threading.Thread(target=thread_worker, daemon=True))

    for j in range(NUM_THREADS):
        all_threads[j].start()

    for j in range(NUM_THREADS):
        all_threads[j].join()



# redefine as a DataFrame, to have labels
chi_sq_tests = pd.DataFrame(chi_sq_tests, 
                            columns=cat_vars.columns, 
                            index=cat_vars.columns)

round(chi_sq_tests,3).to_csv('chi_sq_tests.csv')
print("\nProcess complete and file exported.")