import pandas as pd
import numpy as np
from NeuronsMemoryTestPipeline import MRT_text_processing
#from NeuronsMemoryTestPipeline.MRT_text_processing import clean_free_recall
pd.options.display.show_dimensions = False

def alias_group_define(df):
    """obtain all group values, split them and create a new column for each group_id
    Args:
        df (_type_): the alias dataframe
    Returns:
        _type_: updated dataframe with new group_id column
    """
    df.group_id = df.group_id.astype(str)
    new_rows = []
    for _, row in df.iterrows():
        if ',' in row['group_id']:
            groups = row['group_id'].split(',')
            for group in groups:
                new_row = row.copy()
                new_row['group_id_new'] = group
                new_rows.append(new_row)
    new_df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    if ',' in row['group_id']:
        new_df.loc[new_df['group_id_new'].isna(), 'group_id_new'] = new_df['group_id']
        new_df['group_id'] = new_df['group_id_new']
        new_df.drop('group_id_new', axis=1, inplace=True)
    new_df.dropna(subset=['group_id'], inplace=True)
    new_df.drop_duplicates(inplace=True)
    new_df = new_df.sort_values('group_id').reset_index(drop=True)
    new_df.group_id = new_df.group_id.astype(str)
    return new_df

def process_recall(df, filter_task, model, alias_df, group=['group_id']):
    """ Prepares the data, process it using text cleaning module, calculates free recall scores per group, including average position and average recall %.
    Args:
        df: dataframe with data from Jatos and identified MRT module plus task_name
        group (list): group by list that provides filter for grouping dataset
    Returns:
        df: updated data frame with the score column
    """

    df = df.loc[(df['task_name'] == filter_task) & (df['trial_name'].str.startswith('R-'))].copy()
    df['position'] = df['trial_name'].apply(lambda x: int(x.split('-')[-1]))
    
    df_cleaned = pd.DataFrame()
    corrected_entries = pd.DataFrame()
    for group in sorted(df.group_id.unique().tolist(), reverse=False):
        print(f'\n\n *** Group ID: {group} ***')
        df_group = df[df.group_id == group].copy()
        target_brands = (
            alias_df
            .loc[alias_df['group_id'] == group, 'mrt_stimulus']
            .dropna()
            .astype(str)
            .str.strip()
            .loc[lambda x: x != '']
            .unique()
            .tolist()
        )
        print(f'\nBRANDS used in the project for group {group}:')
        for brand in sorted(target_brands):
            print('  ', brand)
        
        total_responses = len(df_group.given_response_label_presented.dropna())
        print('*'*50)
        print(f'\nThere are {total_responses} entries in total.\n')
        print('Identified prior to adjustment: \n', df_group[df_group.given_response_label_presented.isin(target_brands)].given_response_label_presented.value_counts())
        df_group_tocorrect = df_group[~df_group.given_response_label_presented.isin(target_brands)].copy()
        df_group_tocorrect = df_group_tocorrect.dropna(subset=['given_response_label_presented'])
        df_group = df_group[df_group['given_response_label_presented'].isin(target_brands) | pd.isna(df_group['given_response_label_presented'])].copy()
        df_group['corrected'] = df_group['given_response_label_presented']
        df_group['method'] = 'original'
        responses_to_clean = df_group_tocorrect.given_response_label_presented.dropna().unique().tolist()
        print(f'\nThere are {len(responses_to_clean)} entries to clean further.')
        
        corrected_df = MRT_text_processing.clean_free_recall(df_group_tocorrect, target_brands, responses_to_clean, model)
        
        df_group = pd.concat([df_group, corrected_df], axis=0, ignore_index=True)
        
        df_cleaned = pd.concat([df_cleaned, df_group], axis=0, ignore_index=True)
        
    corrected_entries = df_cleaned[['group_id', 'given_response_label_presented', 'corrected', 'method']].copy()
    corrected_entries = corrected_entries[corrected_entries['method'] != 'not_match']
    corrected_entries = corrected_entries.sort_values('method', ascending=True).reset_index(drop=True)
    
    not_match = df_cleaned[['group_id', 'given_response_label_presented', 'corrected', 'method']].copy()
    not_match = not_match[not_match['method'] == 'not_match']
        
    print('*'*50)
    return df_cleaned, corrected_entries, not_match

def compute_scores(df_given: pd.DataFrame, group = ['group_id', 'project_identifier', 'task_name', 'corrected','total_participants']):
    """ Calculates: Average % , Average position, Average Log score based on position
    Args:
        df (dataframe): processed data frame with cleaned text
        no_recall (dataframe): dataset with brands that were not mentioned
    Returns:
        dataframe: updated dataframe with the scores columns
    """
    df = df_given.copy()
    df['corrected'] = df['corrected'].fillna(df['given_response_label_presented'])
    df['position_mean'] = df.groupby(group, observed=False)['position'].transform('mean')
    df['brand_count'] = df.groupby(group, observed=False)['position'].transform('count')   
    df['recall_%'] = df['brand_count'] / df['total_participants'] * 100  
    df['log_position'] = np.log(df['position_mean'] + 1)
    df['Freerecall'] = 1 / np.log(df['position_mean']+1) * df['recall_%']
    df['Freerecall'] = df['Freerecall'].clip(0, 100)
    df = df.sort_values('Freerecall', ascending=False).drop_duplicates().reset_index(drop=True)
    df = df [group + ['position_mean', 'brand_count', 'recall_%', 'log_position', 'Freerecall']].copy()
    df.rename(columns={'corrected':'mrt_stimulus'}, inplace=True)
    df = df.drop_duplicates().reset_index(drop=True)    
    return df