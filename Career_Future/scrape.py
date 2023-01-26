from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import hydra

@hydra.main(config_path='./conf', config_name='config.yaml')
def main(args):
    pass

if __name__ == "__main__" :
    main()