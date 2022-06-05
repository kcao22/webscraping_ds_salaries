# Author: Kevin Cao

# Imports
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

# Input data
company_name = input('Please input company name: ')
rating = float(input('Please input company rating out of 5. If unknown, enter -1: '))
job_name = input('Please input job name: ')
job_location = input('Please input job location: ')
print('Please paste job description. At the end of the description, press Enter, then Ctrl-Z, and finally Enter again to finish: ')
contents = []
while True:
    try:
        line = input('')
    except EOFError:
        break
    contents.append(line)
job_description = ''.join([line for line in contents])
company_size = int(input('Please select the corresponding number to the company size: \n1. 1 to 50 Employees \n2. 51 to 200 Employees \n3. 201 to 500 Employees \n4. 501 to 1000 Employees \n5. 1001 to 5000 Employees \n6. 5001 to 10000 Employees \n7. 10000+ Employees \n8. Unknown  \n: ' ))
year_founded = input('Please input the year the company was founded. If unknown, enter -1: ')
company_type = int(input('Please select the corresponding number to the company size: \n1. Company - Private \n2. Company - Public \n3. Other  \n: '))
company_revenue = int(input('Please select the corresponding number to the company size: \n1. Less than $1 million (USD) \n2. $1 to $5 million (USD) \n3. $5 to $10 million (USD) \n4. $10 to $25 million (USD) \n5. $25 to $50 million (USD) \n5. $50 to $100 million (USD) \n6. $100 to $500 million (USD) \n7. $500 million to $1 billion (USD) \n8. $1 to $2 billion (USD) \n9. $2 to $5 billion (USD) \n10. $5 to $10 billion (USD) \n11. $10+ billion (USD) \n12. Unknown / Non-Applicable \n: ' ))
grouped_sector = int(input('Please select the corresponding number to the company sector of best fit: \n1. Education \n2. Retail Service \n3. Health \n4. Manufacturing \n5. Finance \n6. Communications \n7. Entertainment \n8. Technology \n9. Construction / Real Estate \n10. Energy & Transportation \n11. Unknown / Non-Applicable \n: ' ))
company_sector = '-1'

# Converting input integer to string choice
company_size_dict = {1: '1 to 50 Employees',
                     2: '51 to 200 Employees',
                     3: '201 to 500 Employees',
                     4: '501 to 1000 Employees',
                     5: '1001 to 5000 Employees',
                     6: '5001 to 10000 Employees',
                     7: '10000+ Employees',
                     8: 'Unknown'}
company_type_dict = {
                1: 'Company - Private',
                2: 'Company - Public',
                3: 'Other'
                }
company_revenue_dict = {
                1: 'Less than $1 million (USD)',
                2: '$1 to $5 million (USD)',
                3: '$5 to $10 million (USD)',
                4: '$10 to $25 million (USD)',
                5: '$25 to $50 million (USD)',
                6: '$50 to $100 million (USD)',
                7: '$100 to $500 million (USD)',
                8: '$500 million to $1 billion (USD)',
                9: '$2 to $5 billion (USD)',
                10: '$5 to $10 billion (USD)',
                11: '$10+ billion (USD)',
                12: '$1 to $2 billion (USD)',
                13: 'Unknown / Non-Applicable'
                }
grouped_sector_dict = {
                1: 'Education', 
                2:'Retail Service',
                3: 'Health',
                4: 'Manufacturing',
                5: 'Finance', 
                6: 'Communications',
                7: 'Entertainment',
                8: 'Technology',
                9: 'Construction / Real Estate',
                10: 'Energy & Transportation',
                11: 'Unknown / Non-Applicable'
                }
company_size = company_size_dict[company_size]
company_type = company_type_dict[company_type]
company_revenue = company_revenue_dict[company_revenue]
grouped_sector = grouped_sector_dict[grouped_sector]

# Loading user test dataset
cols_pd = ['Job Name', 'Job Description', 'Rating', 'Company Name', 'Job Location', 'Company Size', 'Year Founded', 'Company Type', 'Company Industry', 'Company Sector', 'Company Revenue']
values = [[job_name, job_description, rating, company_name, job_location, company_size, year_founded, company_type, grouped_sector, company_sector, company_revenue]]
df_test = pd.DataFrame(values, columns=cols_pd)

# Transforming user test data
X_test = transform_user_data.clean_data(df_test)
X_test = X_test[columns]

# Encoding data
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
print('The predicted salary for {job} at {company} is ${salary}k'.format(job=job_name, company=company_name, salary=y_pred))