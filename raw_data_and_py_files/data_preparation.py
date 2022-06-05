# Author: Kevin Cao

# Imports
import regex as re
import spacy

# All functions
def handle_incorrect_categories(df):
    '''
    Handles data that is misplaced in the incorrect categories from Glassdoor. For example, some "Company Revenue" information ends up in "Company Type".
    '''
    list_wrong_types = ['$1 to $5 million (USD)',
                        '$5 to $10 million (USD)',
                        'Less than $1 million (USD)'
                        ]
    list_wrong_sectors = [ '$1 to $2 billion (USD)',
                            '$1 to $5 million (USD)',
                            '$10 to $25 million (USD)',
                            '$10+ billion (USD)',
                            '$100 to $500 million (USD)',
                            '$50 to $100 million (USD)',
                            'Less than $1 million (USD)'
                        ]
    list_wrong_years  = [
                        'Company - Private',
                        'Company - Public',
                        'Contract',
                        'Government',
                        'Nonprofit Organization',
                        'Self-employed',
                        ]
    for wrong in list_wrong_types:
        df.loc[df['Company Type']==wrong, 'Company Revenue'] = wrong
        df.loc[df['Company Type']==wrong, 'Company Type'] = 'Unknown / Non-Applicable'
    for wrong in list_wrong_sectors:
        df.loc[df['Company Sector']==wrong, 'Company Revenue'] = wrong
        df.loc[df['Company Sector']==wrong, 'Company Sector'] = 'Unknown / Non-Applicable'
    for wrong in list_wrong_years:
        df.loc[df['Year Founded']==wrong, 'Company Type'] = wrong
        df.loc[df['Year Founded']==wrong, 'Year Founded'] = -1

    return df

def handle_missing(df):
    '''
    Handles missing values according to each columns Other / Unknown values. For numerical values, replace missing information with -1.
    '''
    df.loc[df['Company Type']=='-1', 'Company Type'] = 'Unknown / Non-Applicable'
    df['Company Type'] = df['Company Type'].fillna('Unknown / Non-Applicable')
    df.loc[df['Company Sector']=='-1', 'Company Sector'] = 'Unknown / Non-Applicable'
    df['Company Sector'] = df['Company Sector'].fillna('Unknown / Non-Applicable')
    df.loc[df['Company Revenue']=='-1', 'Company Revenue'] = 'Unknown / Non-Applicable'
    df['Company Revenue'] = df['Company Revenue'].fillna('Unknown / Non-Applicable')
    df.loc[df['Company Industry']=='-1', 'Company Industry'] = 'Unknown / Non-Applicable'
    df['Company Industry'] = df['Company Industry'].fillna('Unknown / Non-Applicable')
    df.loc[df['Company Size']=='-1', 'Company Size'] = 'Unknown'
    df['Company Size'] = df['Company Size'].fillna('Unknown')
    df.loc[df['Year Founded']=='-1', 'Year Founded'] = -1
    df.loc[df['Year Founded']=='Unknown', 'Year Founded'] = -1
    df['Year Founded'] = df['Year Founded'].fillna(-1)
    df['Rating'] = df['Rating'].fillna(-1)

    return df[df['Salary'].notnull()]


def consolidate_size(df):
    '''
    Certain labels are differentiated due to lower case 'employee' versus capitalized 'Employee'. Consolidating these categorical labels.
    '''
    df.loc[df['Company Size'] == '1 to 50 employees', 'Company Size'] = '1 to 50 Employees'
    df.loc[df['Company Size'] == '10000+ employees', 'Company Size'] = '10000+ Employees'
    df.loc[df['Company Size'] == '1001 to 5000 employees', 'Company Size'] = '1001 to 5000 Employees'
    df.loc[df['Company Size'] == '201 to 500 employees', 'Company Size'] = '201 to 500 Employees'
    df.loc[df['Company Size'] == '5001 to 10000 employees', 'Company Size'] = '5001 to 10000 Employees'
    df.loc[df['Company Size'] == '501 to 1000 employees', 'Company Size'] = '501 to 1000 Employees'
    df.loc[df['Company Size'] == '51 to 200 employees', 'Company Size'] = '51 to 200 Employees'

    return df

def convert_salary(df):
    '''
    Replaces job salaries with numeric values, handles salaries on hourly basis and annual basis. Assumes a 2080 hour work year.
    '''
    df = df[df['Salary'] != '-1']
    df['Hourly'] = df['Salary'].apply(lambda x: 1 if 'Per Hour' in x else 0)
    df['Employer Provided'] = df['Salary'].apply(lambda x: 1 if 'Employer Provided Salary:' in x else 0)
    df['Glassdoor Estimated'] = df['Salary'].apply(lambda x: 1 if '(Glassdoor est.)' in x else 0)
    salaries = df['Salary'].apply(lambda x: x.replace('(Glassdoor est.)', '').replace('Employer Provided Salary:', '').replace('(Employer est.)', '').replace('Per Hour', '').replace('()', '').replace(' - ', '-').replace('$', '').replace('K', '').strip())
    df['Lower Bound Salary'] = salaries.apply(lambda x: int(x.split('-')[0]))
    df['Upper Bound Salary'] = salaries.apply(lambda x: int(x.split('-')[-1]))
    df['Average Salary'] = (df['Lower Bound Salary'] + df['Upper Bound Salary']) / 2
    df['Lower Bound Salary'] = df.apply(lambda x: x['Lower Bound Salary'] * 2.080 if x['Hourly'] == 1 else x['Lower Bound Salary'], axis=1)  # Have to do df.apply because using two separate cols
    df['Upper Bound Salary'] = df.apply(lambda x: x['Upper Bound Salary'] * 2.080 if x['Hourly'] == 1 else x['Upper Bound Salary'], axis=1)
    df['Average Salary'] = df.apply(lambda x: x['Average Salary'] * 2.080 if x['Hourly'] == 1 else x['Average Salary'], axis=1)
    return df

def clean_locations(df):
    '''
    Converts the locations to states, remote, or country.
    Full state names to abbreviations:
        https://gist.github.com/rogerallen/1583593
    '''
    # If there is a comma in the value, then need to extract the state.
    # If remote, keep remote
    # If United States, keep United States
    locations = []
    us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",}
    df['Job Location'] = df['Job Location'].fillna('Remote')
    df.loc[df['Job Location'] == 'New York State', 'Job Location'] = 'New York State, NY'
    for state in df['Job Location']:
        if ',' not in state:
            if state in us_state_to_abbrev.keys():
                locations.append(us_state_to_abbrev[state])
            else:  # Remote
                locations.append(state)
        else:  # Comma in text
            locations.append(state.split(', ')[-1])
    df['Job State'] = locations

    return df

def group_locations(df):
    '''
    States are grouped together based on:
    https://en.wikipedia.org/wiki/List_of_regions_of_the_United_States#Census_Bureau-designated_regions_and_divisions
    Will be grouped into 4 total regions
    '''
    df = clean_locations(df)
    regions_to_states = {
    'South': ['WV', 'DC', 'MD', 'VA',
              'KY', 'TN', 'NC', 'MS',
              'AR', 'LA', 'AL', 'GA', 'SC',
              'FL', 'DE'],
    'Southwest': ['AZ', 'NM', 'OK', 'TX'],
    'West': ['WA', 'OR', 'CA', 'NV', 'ID', 'MT',
             'WY', 'UT', 'CO', 'AK', 'HI'],
    'Midwest': ['ND', 'SD', 'NE', 'KS', 'MN','IA', 
    'MO', 'WI', 'IL', 'MI', 'IN', 'OH'],
    'Northeast': ['ME', 'VT', 'NY', 'NH', 'MA', 'RI', 'CT', 'NJ', 'PA'],
    'Remote/Other': ['Remote', 'United States']
    }
    states_to_regions = {value: key for key in regions_to_states for value in regions_to_states[key]}
    df['Job State'] = df['Job State'].map(states_to_regions)

    return df

def convert_year_founded(df, current_year):
    '''
    Convert year founded to age of company by taking the difference between the year founded and the current year.
    '''
    df['Company Age'] = df['Year Founded'].apply(lambda x: x if x == -1 else current_year - int(x))

    return df

def higher_education(df):
    '''
    Takes job description and determines if higher education (Masters, PhD, PostDoc are mentioned.)
    '''
    education  = ["MSc","PhD", "Master", "Doctorate", "Postdoc"]
    edu_req = []
    for desc in df['Job Description']:
        if any(level.lower() in desc.lower() for level in education):
            edu_req.append('Higher Education')
        else:
            edu_req.append('No Higher Education')
    df['Education Demanded'] = edu_req

    return df

def find_top_skills(df):
    '''
    Finds the tops skills required 
    '''
    # Create batch of different data science related skills
    languages = ["Python", "C++", "MatLab", "C#", "C++" "JavaScript","Julia", "Pearl", "HTML", "Bash", "Java", "Scala", "SQL", "SAS", "R Studio", "R-Studio", "Swift", "D3", "Shiny", "RShiny"]
    software = ["Excel", "Tableau", "PowerBI", "Power BI", "Business Intelligence", "Data Visualization"]
    big_data  = ["Big Data", "ETL", "Atlas", "Spark", "Hadoop", "Impala", "Cassandra", "Kafka", "HDFS", "HBase", "Hive", "Kubernetes", "Kubeflow", "Airflow", "BigQuery", "MongoDB"]
    cloud = ["AWS", "GCP", "Azure", "Google Cloud", "S3","Redshift","EC2","Lambda", "Route S3","Dynamo"]
    skills = languages + software + big_data + cloud
    # Create a count of each skill based on the number of times each skill appears in all job descriptions
    skill_count = dict.fromkeys(skills, 0)
    for skill in skills:
        for desc in df['Job Description']:
            if skill.lower() in desc.lower():
                skill_count[skill] += 1
            else:
                pass

    return skill_count

def match_skills(df, threshold):
    '''
    Matches job description skills demanded with list of in-demand skills for data scientists. Creates boolean columns for top skills appearing in job descriptions. Threshold set at 1000 apperances of skill.
    '''
    popular_skills = []
    # For any skill with greater than 1000 appearances (appearing in ~20% of job descriptions), append to populat skills
    skill_count = dict(sorted(find_top_skills(df).items(), key=lambda item: item[1], reverse=True))
    for key in skill_count:
        if skill_count[key] > 1000:
            popular_skills.append(key)
        else:
            pass
    # Create boolean columns for popular skills
    for skill in popular_skills:
        df[skill] = df['Job Description'].apply(lambda x: 1 if skill.lower() in x.lower() else 0)
    
    return df

def length_of_desc(df):
    '''
    Returns the length of the job description as a column.
    '''
    df['Description Length'] = df['Job Description'].apply(lambda x: len(x))

    return df

def clean_job_names(df):
    '''
    Engineers name of job to useful feature by extracting labels such as seniority or if a job is data analyst vs data scientist.
    '''
    level = []
    label = []
    nlp = spacy.load('en_core_web_sm')
    # Create batches of different levels of experience labels.
    experienced = ['lead','leader', 'principal', 'senior', 'sr', 'iv', 'iii', 'mid']
    entry = ['entry', 'associate', 'assc', 'i', 'ii', 'junior', 'jr']
    
    # Use spaCy processing to ensure each token of each job name is matched with a batch label.
    for index, name in enumerate(df['Job Name']):
        experienced_count = 0
        entry_count = 0
        other_count = 0
        doc = nlp(name)
        # print('Index: ', index)
        name = re.sub(r'[^\w\s]', ' ', name.lower())
        if 'manager' in name.lower():
            label.append('Manager')
        elif 'director' in name.lower():
            label.append('Director')
        elif 'machine learning' in name.lower() or 'ml' in name.lower():
            label.append('Machine Learning Engineer')
        elif 'data engineer' in name.lower():
            label.append('Data Engineer')
        elif 'data scientist' in name:
            label.append('Data Scientist')
        elif 'analyst' in name.lower():
            label.append('Data Analyst')
        else:
            label.append('Other')
        # tokenize
        for token in doc:
            if token.pos_ not in ['PUNCT']:
                if [ele for ele in experienced if(ele == token.text.lower())]:
                    experienced_count += 1
                elif [ele for ele in entry if (ele == token.text.lower())]:
                    entry_count += 1
                else:
                    other_count += 1
            else:
                pass
        if experienced_count != 0:
            level.append('Experienced')
        elif entry_count != 0:
            level.append('Entry Level')
        else:
            level.append('Other')
    df['Job Level'] = level
    df['Job Label'] = label

    return df

def group_company_names(df):
    '''
    Labels if a company is a FAANG company or not.
    '''
    FAANG = ['Facebook', 'Meta', 'Apple', 'Amazon', 'Netflix', 'Google', 'Alphabet']
    faang_or_not = []
    for name in df['Company Name']:
        if [ele for ele in FAANG if (ele.lower() in name.lower())]:
            faang_or_not.append('FAANG')
        else:
            faang_or_not.append('Not FAANG')
    df['FAANG Or Not'] = faang_or_not
    df.drop(columns=['Company Name'], inplace=True)
    
    return df

def group_company_attributes(df):
    '''
    Thinning the number of unique values for company type, industry, and sector. There are many values between industry and sector that overlap.
    Grouping different industries into more defined sectors, will also not use the original sector values which are ambigious at best. For example, 'Business Services' vs 'Accounting' vs 'Insurance', etc.
    '''
    group_to_industry = {
            'Education': ['Colleges & Universities', 'Education'],

            'Government': ['Aerospace & Defense','Government & Public Administration', 'National Agencies', 'Government'],

            'Retail': ['Consumer Electronics & Appliances Stores', 'Department, Clothing & Shoe Stores', 'General Merchandise & Superstores', 'Grocery Stores', 'Home Furniture & Housewares Stores', 'Other Retail Stores', 'Restaurants & Cafes', 'Government'],

            'Service': ['Advertising & Public Relations', 'Business Consulting', 'Financial Services', 'Grantmaking & Charitable Foundations', 'HR Consulting', 'Hotels & Resorts', 'Human Resources & Staffing', 'Management & Consulting', 'Membership Organizations', 'Nonprofit & NGO', 'Security & Protective', 'Staffing & Subcontracting', 'Service'],

            'Health': ['Beauty & Wellness', 'Biotech & Pharmaceuticals', 'Health Care Services & Hospitals', 'Healthcare', 'Pharmaceutical & Biotechnology', 'Health'],

            'Manufacturing': ['Consumer Product Manufacturing', 'Electronics Manufacturing', 'Food & Beverage Manufacturing', 'Health Care Products Manufacturing', 'Machinery Manufacturing', 'Manufacturing', 'Transportation Equipment Manufacturing', 'Manufacturing'],

            'Finance': ['Accounting & Tax', 'Banking & Lending', 'Financial Transaction Processing', 'Insurance Agencies & Brokerages', 'Insurance Carriers', 'Investment & Asset Management', 'Finance'],

            'Communications': ['Broadcast Media','Cable, Internet & Telephone Providers', 'Telecommunications Services', 'Communications'],

            'Entertainment': ['Arts, Entertainment & Recreation', 'Film Production', 'Gambling', 'Sports & Recreation', 'Video Game Publishing', 'Entertainment'],

            'Technology': ['Computer Hardware Development', 'Enterprise Software & Network Solutions', 'Information Technology', 'Information Technology Support Services', 'Internet & Web Services', 'Research & Development', 'Technology'],

            'Construction / Real Estate': ['Architectural & Engineering Services',  'Building & Personnel Services', 'Real Estate', 'Construction / Real Estate'],
                            
            'Energy & Transportation': ['Airlines, Airports & Air Transportation', 'Automotive Parts & Accessories Stores','Energy & Utilities', 'Shipping & Trucking', 'Taxi & Car Services', 'Energy & Transportation'],
            
            'Unknown / Non-Applicable': ['Unknown / Non-Applicable']
        }
    # Reverse dictionary keys and values
    industry_to_group = {value: key for key in group_to_industry for value in group_to_industry[key]}
    df['Grouped Company Industry'] = df['Company Industry'].map(industry_to_group)
    df.loc[(df['Grouped Company Industry']=='Construction / Real Estate') | (df['Grouped Company Industry']=='Communications') | (df['Grouped Company Industry']=='Education') | (df['Grouped Company Industry']=='Entertainment'), 'Company Industry'] = 'Other'

    df.loc[(df['Company Type'] != 'Company - Public') & (df['Company Type'] != 'Company - Private'), 'Company Type'] = 'Other'
    df.drop(columns=['Company Sector'], inplace=True)  # Sector and Industry are largely redundant

    return df


def clean_data(df):
    '''
    Calls all functions for data cleaning in a single wrapper function.
    '''
    df = handle_incorrect_categories(df)
    df = handle_missing(df)
    df = convert_salary(df)
    df = group_locations(df)
    df = convert_year_founded(df, 2022)
    df = higher_education(df)
    df = match_skills(df, 1000)
    df = length_of_desc(df)
    df = clean_job_names(df)
    df = group_company_names(df)
    df = group_company_attributes(df)
    
    return df