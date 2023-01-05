# ReadMe
 
This consolidates my efforts in scraping websites.
It should contain scrappers for 
- Jobstreet
- Newegg

Work in progress or planned
- NTUC
- redmart
- Giant
- Sheng siong

## To use

1. Clone this repo

2. Use conda to install env:

```
conda env create -f conda.yml
```

3. Activate conda env
```
conda activate scrapper-env
```

4. Choose scrapper and run (for exact instructions refer to each header)
```
python/<name of scrapper>/scrape.py settings.pages <num of pages> settings.search_term <what you want to search, please add a hypen in between words>
```
Example
```
python/JobStreet/scrape.py pages 5 search_term Data-Engineer
```

5. Outputs JSONL file and a log file in the output folder

## Jobstreet

Jobstreet Data: 
- See what affects salary
- Come up with topic modelling
- Generate a sample Job Description