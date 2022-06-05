#  Author: Kevin Cao

# Imports
from cProfile import label
from logging import PlaceHolder
import gradio as gr
import pandas as pd
import machine_learning
import transform_user_data
import warnings
from sklearn.ensemble import RandomForestRegressor

# Ignoring warning messages in terminal
warnings.filterwarnings('ignore')

# Loading Training Data
df = pd.read_csv('data/cleaned_no_outliers.csv')
columns = ['Rating', 'Company Size', 'Company Type', 'Company Revenue', 'Hourly', 'Employer Provided', 'Glassdoor Estimated', 'Job State', 'Company Age', 'Education Demanded', 'Python', 'SQL',
'Excel', 'AWS', 'Spark', 'Tableau', 'Scala', 'Big Data',
'Data Visualization', 'Description Length', 'Job Level', 'Job Label', 'Grouped Company Industry']
X_train = df[columns]
y_train = df['Average Salary']

# Examples
examples = [['Data Scientist', 'This job requires knowledge of Python, SQL, and AWS', 4.4, 'Example Company', 'City, State_Abbrev', '1 to 50 Employees', 2022, 'Company - Private', 'Retail Service', 'Less than $1 million (USD)']]

# Gradio Variables and Prediction Model
def predict_salary(company_name, rating, job_name, job_location, job_description, company_size, year_founded, company_type, company_revenue, grouped_sector):
    '''
    Defines interface for page, takes input values and predicts salary based off of input values. Returns predicted salary.
    '''
    cols_pd = ['Job Name', 'Job Description', 'Rating', 'Company Name', 'Job Location', 'Company Size', 'Year Founded', 'Company Type', 'Company Industry', 'Company Sector', 'Company Revenue']
    company_sector = '-1'
    values = [[job_name, job_description, rating, company_name, job_location, company_size, year_founded, company_type, grouped_sector, company_sector, company_revenue]]
    df_test = pd.DataFrame(values, columns=cols_pd)
    X_test = transform_user_data.clean_data(df_test)
    X_test['Hourly'] = 0
    X_test['Employer Provided'] = 0
    X_test['Glassdoor Estimated'] = 0
    X_test = X_test[['Rating', 'Company Size', 'Company Type', 'Company Revenue', 'Hourly', 'Employer Provided', 'Glassdoor Estimated', 'Job State', 'Company Age', 'Education Demanded', 'Python', 'SQL',
    'Excel', 'AWS', 'Spark', 'Tableau', 'Scala', 'Big Data',
    'Data Visualization', 'Description Length', 'Job Level', 'Job Label', 'Grouped Company Industry']]
    X_train_encoded, X_test_encoded = machine_learning.one_hot_encode_data(X_train, X_test)
    # From recursive feature elimination using random forest
    optimal_features = ['Company Size_10000+ Employees',
    'Company Size_1001 to 5000 Employees',
    'Company Size_201 to 500 Employees',
    'Company Size_5001 to 10000 Employees',
    'Company Size_501 to 1000 Employees',
    'Company Size_51 to 200 Employees',
    'Company Size_Unknown',
    'Company Type_Company - Public',
    'Company Type_Other',
    'Company Revenue_$1 to $5 million (USD)',
    'Company Revenue_$10+ billion (USD)',
    'Company Revenue_$100 to $500 million (USD)',
    'Company Revenue_$2 to $5 billion (USD)',
    'Company Revenue_$25 to $50 million (USD)',
    'Company Revenue_$5 to $10 billion (USD)',
    'Company Revenue_$500 million to $1 billion (USD)',
    'Company Revenue_Unknown / Non-Applicable',
    'Job State_Northeast',
    'Job State_Remote/Other',
    'Job State_South',
    'Job State_Southwest',
    'Job State_West',
    'Education Demanded_No Higher Education',
    'Job Level_Experienced',
    'Job Level_Other',
    'Job Label_Data Scientist',
    'Job Label_Machine Learning Engineer',
    'Job Label_Other',
    'Grouped Company Industry_Construction / Real Estate',
    'Grouped Company Industry_Energy & Transportation',
    'Grouped Company Industry_Entertainment',
    'Grouped Company Industry_Finance',
    'Grouped Company Industry_Government',
    'Grouped Company Industry_Health',
    'Grouped Company Industry_Manufacturing',
    'Grouped Company Industry_Retail',
    'Grouped Company Industry_Service',
    'Grouped Company Industry_Technology',
    'Grouped Company Industry_Unknown / Non-Applicable',
    'Rating',
    'Employer Provided',
    'Glassdoor Estimated',
    'Company Age',
    'Python',
    'SQL',
    'Excel',
    'AWS',
    'Spark',
    'Tableau',
    'Scala',
    'Big Data',
    'Data Visualization',
    'Description Length']
    X_train_encoded =  X_train_encoded[optimal_features]
    X_test_encoded = X_test_encoded[optimal_features]

    # Fitting Model
    rf_model = RandomForestRegressor(max_depth=8, max_features=45, min_samples_leaf=35, min_samples_split=100, n_estimators=165)
    rf_model.fit(X_train_encoded, y_train)

    # Predicting
    y_pred = rf_model.predict(X_test_encoded)[0]
    y_pred = int(round(y_pred, 0))
    result_string = '$' + str(y_pred) + ',000'
    return result_string

# Actual Gradio Interface
demo = gr.Interface(predict_salary,
[
    gr.inputs.Textbox(label='Company Name'),
    gr.Number(placeholder='Company rating out of 5. If unknown, enter -1', label='Company Rating'),
    gr.inputs.Textbox(label='Job Name'),
    gr.inputs.Textbox(label='Job Location'),
    gr.inputs.Textbox(label='Job Description'),
    gr.Radio(choices=['1 to 50 Employees', '51 to 200 Employees', '201 to 500 Employees', '501 to 1000 Employees', '1001 to 5000 Employees', '5001 to 10000 Employees', '10000+ Employees', 'Unknown'], label='Company Size'),
    gr.Number(placeholder='Year company was founded. If unknown, enter -1', label='Year Founded'),
    gr.Radio(['Company - Private',  'Company - Public', 'Other'], label='Company Type'),
    gr.Radio(['Less than $1 million (USD)', '$1 to $5 million (USD)', '$5 to $10 million (USD)', '$10 to $25 million (USD)', '$25 to $50 million (USD)', '$50 to $100 million (USD)', '$100 to $500 million (USD)', '$500 million to $1 billion (USD)', '$1 to $2 billion (USD)', '$2 to $5 billion (USD)', '$5 to $10 billion (USD)', '$10+ billion (USD)', 'Unknown / Non-Applicable'], label='Company Revenue'),
    gr.Radio(['Education', 'Retail Service', 'Health', 'Manufacturing', 'Finance', 'Communications', 'Entertainment', 'Technology', 'Construction / Real Estate', 'Energy & Transportation', 'Unknown / Non-Applicable'], label='Company Industry')
], outputs = 'label', examples=examples,
interpretation="default",
live=False, title='Data Scientist Salary Estimator'
)

demo.launch(share=True)
