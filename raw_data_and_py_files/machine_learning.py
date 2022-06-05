# Author: Kevin Cao

# Imports
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder




def split_data(df):
    '''
    Returns data split into training and testing data.
    '''
    X_train, X_test, y_train, y_test = train_test_split(df.drop(columns=['Average Salary']), df['Average Salary'], test_size=0.25, random_state=89)

    return X_train, X_test, y_train, y_test


def one_hot_encode_data(X_train, X_test):
    '''
    One hot encodes training and testing data. Fit / transforms training data and then encodes testing data. Ignores unknowns.
    '''
    X_train_cat = X_train.select_dtypes('object')
    X_train_num = X_train.select_dtypes('number')
    ohe = OneHotEncoder(drop='first', handle_unknown='ignore')
    ohe.fit(X_train_cat)
    transformed_train = ohe.transform(X_train_cat).toarray()
    X_train_cat_transformed = pd.DataFrame(transformed_train, columns=ohe.get_feature_names_out())

    X_train_encoded = pd.concat([X_train_cat_transformed.reset_index(drop=True), X_train_num.reset_index(drop=True)], axis=1)
    X_test_cat = X_test.select_dtypes('object')
    X_test_num = X_test.select_dtypes('number')
    transformed_test = ohe.transform(X_test_cat).toarray()
    X_test_cat_transformed = pd.DataFrame(transformed_test, columns=ohe.get_feature_names_out())
    X_test_encoded = pd.concat([X_test_cat_transformed.reset_index(drop=True), X_test_num.reset_index(drop=True)], axis=1)

    return X_train_encoded, X_test_encoded