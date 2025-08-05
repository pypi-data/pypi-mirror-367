import os
import sys
import json
import pandas as pd

def tabulate_group(df,list):
    """Creates a tabulate of the given columns 
    Parameters
    ----------
    df: Dataframe we want to rename its columns
    list:List of the columns we want to group by with
    Returns
    -------
    The tabulate
    """
    return(df.groupby(list).size().reset_index())
    
def filter_conditions(df):
    module_name = df['module_name']
    reaction_time = df['reaction_time']

    if module_name in ['FRT-C_Em', 'FRT-C_Em-Pre', 'FRT-C_Em-Post']:
        if reaction_time < 350:
            return "Below"
        elif reaction_time > 2500:
            return "Above"
        else: return "Good"

    elif module_name == 'FRT-C_Mo':
        if reaction_time < 300:
            return "Below"
        elif reaction_time > 2500:
            return "Above"
        else: return "Good"
        
    elif module_name == 'FRT-B_Me':
        if reaction_time < 400:
            return "Below"
        elif reaction_time > 4000:
            return "Above"
        else: return "Good"


def check_files(args):
    if len(args) <= 1:
        sys.exit('Please provide all arguments: \nthe first one is the jatos and \nthe all demographics csv files' )
    else: print(f'You are processing {len(args)-1} demographic files')

    
def upload_jatos(file):
    if not os.path.exists(file):
        sys.exit(f'{file} - does not exist')
    if not os.path.isfile(file):
        sys.exit(f'{file} - is not a file')
    if os.path.splitext(file)[1] == '.txt':     # Load data from the jatos file (txt. file)
        l_d = []
        with open(file, encoding='UTF-8') as f:
            for line in f:
                l_d.append(json.loads(line))

        new_l_d = []
        for item in l_d:
            if isinstance(item, dict):
                new_l_d.append(item)
            elif isinstance(item, int):
                continue
            else:
                new_l_d.extend([b for b in item if b is not None])
        l_d = new_l_d

        for i in range(len(l_d)):
            d = l_d[i]
            if 'responses' in d.keys():
                d.update(json.loads(d['responses']))
                l_d[i] = d
        df_jatos = pd.DataFrame(l_d)
        df_jatos['behavioral_task_duration_dt'] = pd.to_timedelta(df_jatos['behavioral_task_duration'])
        df_jatos['behavioral_task_duration_minutes'] = df_jatos['behavioral_task_duration_dt'].dt.total_seconds() / 60
    else: 
        df_jatos = pd.read_csv(file, low_memory=False)
        df_jatos['participant_id'] = df_jatos['participant_id'].str.strip()
        df_jatos['participant_id'] = df_jatos['participant_id'].astype(str)
        df_jatos['reaction_time'] = pd.to_numeric(df_jatos['reaction_time'], errors= 'coerce')
    
    return df_jatos

def percent_calculation(df):
    if "Above" in df.columns and "Below" in df.columns:
        df["Sum"] = df["Above"].fillna(0) + df["Below"].fillna(0) + df["Good"]
    elif "Above" in df.columns:
        df["Sum"] = df["Above"].fillna(0) + df["Good"]
        print("There are no responses below the minimum.")
    elif "Below" in df.columns:
        df["Sum"] = df["Below"].fillna(0) + df["Good"]
        print ("There are no responses Above the maximum.")
    else:
        df["Sum"] = df["Good"]
        print("There are no responses outside the norm.")
    df["Good_percent"] = df["Good"]/df["Sum"]
    return df