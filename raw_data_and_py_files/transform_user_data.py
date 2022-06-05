# Author: Kevin Cao

# Imports
import regex as re
import spacy

# All functions

def add_null_salary(df):
    '''
    0's for hourly, glassdoor estimated, and employer estimated.
    '''
    df['Hourly'] = 0
    df['Employer Provided'] = 0
    df['Glassdoor Estimated'] = 0

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
    # Group states to four regions and remote/other
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
    # Reverse dictionary key and values
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

def match_skills(df):
    '''
    Matches job description skills demanded with list of in-demand skills for data scientists.
    '''
    # From EDA, most populat skills > 1000 counts
    popular_skills = ['Python', 'SQL', 'Excel', 'AWS', 'Spark', 'Tableau', 'Scala', 'Big Data', 'Data Visualization']
    for skill in popular_skills:
        for desc in df['Job Description']:
            if skill.lower() in desc.lower():
                df[skill] = 1
            else:
                df[skill] = 0
    return df

def length_of_desc(df):
    '''
    Returns the length of the job description as a column.
    '''
    df['Description Length'] = df['Job Description'].apply(lambda x: len(x))

    return df

def clean_job_names(df):
    '''
    Engineers name of job to useful feature by extracting labels.
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
            'Education': ['Colleges & Universities', 'Education', 'K-12 Education', 'Preschool & Child Care', ],

            'Government': ['Aerospace & Defense','Government & Public Administration', 'National Agencies', 'Government', 'Federal Agencies'],

            'Retail': ['Consumer Electronics & Appliances Stores',  'Department, Clothing & Shoe Stores', 'Department, Clothing, & Shoe Stores', 'General Merchandise & Superstores', 'Grocery Stores', 'Home Furniture & Housewares Stores', 'Other Retail Stores', 'Restaurants & Cafes', 'Consumer Product Rental', 'Retail & Wholesale', 'Sporting Goods Stores', 'Wholesale',],

            'Service': ['Advertising & Public Relations',  'Advertising & Marketing', 'Business Consulting', 'Financial Services', 'Grantmaking & Charitable Foundations', 'HR Consulting', 'Hotels & Resorts', 'Human Resources & Staffing', 'Management & Consulting', 'Membership Organizations', 'Nonprofit & NGO', 'Security & Protective', 'Staffing & Outsourcing', 'Staffing & Subcontracting', 'Service', 'Consulting',  'Education Training Services', 'Farm Support Services', 'IT Services','Metals Brokers', 'Religious Organizations', 'Security Services', 'Social Assistance', 'Taxi & Car Services', 'Transportation Management',],

            'Health': [ 'Beauty & Personal Accessories Stores', 'Beauty & Wellness', 'Biotech & Pharmaceuticals', 'Health Care Services & Hospitals', 'Healthcare', 'Pharmaceutical & Biotechnology', 'Health', 'Health, Beauty, & Fitness'],

            'Manufacturing': ['Consumer Product Manufacturing', 'Consumer Products Manufacturing', 'Electronics Manufacturing', 'Food & Beverage Manufacturing', 'Health Care Products Manufacturing', 'Machinery Manufacturing', 'Manufacturing', 'Transportation Equipment Manufacturing', 'Manufacturing',  'Chemical Manufacturing', 'Industrial Manufacturing', 'Logistics & Supply Chain', 'Manufacturing',  'Mining', 'Telecommunications Manufacturing',],

            'Finance': ['Accounting', 'Accounting & Tax',  'Banks & Credit Unions', 'Banking & Lending', 'Lending','Financial Transaction Processing', 'Insurance Agencies & Brokerages', 'Insurance Carriers', 'Investment & Asset Management', 'Finance', 'Brokerage Services', 'Financial Analytics & Research', 'Investment Banking & Asset Management', 'Stock Exchanges', ],

            'Communications': ['Broadcast Media','Cable, Internet & Telephone Providers', 'Telecommunications Services', 'Communications', 'Media & Communication', 'TV Broadcast & Cable Networks', ],

            'Entertainment': ['Arts, Entertainment & Recreation', 'Film Production', 'Gambling', 'Sports & Recreation', 'Video Game Publishing', 'Entertainment', 'Auctions & Galleries', 'Motion Picture Production & Distribution', 'Publishing', 'Video Games',],

            'Technology': [ 'Computer Hardware & Software', 'Computer Hardware Development', 'Enterprise Software & Network Solutions', 'Information Technology', 'Information Technology Support Services', 'Internet & Web Services', 'Research & Development', 'Technology',  'Internet',],

            'Construction / Real Estate': ['Architectural & Engineering Services',  'Building & Personnel Services', 'Real Estate', 'Construction / Real Estate', 'Construction',],
                            
            'Energy & Transportation': ['Airlines, Airports & Air Transportation', 'Automotive Parts & Accessories Stores','Energy & Utilities', 'Shipping & Trucking', 'Energy & Transportation',  'Energy', 'Gas Stations', 'Travel Agencies', 'Trucking','Utilities',],
            
            'Unknown / Non-Applicable': ['Unknown / Non-Applicable']
        }
    # Reverse dictionary key and values
    industry_to_group = {value: key for key in group_to_industry for value in group_to_industry[key]}
    df['Grouped Company Industry'] = df['Company Industry'].map(industry_to_group)
    # Grouping some of the grouped industries, poor representation in data.
    df.loc[(df['Grouped Company Industry']=='Construction / Real Estate') | (df['Grouped Company Industry']=='Communications') | (df['Grouped Company Industry']=='Education') | (df['Grouped Company Industry']=='Entertainment'), 'Company Industry'] = 'Other'
    # Grouping type of company together. From EDA, public and private dominate, all others are poorly represented
    df.loc[(df['Company Type'] != 'Company - Public') & (df['Company Type'] != 'Company - Private'), 'Company Type'] = 'Other'
    df.drop(columns=['Company Sector'], inplace=True)  # Sector and Industry are largely redundant

    return df

def clean_data(df):
    '''
    Calls all functions for data cleaning in a single wrapper function.
    '''
    df = add_null_salary(df)
    df = group_locations(df)
    df = convert_year_founded(df, 2022)
    df = higher_education(df)
    df = match_skills(df)
    df = length_of_desc(df)
    df = clean_job_names(df)
    df = group_company_names(df)
    df = group_company_attributes(df)
    
    return df