from pandas import DataFrame
from financial_dataset_loader import load_menu_snapshot
from .menu3233_value_preprocessor import preprocess_cols_num_menu3233
from ..column_preprocessor_basis import remove_index_name, set_col_as_index

def set_custom_index(df: DataFrame) -> DataFrame:
    def create_index_name(row):
        return str(row['펀드코드']) + '-' + str(row['판매사']).replace(' ','')
    custom_index_name = df.apply(create_index_name, axis=1)
    return df.set_index(custom_index_name)

def preprocess_raw_menu3233(menu3233: DataFrame) -> DataFrame:
    return (
        menu3233
        .copy()
        .pipe(set_custom_index)
        .pipe(preprocess_cols_num_menu3233)
    )

def get_preprocessed_menu3233(date_ref=None):
    return preprocess_raw_menu3233(load_menu_snapshot('3233', date_ref=date_ref))

map_raw_to_preprocessed_menu3233 = preprocess_raw_menu3233
map_fund_code_to_preprocessed_menu3233 = get_preprocessed_menu3233
