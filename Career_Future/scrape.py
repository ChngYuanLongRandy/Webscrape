from scraper import Scraper
import hydra



@hydra.main(config_path='./conf', config_name='config.yaml')
def main(args):

    search_terms = args['settings']['search-terms']
    scraper = Scraper(search_terms[0])
    scraper._test_scrape()




if __name__ == "__main__" :
    main()