import bs4
import json
import requests
import logging
from collections import defaultdict
from typing import List

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)

jobstreet_main_link = 'http://www.jobstreet.com.sg'
jobstreet_search_link = 'http://www.jobstreet.com.sg/en/job-search/'
search_terms = ['data-scientist-jobs','data-engineer-jobs', 'data-analyst-jobs', 'machine-learning-jobs']


def return_com_overview(results)->dict:
    """returns a dictionary filled with company overview information

    Args:
        results (bs4.element.ResultSet): The results from bs4

    Returns:
        dict: Key: Company overview, value: text
    """
    com_overview_dict = {}
    for section in results:
        if str(section.text)[:16].lower() == 'company overview':
            com_overview_dict['Company Overview'] = str(section.text)[16:]
    return com_overview_dict


def return_job_details(results)->dict:
    """Returns the job details in a dictionary with the headers in bold 
    and the list underneath them as values. Does not capture if they are
    not in list!

    Args:
        results (bs4.element.ResultSet): From soup.select

    Returns:
        dict: a Default dictionary with headers as key and the list as values
    """
    temp_dict = defaultdict(list)
    # its false by default coz in the first run I am always expecting a header first before lists will appear
    new_header = False
    temp_string = ""
    for idx, content in enumerate(results[0].find_all(['li','strong'])):
        if content.name == "strong":
            # print(f"Header : {content.text}")
            if new_header == True:
                last_key = list(temp_dict.keys())[-1]
                temp_dict[last_key] = temp_string
                temp_string = ""
                new_header = False
            temp_dict[content.text] = []
            new_header = True
            continue
        if (content.name == 'li'):
            # print(f"List content: {content.text}")
            temp_string +=content.string + "."
        if idx == len(results[0].find_all(['li','strong']))-1:
            last_key = list(temp_dict.keys())[-1]
            temp_dict[last_key] = temp_string

    return temp_dict

def return_company_name(results)->str:
    company_name = results[0].string
    return company_name

def return_small_section_text(results)->List:
    small_section_text = [data.string for data in results]
    return small_section_text

def return_add_info(results)->dict:
    temp_dict = defaultdict(list)
    for item in results:
        key = item.findAll('span')[0].text
        value = item.findAll('span')[1].text
        temp_dict[key] = value
    return temp_dict

def log_info(position,company_name,small_section,jd, add_info, com_overview):
    logger.info(position)
    logger.info(company_name)
    logger.info(small_section)
    logger.info(jd)
    logger.info(add_info)
    logger.info(com_overview)

def main():
    idx = 1
    link = jobstreet_search_link + search_terms[0]
    results = requests.get(link)
    if results.status_code == 200:
        logger.info('Job street link is Good to go!')
    else:
        logger.error(f'Unable to proceed with {link}')

    soup = bs4.BeautifulSoup(results.text, 'html.parser')
    # This headers will contain all of the clickable links at the side bar
    headers = soup.select('h1 a')
    position = headers[idx].string
    job_link=headers[idx].get('href')
    job_link = jobstreet_main_link+job_link
    results_job_link = requests.get(job_link)
    if results_job_link.status_code==200:
        logger.info('Job street job link is Good to go!')
        soup = bs4.BeautifulSoup(results_job_link.text,'html.parser')
        small_section = soup.find_all('div', {"class": "sx2jih0 zcydq86a"})
        company_name = soup.find_all('span', {"class": "sx2jih0 zcydq84u _18qlyvc0 _18qlyvc1x _18qlyvc2 _1d0g9qk4 _18qlyvcb"})
        jd = soup.select('[data-automation="jobDescription"]')
        add_info = soup.find_all('div', {"class": "sx2jih0 zcydq8r _1tqfum90 _1tqfum97"})
        com_overview = soup.findAll('div', {'class': "sx2jih0 zcydq86q zcydq86v zcydq86w"})

        small_section = return_small_section_text(small_section)
        company_name = return_company_name(company_name)
        jd = return_job_details(jd)
        add_info = return_add_info(add_info)
        com_overview = return_com_overview(com_overview)
        log_info(position,company_name,small_section,jd, add_info, com_overview)

if __name__ == "__main__":
    main()