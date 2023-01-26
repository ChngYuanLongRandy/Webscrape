from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from typing import List
import logging 

class Scraper:
    """Scrapper class to return scrape details with one search term.
    """

    def __init__(self, search_term:str):
        self.search_term = search_term
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.url = "https://www.mycareersfuture.gov.sg/" + \
            f"search?search={self.search_term}&sortBy=relevancy&page=0"
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)


    def __repr__(self) -> str:
        return str(f"Chrome Driver with search term: {self.search_term}")


    def _update_url_next_link(self):
        """updates the url to go to the next page
        """
        self.url = self.url[:-1]+str(int(self.url[-1])+1)


    def _get_jobpost_details(self, link:str)->dict:
        """takes a jobpost link and returns all of the job 
        details in a posting in a dictionary

        Args:
            link (str): link of the job posting
        """
        self.driver.get(self.url)
        company = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@data-cy='company-hire-info__company']")
        position = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//h1[@id='job_title']")
        address = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='address']")
        employment_type = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='employment_type']")
        seniority = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='seniority']")
        min_experience = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='min_experience']")
        job_category = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='job-categories']")
        salary = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//span[@data-cy='salary-range']")
        num_applications = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//span[@id='num_of_applications']")
        last_posted_date = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//span[@id='last_posted_date']")
        expiry_date = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//span[@id='expiry_date']")
        JD = self.driver.find_element(by=By.XPATH, value="//div[@id='description-content']")
        url = link

        res = {
            'company':company.text,
            'position': position.text,
            'address': address.text,
            'employment_type' : employment_type.text,
            'seniority' : seniority.text,
            'min_experience' : min_experience.text,
            'job_category' : job_category.text,
            'salary' : salary.text,
            'num_applications' : num_applications.text,
            'last_posted_date': last_posted_date.text,
            'expiry_date' : expiry_date.text,
            'JD' : JD.text,
            'url' : url
        }

        return res


    def _get_links(self)->List:
        """takes a link from the main page and returns all of the job links
        found within and returns as a list

        Args:
            link (str): url of the page
        """
        self.driver.get(self.url)
        retrieved_links = self.driver.find_elements(by=By.TAG_NAME, value="a")

        links = []

        for link in retrieved_links:
            if link.get_attribute('href'):
                if 'job' in link.get_attribute('href'):
                    links.append(link.get_attribute('href'))

        return links
    
    def _get_jobposts_details(self)->List[dict]:
        """ takes a result page and returns all of the details on the job posts
        back as a list of dict
        """

        data = []

        links = self._get_links()

        for link in links:
            data.append(self._get_jobpost_details(link))
        
        return data

    def _check_if_invalid_page(self)->bool:
        """checks if the page is invalid (does not contain any more job postings)
        as it reaches the end of the result by returning a boolean
        True if no links, False if still has some links to scrape
        """

        links = self._get_links()
        self.logger.info(f"Links are {links}")
        if len(links) == 0:
            return True
        else: return False

    def scrape(self)->List[dict]:
        """scrapes the page using the search term till it reaches the end of the 
        results
        """

        data = []

        while self._check_if_invalid_page == False:
            data += self._get_jobposts_details()
            self._update_url_next_link()
        
        return data

    def _test_scrape(self)->List[dict]:
        """test the scraper by scraping only 2 pages 
        """

        self.driver.implicitly_wait(2)
        page_num = 0
        data = self._get_jobposts_details()


        # while self._check_if_invalid_page == False and page_num < 3:
        #     data += self._get_jobposts_details()
        #     self._update_url_next_link()
        #     page_num +=1
        
        return data