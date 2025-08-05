import pandas as pd
import numpy as np

def produce_demographics(df):
    """ Calculate age, gender, age_group bins demographics for the current 'group_id'
    Args:
        df (dataframe): given jatos dataframe
        id_col (str, optional): name of the column for participant id. Defaults to 'participant_id'.
        age_col (str, optional): name of the column for age data. Defaults to 'Age'.
        age_group (str, optional): name of the column for age_group split data. Defaults to 'Age_Group'.
        gender_col (str, optional): name of the column for gender. Defaults to 'Gender'.
        group_col (str, optional): name of the column(s) for grouping. Defaults to 'group_id'.
    Returns:
        three dataframes: the participants demographics data: age, age split, gender
    """
    age_demographics = df[['group_id','Age']].copy()
    age_demographics= age_demographics.groupby(['group_id'], observed=False)['Age'].agg(['min', 'max', 'mean', 'std']).reset_index()
    age_demographics.rename(columns={'group_id': 'group_id Age'}, inplace=True)
    age_demographics.set_index('group_id Age', inplace=True)
    print(f'AGE Statistics: \n {age_demographics}')

    age_group_count = df[['group_id','Age_Group','participant_id']].drop_duplicates()
    age_group_count= age_group_count.groupby(['group_id', 'Age_Group'], observed=False)['participant_id'].agg(['count']).reset_index()
    age_group_split = df[['group_id','Age_Group','Age']].drop_duplicates()
    age_group_split= age_group_split.groupby(['group_id', 'Age_Group'], observed=False)['Age'].agg(['min', 'max', 'mean', 'std']).reset_index()
    age_group_split = age_group_split.merge(age_group_count, on=['group_id','Age_Group'], how='left')
    print(f'\nAGE GROUP Statistics: \n {age_group_split}')

    df['total_participants'] = df.groupby('group_id')['participant_id'].transform('nunique')
    gender_demographics = df[['group_id', 'Gender', 'participant_id', 'total_participants']].drop_duplicates()
    gender_demographics= gender_demographics.groupby(['group_id', 'Gender', 'total_participants'], observed=False)['participant_id'].agg(['count']).reset_index()
    gender_demographics['percentage'] = np.round(100 * gender_demographics['count']/gender_demographics['total_participants'], 2)
    gender_demographics.reset_index(drop = True, inplace=True)
    gender_demographics.set_index(['group_id', 'total_participants', 'Gender'], inplace=True)
    print(f'\nGENDER Statistics: \n {gender_demographics}')
    return age_demographics, gender_demographics, age_group_split


def filter_reaction_time(df,module, bottom_t = 300, upper_t = 2500, participant_id_column = "participant_id"):
    """ Filter the data by specified upper and lower limits of the reaction time by participant
    Args:
        df (dataframe): : data frame with the results obtained from jatos
        column_name (str): the name of the column that should be considered for filtering
        lt (int, optional): Lower boundary. Defaults to 1000.
        ut (int, optional): Upper boundary. Defaults to 2500.
    Returns:
        dataframe: filtered dataframe
    """
    df = df[(df['module_name'] == module) & ((df['trial_name'] == 'Association'))].copy()
    print(f'Reaction Time for {module}: \n  {df["reaction_time"].describe().to_frame().T}')
    above_reaction_time_t = df.loc[(df.reaction_time > upper_t)]
    print('\nNumber of answers above the threshold:', len(above_reaction_time_t))
    print(round(len(above_reaction_time_t)/(df.shape[0] * 100), 2), '% of the responses')
    below_reaction_time_t = df.loc[(df.reaction_time < bottom_t)]
    print('Number of answers below the threshold:', len(below_reaction_time_t))
    print(round(len(below_reaction_time_t)/(df.shape[0] * 100), 2), '% of the responses')
    df_filtered = df.loc[df.reaction_time.between(bottom_t, upper_t, inclusive="neither")].reset_index(drop = True)
    print("With applying this filter we are excluding", (df[participant_id_column].nunique()-df_filtered[participant_id_column].nunique()), "participants from the initial sample")
    return df_filtered


def merge_dfs(df1, df2, group_columns=['frt_stimulus', 'frt_association', 'module_name', 'group_id']):
    """ Merging function, merge two pandas dataframe based on a list of grouping columns.
    Args:
        df1 : pandas dataframe
        df2 : pandas dataframe
        group_columns : list: Grouping columns, by default == ['frt_stimulus', 'frt_association', 'module_name']
    Returns :
        dataframe: Merged dataframe with column from both input dataframes(df1, df2)
    """
    merged_df = pd.merge(df1, df2, on=group_columns)
    return merged_df 

def process_data(df, ub=2500, group_columns=['frt_stimulus', 'frt_association', 'module_name', 'frt_response', 'group_id']):
    """ Process raw data to generate certainty, mean per participant and a pivot table of response counts: produce total count of groupings + renaming
    Args:
        df (dataframe): pre-filtered database
        ub (int, optional): _description_. Defaults to 25000.
        group_columns (list, optional): Columns to be used for grouping. Defaults to ['frt_stimulus', 'frt_association', 'module_name', 'frt_response', 'group_id'].
    Returns:
        dataframe: pivoted dataframe with total count of Yes and No responses
    """
    df.loc[:, 'certainty'] = ub - df['reaction_time'].copy()
    df.loc[:, 'mean_per_p'] = df.groupby(['participant_id', 'module_name'])['certainty'].transform('mean')

    gr_n = df.groupby(group_columns).size().reset_index(name='count')
    pivot_index = [x for x in group_columns if x != 'frt_response']
    gr_n_p = gr_n.pivot(index=pivot_index, columns='frt_response', values='count')
    gr_n_p = gr_n_p.reset_index()

    gr_n_p = gr_n_p.fillna(0)
    gr_n_p['Yes'] = 0 if 'Yes' not in gr_n_p.columns else gr_n_p['Yes']
    gr_n_p['No'] = 0 if 'No' not in gr_n_p.columns else gr_n_p['No']
    gr_n_p.rename(columns={"No": "N_grouping_No", "Yes": "N_grouping_Yes"}, inplace=True)
    gr_n_p['N_grouping_total'] = gr_n_p['N_grouping_No'] + gr_n_p['N_grouping_Yes']
    return gr_n_p


def group_quartiles(df, group_columns=['frt_stimulus', 'frt_association', 'module_name', 'frt_response', 'group_id'], value_col='certainty', group_zeroes=['participant_id', 'group_id', 'frt_response'] ):
    """ Getting quartiles : IQR
    Args:
        df (dataframe): preprocessed dataframe
        group_columns (list, optional): Columns to be used for grouping. Defaults to ['frt_stimulus', 'frt_association', 'module_name', 'frt_response', 'group_id'].
        value_col (str, optional): The column with the values used to calculate IQR. Defaults to 'certainty'.
        group_zeroes (list, optional): _description_. Defaults to ['participant_id', 'frt_response'].
    Returns:
        dataframe: updated dataframe with the IQR counts per group.
    """
    quartiles = df.groupby(group_columns)[value_col].apply(lambda x: np.percentile(x, [25, 75], interpolation='weibull'))
    quartiles_df = pd.DataFrame(quartiles.tolist(), columns=['IQR1_grouping', 'IQR3_grouping'], index=quartiles.index)
    quartiles_df['group_IQR'] = quartiles_df['IQR3_grouping'] - quartiles_df['IQR1_grouping']
    if (quartiles_df['group_IQR'] < 20).any():
        print("\n ***** There is values in Group IQR smaller than 20! ***** \n")
    result = merge_dfs(quartiles_df, df, group_columns=group_columns)
    result['group_IQR'] = result['group_IQR'].fillna(0)

    result['participant_mean'] = result.groupby(group_zeroes)['group_IQR'].transform('mean')
    result['group_IQR'] = np.where(result['group_IQR']<20, result['participant_mean'], result['group_IQR'])
    result.drop(columns=['participant_mean'], inplace=True)
    return result

def groupby_and_tabulate(df, group_columns=['frt_stimulus', 'frt_association', 'module_name', 'group_id'], value_col='group_IQR'):
    """ Grouping and Calculating Mean, 
        Pivoting to Wide Format, 
        Merging with Original DataFrame, 
        Handling 'Yes' and 'No' Columns, 
        Column Renaming and Dropping Duplicates.
    Args:
        df (dataframe): provided dataframe
        group_columns (list, optional): _description_. Defaults to ['frt_stimulus', 'frt_association', 'module_name', 'group_id'].
        value_col (str, optional): Column to use to calculate mean. Defaults to 'group_IQR'.
    Returns:
        dataframe: updated dataframe
    """
    grouped = df.groupby(group_columns + ['frt_response'])[[value_col]].mean().reset_index()
    pivot = grouped.pivot_table(index=group_columns, columns='frt_response', values=value_col).reset_index()
    merged = pd.merge(df[group_columns], pivot, on=group_columns)
    merged['Yes'] = 0 if 'Yes' not in merged.columns else merged['Yes']
    merged['No'] = 0 if 'No' not in merged.columns else merged['No']
    merged['Yes'] = merged['Yes'].fillna(0)
    merged['No'] = merged['No'].fillna(0)
    merged = merged.rename(columns={'Yes': 'g_iqr_yes', 'No': 'g_iqr_no'})
    merged = merged.drop_duplicates(subset=group_columns)
    return merged

def positive_negative(df, group_columns=['frt_stimulus', 'frt_association', 'module_name', 'group_id']):
    """ Identify if the most responses are Yes or No and create the column with the matching positive or negative label
    Args:
        df (dataframe): working dataframe
        group_columns (list, optional): grouping parameter. Defaults to ['frt_stimulus', 'frt_association', 'module_name', 'group_id'].
    Returns:
        dataframe: updated with the new column positive_negative
    """
    grouped = df.groupby(group_columns)['frt_response'].value_counts().reset_index(name="positive_negative")
    pivot = grouped.pivot_table(index=['frt_association', 'module_name'], columns='frt_response', values="positive_negative").reset_index()
    pivot['Yes'] = 0 if 'Yes' not in pivot.columns else pivot['Yes']
    pivot['No'] = 0 if 'No' not in pivot.columns else pivot['No']
    pivot['Yes'] = pivot['Yes'].fillna(0)
    pivot['No'] = pivot['No'].fillna(0)
    pivot["positive_negative"]=np.where(pivot['Yes']>=pivot["No"],"Positive", "Negative")
    return (pivot)

def calculate_certainty_formula(row, group_columns, iqr_col):
    """ Calculation of the certainty on the group_columns level, using encoded formula.
    Args:
        row (str or int):row of the dataframe to use for calculation
        group_columns (list): list of the name of the columns use for grouping
        iqr_col (str): name of the column use for calculation of the certainty (mainly group_iqr_yes or group_iqr_no)
    Returns:
        float: value that is being calculated
    """
    try: 
        numerator = row['certainty'] * (row[group_columns] / row['N_grouping_total']) * 2
        denominator = row['mean_per_p']
        exponent = ((row['g_iqr_yes'] + row['g_iqr_no']) / row[iqr_col]) / 2
        return (numerator / denominator) ** exponent
    except:
        print ('*** WARNING ***') 
        print(f"group_IQR {row['mean_per_p']} OR grouping size {row['N_grouping_total']} OR exponent {exponent} issue! \n")
        return 0
    
def calculate_certainty_score(row):
    """ Identifies the parameters of the row for further calculation of the certainty score
    Args:
        row (str or int): row of the dataframe
    Returns:
        float: value of the certainty score with the specific parameters
    """
    if row['positive_negative'] == "Positive":
        if row['N_grouping_No'] < 3:
            return 'small_no'
        if row['N_grouping_Yes'] < 3: 
            return 'small_yes'
        if row['frt_response'] == "Yes":
            return calculate_certainty_formula(row, 'N_grouping_Yes', 'g_iqr_yes')
        elif row['frt_response'] == "No":
            return calculate_certainty_formula(row, 'N_grouping_Yes', 'g_iqr_no')
    elif row['positive_negative'] == "Negative":
        if row['N_grouping_No'] < 3:  ######## CHECK and UPDATE
            return 'small_no'
        if row['N_grouping_Yes'] < 3: 
            return 'small_yes'
        if row['frt_response'] == "Yes":
            return calculate_certainty_formula(row, 'N_grouping_No', 'g_iqr_yes')
        elif row['frt_response'] == "No":
            return calculate_certainty_formula(row, 'N_grouping_No', 'g_iqr_no')


def produce_frt_score(df, group_columns=['frt_stimulus', 'frt_association', 'module_name', 'group_id'], certainty_col='certainty_score', response_col='frt_response', certainty='certainty'):
    """ Final step of the frt_score calculation that creates certainty agreement per group, calculates overall % of the yes and no responses and returns the metric frt score.
    Args:
        df (dataframe): dataframe preprocessed with the required columns
        group_columns (list, optional): Columns required for grouping. Defaults to ['frt_stimulus', 'frt_association', 'module_name', 'group_id', 'positive_negative'].
        certainty_col (str, optional): name of the column. Defaults to 'certainty_score'.
        response_col (str, optional): name of the column. Defaults to 'frt_response'.
        certainty (str, optional): name of the column. Defaults to 'certainty'.
    Returns:
        dataframe: the dataframe that contains frt_scores for each stimilus.
    """
    # BREAK CERTAINTY
    df_edge = df[(df[certainty_col] == 'small_no') | (df[certainty_col] == 'small_yes')].copy()
    df = df[(df[certainty_col] != 'small_no') & (df[certainty_col] != 'small_yes')].copy()
    grouped_df = df.groupby(group_columns).agg(
        certainty_sum_Yes = (certainty_col, lambda x: x[df[response_col] == 'Yes'].sum()),
        certainty_sum_No = (certainty_col, lambda x: x[df[response_col] == 'No'].sum()),
        certainty_Yes = (certainty, lambda x: x[df[response_col] == 'Yes'].mean()),
        certainty_No = (certainty, lambda x: x[df[response_col] == 'No'].mean()), 
        agreement_Yes = ('g_iqr_yes', 'mean'),
        agreement_No = ('g_iqr_no', 'mean'),
        N_Yes = (response_col, lambda x: (x == 'Yes').sum()),
        N_No = (response_col, lambda x: (x == 'No').sum()),
        N_Total = (response_col, 'count'),
    ).reset_index()
    
    grouped_df['%_Yes'] = (grouped_df['N_Yes'] / grouped_df['N_Total']) * 100
    grouped_df['%_No'] = (grouped_df['N_No'] / grouped_df['N_Total']) * 100
    grouped_df['frt_summation'] = grouped_df['certainty_sum_Yes'] + grouped_df['certainty_sum_No']
    grouped_df['frt_score'] = (grouped_df['certainty_sum_Yes'] / grouped_df['frt_summation']) * 100
    grouped_df['Scaling'] = (grouped_df['frt_score'] - grouped_df['%_Yes'])
    print('\n***** PLEASE CHECK: distribution of Scaling! *****')
    print(grouped_df['Scaling'].describe().to_frame().T)
    
    if df_edge.shape[0] > 0:
        df_edge['frt_score'] = 0
        df_edge['Scaling'] = 0
        df_edge.loc[df_edge[certainty_col] == 'small_no', 'frt_score'] = 100
        #df_edge.loc[df_edge[certainty_col] == 'small_yes', 'frt_score'] = 0
        #df_edge.loc[df_edge[certainty_col] == 'small_no', 'Scaling'] = 0
        #df_edge.loc[df_edge[certainty_col] == 'small_yes', 'Scaling'] = 0  #### CHECK and UPDATE
        df_edge['N_Yes'] = df_edge['N_grouping_Yes']
        df_edge['N_No'] = df_edge['N_grouping_No']
        df_edge['N_Total'] = df_edge['N_grouping_Yes'] + df_edge['N_grouping_No']
        df_edge['%_Yes'] = (df_edge['N_grouping_Yes'] / df_edge['N_Total']) * 100
        df_edge['%_No'] = (df_edge['N_grouping_No'] / df_edge['N_Total']) * 100
        df_edge = df_edge[group_columns + ['frt_score', 'N_Yes', 'N_No', 'N_Total', '%_Yes', '%_No', 'Scaling']].copy()
        df_edge.drop_duplicates(inplace=True)
        df_edge = df_edge.dropna(axis=1, how='all')
        grouped_df = grouped_df.dropna(axis=1, how='all')  
        grouped_df = pd.concat([grouped_df, df_edge], axis=0)
    return grouped_df

def frt_scores(df):
    """Step-by-step application of the memory recognition computation.
    Args:
        df (dataframe): initial dataframe
    Returns:
        dataframe: Dataframe with required scores including overall % and scores based on IQR and reaction time.
    """
    pre_process_overall = process_data(df)
    merged = merge_dfs(df, pre_process_overall)
    overall_quartiles = group_quartiles(merged)
    overall_quartiles['group_IQR'].describe()
    overall_response_d = groupby_and_tabulate(overall_quartiles)
    merged_iqr_n = merge_dfs(overall_quartiles, overall_response_d)
    pos_neg=positive_negative(merged_iqr_n)
    merged_iqr_n=pos_neg.merge(merged_iqr_n,on=['frt_association', 'module_name'])
    merged_iqr_n['certainty_score']  = merged_iqr_n.apply(calculate_certainty_score, axis=1)
    print(merged_iqr_n[(merged_iqr_n['certainty_score'] != 'small_no') & (merged_iqr_n['certainty_score'] != 'small_yes')]['certainty_score'].astype('float').describe().to_frame().T)
    print('\n***** PLEASE CHECK: edge cases! *****')
    print('Small number of No: ', merged_iqr_n[merged_iqr_n['certainty_score'] == 'small_no']['N_grouping_No'].unique())
    print('Small number of Yes: ', merged_iqr_n[merged_iqr_n['certainty_score'] == 'small_yes']['N_grouping_Yes'].unique())

    overall_frt = produce_frt_score(merged_iqr_n, certainty_col='certainty_score', response_col='frt_response')
    frt_score = overall_frt[['group_id', 'frt_stimulus', 'frt_association','frt_score']].round(2)
    frt_score.sort_values(['group_id','frt_stimulus']).reset_index(drop=True)
    frt_score = frt_score.sort_values(['group_id','frt_score']).reset_index(drop=True)
    return frt_score, overall_frt


def split_score(df, filter_list, column):
    """ Applies the filters, calculates recognition scores for each filtered DataFrame, 
        and merges them based on specific columns and suffixes.
    Args:
        df (DataFrame): DataFrame
        filter_list (list): list of filters: Male or Female,  Younger, Mid, Older
        column (str): a column on which to apply the filters: Gender or Age_Group
    Returns:
        DataFrame: DataFrame with the frt_scores based on the filters
    """
    split = pd.DataFrame()
    for filter_value in filter_list:
        filtered_df = df[df[column] == filter_value]
        split_part, split_part_scaling = frt_scores(filtered_df)
        split_part[column] = filter_value
        split = pd.concat([split, split_part], axis=0)
        split[column] = pd.Categorical(split[column], categories=filter_list, ordered=True)

    split.sort_values(['group_id','frt_stimulus','frt_association']+[column], inplace=True)
    index_cols = ['group_id', 'frt_stimulus', 'frt_association'] + [column]
    split.set_index(index_cols, inplace=True)
    return split, split_part_scaling
