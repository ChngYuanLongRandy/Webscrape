from scraper import Scraper
import hydra
import json

@hydra.main(config_path='./conf', config_name='config.yaml')
def main(args):

    search_term = args['settings']['search-term']
    
    scraper = Scraper(search_term, headless=False)
    data = scraper.scrape()

    with open(f'{search_term.replace(" ", "_")}_data.csv','w') as f:
        for row in data:
            f.write(json.dumps(row)+'\n')

if __name__ == "__main__" :
    main()