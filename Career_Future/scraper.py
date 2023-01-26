from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from typing import List
import logging 

class Scraper:
    """Scrapper class to return scrape details with one search term.
    """

    def __init__(self, search_term:str, headless:bool= True):
        self.search_term = search_term
        if headless:
            self.options = Options()
            self.options.headless = True
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
        else: 
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
        self.logger.info("Link updated to next page")
        self.url = self.url[:-1]+str(int(self.url[-1])+1)


    def _get_jobpost_details(self, link:str)->dict:
        """takes a jobpost link and returns all of the job 
        details in a posting in a dictionary

        Args:
            link (str): link of the job posting
        """
        self.driver.get(link)

        company = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@data-cy='company-hire-info__company']").text
        position = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//h1[@id='job_title']").text
        address = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='address']").text
        employment_type = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='employment_type']").text
        seniority = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='seniority']").text
        
        # Min experience may not be available
        try:
            min_experience = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='min_experience']").text
        except:
            min_experience = 'NA'
        job_category = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//p[@id='job-categories']").text
        salary = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//span[@data-cy='salary-range']").text
        num_applications = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//span[@id='num_of_applications']").text
        last_posted_date = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//span[@id='last_posted_date']").text
        expiry_date = self.driver.find_element(by=By.XPATH, value="//div[@data-cy='JobDetails__job-info']//span[@id='expiry_date']").text
        JD = self.driver.find_element(by=By.XPATH, value="//div[@id='description-content']").text
        url = link

        res = {
            'company':company,
            'position': position,
            'address': address,
            'employment_type' : employment_type,
            'seniority' : seniority,
            'min_experience' : min_experience,
            'job_category' : job_category,
            'salary' : salary,
            'num_applications' : num_applications,
            'last_posted_date': last_posted_date,
            'expiry_date' : expiry_date,
            'JD' : JD,
            'url' : url
        }

        return res


    def _get_links(self):
        """takes a link from the main page and returns all of the job links
        found within and saves as property
        """
        self.logger.info("Entered Get Links")
        self.driver.get(self.url)

        retrieved_links = self.driver.find_elements(by=By.TAG_NAME, value="a")
        self.logger.info(f"All links are {retrieved_links}")
        links = []

        for link in retrieved_links:
            if link.get_attribute('href'):
                if 'job' in link.get_attribute('href'):
                    links.append(link.get_attribute('href'))

        self.logger.info(f"Valid Links are {links}")
        self.curr_links = links
    
    def _get_jobposts_details(self)->List[dict]:
        """ takes a result page and returns all of the details on the job posts
        back as a list of dict
        """

        data = []

        for link in self.curr_links:
            self.logger.info(f"Entering Link : {link}")
            data.append(self._get_jobpost_details(link))
        
        return data

    def _check_if_invalid_page(self)->bool:
        """checks if the page is invalid (does not contain any more job postings)
        as it reaches the end of the result by returning a boolean
        True if no links, False if still has some links to scrape
        """

        if len(self.curr_links) == 0:
            return True
        else: return False

    def scrape(self)->List[dict]:
        """scrapes the page using the search term till it reaches the end of the 
        results
        """

        self.driver.implicitly_wait(10)
        data = []
        self._get_links()

        while self._check_if_invalid_page() == False:
            self.logger.info(f"Entering Loop")
            data += self._get_jobposts_details()
            self._update_url_next_link()
            self._get_links()

        self.logger.info(f"Scrape done! Data: {data}")
        return data

    def _test_scrape(self)->List[dict]:
        """test the scraper by scraping only 2 pages 
        """
        self.driver.implicitly_wait(10)
        page_num = 0
        data = []
        self._get_links()

        while self._check_if_invalid_page() == False and page_num < 2:
            self.logger.info(f"Entering Loop")
            data += self._get_jobposts_details()
            self._update_url_next_link()
            self._get_links()
            page_num +=1

        self.logger.info(f"Scrape done! Data: {data}")
        return data