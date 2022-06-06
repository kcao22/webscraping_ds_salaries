# Project Overview: Predicting Data Scientist Salaries

 - Built Python regression tool that predicts data scientist salaries with Mean Absolute Error (MAE) of ~ $14k. This tool was built to help prospective data scientists get estimates of data science salaries for job postings where salaries are not listed, particularly for websites like LinkedIn where salary estimates are often not shown.
 - Used Selenium to build web scraping tool to scrape ~ 5,000 jobs from Glassdoor.com and transformed data into a dataset using Python.
 - Transformed dataset and engineered different features including using spaCy to process job titles and Python to collect popular Data Science skillsets from job descriptions.
 - Optimized Random Forest Regression model using validation curves, GridSearchCV, and recursive feature elimination to acheive lowest possible MAE.
 - Built interactive Gradio web page for user to input data science job post information that returns a predicted salary for the job position.

![Alt Text](https://github.com/kcao22/webscraping_ds_salaries/blob/main/images/gradio_sample.gif)

## Libraries and Resources Used

 - **Python Version**: 3.9
 - **Main Packages**: Gradio, Matplotlib, Pandas, scikit-learn, seaborn, Selenium, spaCy
 - **Environment Requirements**: conda env create -f environment.yml
 - **Data Cleaning Ideas**: https://github.com/PlayingNumbers/ds_salary_proj

 ## Web Scraping

Using Selenium, I built a web scraping tool for Glassdoor, a job searching service. Each job posting scraped from Glassdoor was found with a "data scientist" keyword search and was done irrespective of location and minimum or maximum salaries. 5,000 jobs were scraped from the following link: https://www.glassdoor.com/Job/data-scientist-jobs-SRCH_KO0,14.htm. From each job post, the following data points were immediately available upon clicking the "Show More" drop down and thus were collected:

 - Company Name
 - Job Name
 - Job Location
 - Job Description
 - Job Salary
 - Company Rating
 - Company Size
 - Company Type
 - Company Sector
 - Year Founded
 - Company Industry
 - Company Revenue

 Glassdoor job postings are often redundant after a few pages, with the same job postings appearing again and again. After scraping, rows of data that are identical are removed from the overall dataset. Below is an example of the webscraping tool progressing through different job posts that appear on Glassdoor. 

![Alt Text](https://github.com/kcao22/webscraping_ds_salaries/blob/main/images/web_scraper.gif)

 ## Data Cleaning and Feature Engineering

 Once the dataset was compiled from web scraping, the data needed to be cleaned. The following list describes the data cleaning and feature engineering that was done during this project:

  - Data cleaning including moving incorrect data points to correct data columns, filling null values, remapping categorical values that differed because of capitalization, and dropping null salary data
  - Parsed numerical salary data from salary text
  - Parsed job location state from location data and mapped locations to USA major regions to reduce number of features for encoding later
  - Converted company founding year to age of company
  - Extracted higher education requirements and job skill requirements from job description text
    - The engineered boolean skill columns such as "Python" and "SQL" were added based on rate of appearance in job description data. In this case, the top skills appearing in at least 1000 job descriptions (20% of all data) were included as boolean columns
  - Created description length column
  - Processed job titles using spaCy natural language processing for token matching with different labels and levels to create job level and explicit job label columns
  - Grouped company industries into more encompassing markets and dropped redundant company sector column

## Exploratory Data Analysis

 After data cleaning and feature engineering, average salaries for various categorical features are plotted for understanding of data for future machine learning steps. The intial data contained many outliers, which were removed for machine learning in the next step. 
 
 Below are a few interesting visuals.

![alt text](https://github.com/kcao22/webscraping_ds_salaries/blob/main/images/heatmap_corr_num_vals.png "Correlation Heatmap")
![alt text](https://github.com/kcao22/webscraping_ds_salaries/blob/main/images/grouped_company_industry_salaries.png "Salaries by Industry")
![alt text](https://github.com/kcao22/webscraping_ds_salaries/blob/main/images/job_titles.png "Salaries by Job Label")
![alt text](https://github.com/kcao22/webscraping_ds_salaries/blob/main/images/label_level_sals.png "Job Label and Level Salaries")



## Machine Learning Modeling

As the data contains many rows of data that were filled with suitable values, the data is quite sparse. I chose to run with a Random Forest Regressor model because of this. Train test splits were performed to split the data into 75% training data and 25% test data. Model performance is evaluated based on Mean Absolute Error for easier interpretation when evaluating salary estimates. Outliers from the data are removed using the Interquartile Range Method (IQR) to ensure MAE will not be heavily skewed by outlier data. See the below image for initial outliers from all scraped data.

![alt text](https://github.com/kcao22/webscraping_ds_salaries/blob/main/images/average_salary_outliers.png "Outliers")


The training data is then used to fit a OneHotEncoder before the encoder transforms the test set data. OneHotEncoder is employed here to ensure that dummy variable columns match between train and test datasets.

Validation curves are plotted a range of values for the following Random Forest Regressor parameters:

  - n_estimators
  - max_depth
  - min_samples_split
  - min_samples_leaf
  - max_features

This provides insight on ballpark ranges for optimizing each parameter and ensuring no overfitting occurs. Below is an example of overfitting for a parameter.

![alt text](https://github.com/kcao22/webscraping_ds_salaries/blob/main/images/max_depth%20overfitting.png "Outliers")

Recursive feature elimination for random forest is then used to reduce the number of features resulting from OneHotEncoding.

My best performing Random Forest model produced a MAE score of 14.58.

## Interactive Web Page Estimation Tool

As a final step, an interactive web page was produced using Gradio where a user can input job posting information. The web page then returns a predicted salary for the job posting. To see this in action, view the .gif at the top of README. If you would like to use the web interface yourself, please run gradio_gui.py in Python terminal to host the page locally.

