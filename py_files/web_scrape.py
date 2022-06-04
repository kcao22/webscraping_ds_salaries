# Author: Kevin Cao

# Imports
import os
import time
import pandas as pd

from selenium import webdriver  # Used for opening up a web browser
from selenium.common.exceptions import NoSuchElementException  # Used for when element not found

def exit_prompt(driver):
    '''
    Tries to click out of sign in prompt from glassdoor or the estimated salarty prompt.
    Sign in prompt does not trigger when page loads, only after a job posting is clicked (does not appear again after clicking X).
    Glassdoor estimated salary pop up also appears occasionally when progressing through job postings.
    '''
    try:  # Try clicking out of sign in prompt
        exit = driver.find_element_by_class_name('modal_closeIcon')
        exit.click()
    except NoSuchElementException:
        pass

def get_next_page(driver, page_num):
    '''
    Concatenates string argument for clicking on next page and clicks on next page element
    '''
    page_element = '//div[@class="pageContainer"]/button[@data-test="pagination-link-'
    page_element += str(page_num) + '\"' + ']'
    try:  # Try clicking on next page
        driver.find_element_by_xpath(page_element).click()
    except NoSuchElementException:
        print('No Page Element Found')
    time.sleep(3)  # Wait for page to load

def get_data(rows, test=False):
    '''
    Grabs rows of data including:
        - Job name, company name, and job location
        - Job salary and company rating
        - Company information
    '''
    url = 'https://www.glassdoor.com/Job/data-scientist-jobs-SRCH_KO0,14.htm'
    driver = webdriver.Edge()  # Using Edge browser
    driver.get(url)
    all_jobs = []
    # job_count = 1
    job_element_count = 0
    page_num_element = 1
    # job_posts = driver.find_elements_by_class_name('react-job-listing')

    while len(all_jobs) <= rows:  # If less than specified rows.
        company_name = ''
        job_name = ''
        location = ''
        job_desc = ''
        salary = ''
        rating = ''
        company_size = ''
        company_type = ''
        company_sector = ''
        year_founded = ''
        company_industry = ''
        company_revenue = ''
        job_posts = driver.find_elements_by_class_name('react-job-listing')  # To prevent element refresh, page document missing
        exit_prompt(driver)  # Start of new page pop up...
        job_posts[job_element_count].click()
        time.sleep(2)  # Wait to prevent bot detection 
        exit_prompt(driver)  # If estimated salary prompt -> problem right now is if you exit the prompt, you re-read the same job. This is because the prompt pops up, but you don't move onto the next job yet...

        try:  # Attempt at acquiring information
            # Basic Job Information
            company_name = driver.find_element_by_class_name('css-xuk5ye').text.split('\n')[0]
            job_name = driver.find_element_by_class_name('css-1j389vi').text
            location = driver.find_element_by_class_name('css-56kyx5').text
            driver.find_element_by_class_name('css-t3xrds').click()
            job_desc = driver.find_element_by_class_name('jobDescriptionContent').text

            # Salary and Company Rating
            try:  # If salary estimate exists
                salary = driver.find_element_by_class_name('css-1hbqxax').text
            except NoSuchElementException:
                salary = -1
            try:  # If rating exists
                rating = driver.find_element_by_class_name('css-ey2fjr').text
            except:
                rating = -1

            # Company Information
            try: # Separate try except for each company info, or else all will default to -1 if even one piece of information is missing.
                company_size = driver.find_element_by_xpath('//div[@id="EmpBasicInfo"]/div[1]/div/div[1]/span[2]').text
            except NoSuchElementException:
                company_size = -1
            try:
                company_type = driver.find_element_by_xpath('//div[@id="EmpBasicInfo"]/div[1]/div/div[3]/span[2]').text
            except NoSuchElementException:
                company_size = -1
            try:
                company_sector = driver.find_element_by_xpath('//div[@id="EmpBasicInfo"]/div[1]/div/div[5]/span[2]').text
            except NoSuchElementException:
                company_size = -1
            try:
                year_founded = driver.find_element_by_xpath('//div[@id="EmpBasicInfo"]/div[1]/div/div[2]/span[2]').text
            except NoSuchElementException:
                company_size = -1
            try:
                company_industry = driver.find_element_by_xpath('//div[@id="EmpBasicInfo"]/div[1]/div/div[4]/span[2]').text
            except NoSuchElementException:
                company_size = -1
            try:
                company_revenue = driver.find_element_by_xpath('//div[@id="EmpBasicInfo"]/div[1]/div/div[6]/span[2]').text
            except NoSuchElementException:
                company_size = -1
            all_jobs.append([company_name, job_name, location, job_desc, salary, rating, company_size, company_type, company_sector, year_founded,company_industry, company_revenue])
            if test:  # If testing, then print outputs
                print('Company Name: ', company_name)
                print('Job Name: ', job_name)
                print('Location: ', location)
                print('Job Description: ', job_desc[:20])
                print('Salary:', salary)
                print('Rating:' , rating)
                print('Company Size: ', company_size)
                print('Company Type: ', company_type)
                print('Company Sector: ', company_sector)
                print('Year Founded: ', year_founded)
                print('Company Industry: ', company_industry)
                print('Company Revenue: ', company_revenue)
                print('\n')


        except:
            time.sleep(4)
        
        if job_element_count == 29:  # If last job on page, move to next page
            job_element_count = -1
            page_num_element += 1
            print('Page: ', page_num_element)
            # print('Reached last job on the page')
            try:  # In case page fails to load, return data collected.
                get_next_page(driver, page_num_element)
            except:
                return all_jobs 
        else:  # Do not reset counters yet
            pass
        job_element_count += 1
        # job_count += 1

    print("Exit While Loop")
    return all_jobs

def data_to_df_csv(date):
    '''
    Converts scraped data to Pandas DataFrame.
    '''
    data = get_data(850, test=False)
    df = pd.DataFrame(data=data, columns=['Company Name', 'Job Name', 'Job Location', 'Job Description', 'Salary', 'Rating', 'Company Size', 'Company Type', 'Company Sector', 'Year Founded', 'Company Industry', 'Company Revenue'])
    df = df.drop_duplicates()
    file_name = date + '_data.csv'
    df.to_csv(file_name, index=False)

def concat_all_csv():
    '''
    Loads all CSV data files and concatenates all data into a single DataFrame. Then eliminates duplicated job rows and merges into a single file.
    '''
    directory = os.getcwd()
    empty = pd.DataFrame()
    for file in os.listdir(directory):
        if file.endswith('.csv') and file != 'cleaned_data.csv' and file != 'temp_all.csv':
            print(file)
            empty = pd.concat([empty, pd.read_csv(file)], axis=0)
        else:
            pass
    empty = empty.drop_duplicates()
    print('Unique Jobs: ', len(empty))
    return empty