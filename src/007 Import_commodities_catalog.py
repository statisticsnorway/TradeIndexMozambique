# # Import the chapter catalog from Excel

import pandas as pd

commodity_sitc = pd.read_excel(
    '../cat/Commodities_Catalogue_XPMI.xlsx',
    header=0,
    dtype=str,
    na_values={'.', ' .'}
).rename(columns={'Code': 'comno'})
commodity_sitc['sitc1'] = commodity_sitc['sitcr4_1']
commodity_sitc['sitc2'] = commodity_sitc['sitcr4_2']
commodity_sitc

commodity_sitc[['sitc1', 'Description sitcr4_1']].loc[commodity_sitc['sitc1'] == '7'].drop_duplicates(subset='sitc1',keep='first')


# ## Create labels for chapter
# Chapter is hs 2 digits. We create a function for this

def labels_from_cat(df, index, column, label_name, nan_txt='Other'):
    labels = (
    df[[index, column]]
        .drop_duplicates(subset=index,keep='first')
        .fillna(nan_txt)
        .sort_values(index)
        .set_index(index)
        .rename(columns={column: label_name})
        .to_dict()
    )
    return labels


# +
from typing import Union, Dict

def labels_from_cat(
    df: pd.DataFrame,
    index: str,
    column: str,
    label_name: str,
    nan_txt: str = 'Other',
    include_code: bool = False
) -> Dict[str, Dict[Union[str, int], str]]:
    """
    Extracts unique labels from a categorical column and maps them to index values,
    optionally including the index code in the label.

    This function drops duplicate index entries, replaces missing values in the
    specified column with `nan_txt`, sorts by index, and creates a dictionary
    mapping index values to their corresponding label. If `include_code` is True,
    the label is prefixed with the code.

    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        index (str): The column to use as the key/index in the resulting dictionary.
        column (str): The column containing the labels.
        label_name (str): The desired name of the label column in the resulting dictionary.
        nan_txt (str, optional): The text to replace NaN values in the label column. Defaults to 'Other'.
        include_code (bool, optional): Whether to include the index code before the label text. Defaults to False.

    Returns:
        Dict[str, Dict[Union[str, int], str]]:
            A dictionary of the form {label_name: {index_value: label, ...}}.

    Example:
        >>> import pandas as pd
        >>> data = pd.DataFrame({
        ...     'id': [1, 2, 2, 3, 4],
        ...     'category': ['A', 'B', 'B', None, 'D']
        ... })
        >>> labels_from_cat(data, index='id', column='category', label_name='label')
        {'label': {1: 'A', 2: 'B', 3: 'Other', 4: 'D'}}
        
        >>> labels_from_cat(data, index='id', column='category', label_name='label', include_code=True)
        {'label': {1: '1 A', 2: '2 B', 3: '3 Other', 4: '4 D'}}
    """
    tmp = (
        df[[index, column]]
        .drop_duplicates(subset=index, keep='first')
        .fillna(nan_txt)
        .sort_values(index)
        .copy()
    )

    if include_code:
        tmp[column] = tmp[index].astype(str) + ' ' + tmp[column].astype(str)

    labels = (
        tmp.set_index(index)
           .rename(columns={column: label_name})
           .to_dict()
    )
    return labels


# -

# Labels for chapter

chapter_labels = labels_from_cat(
    df=commodity_sitc, 
    index='SH2', 
    column='Descrição SH2', 
    label_name='chapter',
    include_code=True
)
chapter_labels

# Labels for sitc1

sitc1_labels = labels_from_cat(
    df=commodity_sitc, 
    index='sitc1', 
    column='Description sitcr4_1', 
    label_name='sitc1',
    include_code=True
)
sitc1_labels

# Labels for sitc2

sitc2_labels = labels_from_cat(
    df=commodity_sitc, 
    index='sitc2', 
    column='Description sitcr4_2', 
    label_name='sitc2',
    include_code=True
)
sitc2_labels

# Add labels together and save as a json file

labels = chapter_labels | sitc1_labels | sitc2_labels
with open('../cat/labels.json', 'w') as f:
    json.dump(labels, f, ensure_ascii=False, indent=4)

# ## Keep only the columns for match with commodities

commodity_sitc = commodity_sitc[['comno', 'sitc1', 'sitc2']]

# ## Save as parquet file

commodity_sitc.to_parquet('../cat/commodity_sitc.parquet')
print(f'\nNOTE: Parquet file ../cat/commodity_sitc.parquet written with {commodity_sitc.shape[0]} rows and {commodity_sitc.shape[1]} columns\n')
