import bs4
import json
import requests
import logging
from collections import defaultdict
from typing import List
import os
from pprint import pformat
import time
import datetime
import hydra
import random

def return_timestamp():
    """generates timestamp in YYYYMMDDhhmmss format"""
    dt_time = datetime.datetime.today()
    return str(10000000000*dt_time.year + 100000000*dt_time.month + 1000000*dt_time.day + 10000*dt_time.hour + 100*dt_time.minute + dt_time.second)

timestamp = return_timestamp()

logging.basicConfig(
    filename='logfile'+ timestamp,
    filemode='a',
    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

def log_decorator(log_name):
    def log_this(function):
        logger = logging.getLogger(log_name)
        def new_function(*args,**kwargs):
            logger.info(f"{function.__name__} - {args} - {kwargs}")
            output = function(*args,**kwargs)
            logger.info(f"{function.__name__} returned: {pformat(output)}")
            return output
        return new_function
    return log_this

def write_into_jsonl(path:str, job_listings:List[dict]):
    """Writes the output into json file

    Args:
        path (str): output path
        job_listings (List[dict]): all of the job info
        overwrite (bool, optional): whether to overwrite in the output path. Defaults to False.
    """
    with open(path, 'w') as writer:
        for job_listing in job_listings:
            writer.write(json.dumps(job_listing) + '\n')

@log_decorator(logger.name)
def return_company_overview(results)->dict:
    """returns a dictionary filled with company overview information

    Args:
        results (bs4.element.ResultSet): The results from bs4

    Returns:
        dict: Key: Company overview, value: text
    """
    company_overview_dict = {}
    for section in results:
        if str(section.text)[:16].lower() == 'company overview':
            company_overview_dict['Company Overview'] = str(section.text)[16:]
    return company_overview_dict

@log_decorator(logger.name)
def return_job_details(results)->dict:
    """Returns the job details in a dictionary with the headers in bold 
    and the list underneath them as values. If the information does not
    conform to the format then the whole chunk is taken

    Args:
        results (bs4.element.ResultSet): From soup.select

    Returns:
        dict: a Default dictionary with headers as key and the list as values
    """
    temp_dict = defaultdict(list)
    # its false by default coz in the first run I am always expecting a header first before lists will appear
    new_header = False
    temp_string = ""
    # finds bold and list. If not found then extracts everything
    if results[0].find_all('strong') and results[0].find_all('li'):
        for idx, content in enumerate(results[0].find_all(['li','strong'])):
            if content.name == "strong":
                if new_header == True:
                    last_key = list(temp_dict.keys())[-1]
                    temp_dict[last_key] = temp_string
                    temp_string = ""
                    new_header = False
                temp_dict[content.text] = []
                new_header = True
                continue
            if (content.name == 'li'):
                if content.string is None:
                    temp_string = ""
                else:
                    temp_string += content.string + "."
            if idx == len(results[0].find_all(['li','strong']))-1:
                last_key = list(temp_dict.keys())[-1]
                temp_dict[last_key] = temp_string
    elif results[0].find_all(['li']):
        list_jd = results[0].find_all(['li'])
        temp_dict = {'no_header_JD' : [item.string +'.' for item in list_jd]}

    else:
        temp_dict = {'unorganised_jd' : results[0].text}

    return temp_dict

@log_decorator(logger.name)
def return_company_name(results)->str:
    """Returns the company name

    Args:
        results (_type_): _description_

    Returns:
        str: _description_
    """
    company_name = results[0].string
    return company_name

@log_decorator(logger.name)
def return_small_section_text(results)->List:
    """The small section is the upper left corner that contains details like
    position, company name, address and date of posting

    Args:
        results (_type_): _description_

    Returns:
        List: _description_
    """
    small_section_text = [data.string for data in results]
    return small_section_text

@log_decorator(logger.name)
def return_add_info(results)->dict:
    """The additional information captured includes the 'additional information' under
    the main JD and the 'additional company information' after company overview.
    Returns everything in a dictionary with its content as value and header
    as key 
    """
    temp_dict = defaultdict(list)
    for item in results:
        key = item.find_all('span')[0].text
        value = item.find_all('span')[1].text
        temp_dict[key] = value
    return temp_dict

@log_decorator(logger.name)
def return_all_info(results_job_link:str,params:dict)->dict:
    """Main method that does all of the job and calls subordinate methods
    for each section and returns all of the information contained

    Args:
        results_job_link (str): URL of one job 

    Returns:
        dict: results
    """
    soup = bs4.BeautifulSoup(results_job_link.text,'html.parser')
    small_section = soup.find_all('div', {"class": params['small_section']})
    company_name = soup.find_all('span', {"class": params['company_name']})
    jd = soup.select('[data-automation="jobDescription"]')
    add_info = soup.find_all('div', {"class": params['add_info']})
    company_overview = soup.find_all('div', {'class': params['company_overview']})

    small_section = return_small_section_text(small_section)
    company_name = return_company_name(company_name)
    jd = return_job_details(jd)
    add_info = return_add_info(add_info)
    company_overview = return_company_overview(company_overview)

    return small_section, company_name, jd, add_info, company_overview



@log_decorator(logger.name)
def extract_from_one_job_listing(job_link:str, position:str, params:dict)->dict:
    """Returns all of the details from one job listing

    Args:
        job_link (str): url link for the job post
        position (str): position

    Returns:
        dict: If no error returns position, company name, small section, url 
        otherwise will return error message with position and URL
    """
    jobstreet_main_link = params['jobstreet_main_link']
    job_link = jobstreet_main_link+job_link
    results_job_link = requests.get(job_link)

    if results_job_link.status_code==200:
        logger.info('Job street job link is Good to go!')

        try:
            small_section, company_name, jd, add_info, company_overview = return_all_info(results_job_link,params)
            return {"position":position},{"company_name":company_name},{"small_section":small_section},jd, add_info, company_overview, {"url":job_link}

        except Exception as e:
            logger.error(f"Unable to extract info due to {e}")
            return {'Error': {'job_link': job_link, 'Message':str(e), 'position':position}}
    else:
        logger.error(f"Unable to extract job listing info from {job_link} for position {position}")
        return {'Error': {'job_link': job_link, 'Message':"status_code", 'position':position}}

def extract_from_page(link:str, params:dict)->List:
    """Extracts all of the details in one page

    Args:
        link (str): link

    Returns:
        List: _description_
    """
    job_listings = []
    results = requests.get(link)
    if results.status_code == 200:
        logger.info('Job street link is Good to go!')
    else:
        logger.error(f'Unable to proceed with {link}')

    soup = bs4.BeautifulSoup(results.text, 'html.parser')
    # This headers will contain all of the clickable links at the side bar
    headers = soup.select('h1 a')

    for idx in range(1, len(headers)):
#    for idx in range(1, 10):
        time.sleep(random.randint(0, 3))
        position = headers[idx].string
        job_link=headers[idx].get('href')
        job_listings.append(extract_from_one_job_listing(job_link, position, params))
        
    return job_listings

@hydra.main(config_path='./conf', config_name='hydra_config.yaml')
def main(args):
    """main function that takes in hydra configs and generates 
    output
    """

    #############################################
    #####  initialisation of variables      #####
    #############################################

    job_listings = []
    jobstreet_main_link = args['settings']['jobstreet_main_link']
    jobstreet_search_link = args['settings']['jobstreet_search_link']
    page_num = args['settings']['pages']
    # the link needs the additional term of jobs in order for the url to be valid
    search_term = args['settings']['search_term'] + '-jobs'
    link = jobstreet_search_link + search_term

    small_section_param = args['html_tag']['small_section']
    company_name_param = args['html_tag']['company_name']
    add_info_param = args['html_tag']['add_info']
    company_overview_param = args['html_tag']['company_overview']

    params = {
        'small_section':small_section_param,
        'company_name':company_name_param, 
        'add_info':add_info_param, 
        'company_overview':company_overview_param,
        'jobstreet_main_link':jobstreet_main_link,
        'jobstreet_search_link':jobstreet_search_link
        }


    #############################################
    #####  searches page by page and extract#####
    #############################################


    for pg_num in range(1,page_num+1):
        time.sleep(random.randint(0, 3))
        # Should return something like this format https://www.jobstreet.com.sg/en/job-search/data-scientist-jobs/480/
        # jobstreet search link + search term + page num
        link = jobstreet_search_link+ search_term+"/"+ str(pg_num)+"/"

        temp_listing = extract_from_page(link,params)
        for listing in temp_listing:
            job_listings.append(listing)


    #############################################
    #####           Writes file             #####
    #############################################

    curr_dir = os.getcwd()
    sample_path = curr_dir+'/'+ search_term + timestamp +'.jsonl'
    write_into_jsonl(sample_path, job_listings)
    logger.info('Job completed!')


if __name__ == "__main__":
    main()