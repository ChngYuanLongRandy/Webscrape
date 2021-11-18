#! python3
#webscrape.py scrapes a website for information
import pprint
import requests, bs4, csv , re, datetime

#loop through each link and take all information available and store in dictionary

#Intialisation of all of the lists
jobTitles =['Job Title']
datePosted = ['Date posted']
companies = ['Companies']
locations = ['Location']
jobJD =['Job Description']
careerlvl = ['Career Level']
qualification = ['Qualification']
yrExp = ['Years of Experience']
jobType =['Job Type']
pay = ['Pay']
coOverview = ['Company Overview']
otherInfo = ['Other information']
job_URL =['URL']


jobstreet_main_link = 'http://www.jobstreet.com.sg'
search_terms = ('data-scientist-jobs','data-engineer-jobs', 'data-analyst-jobs', 'machine-learning-jobs')

link = 'https://www.jobstreet.com.sg/en/job-search/data-scientist-jobs/'

#while next_url != 'https://www.jobstreet.com.sg/en/job-search/data-scientist-jobs/1/':

for search in search_terms:
    print('Search Now for ' + search + ' jobs')
    link = jobstreet_main_link + '/en/job-search/' + search +'/'
    counter = 0
    after_first_page_bool = False
    while counter <20:

        res = requests.get(link)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        result = soup.select('h1 a')
        # check number of links retrieved in a page
        print('Counter value is ' + str(counter))
        print("Acessing link " + link)
        print("Number of links available in the webpage is " + str(len(result)))

        for i in range(0,len(result)):
            #Job Title
            print("Job Title for result number " + str(i) + " is " + str(result[i].getText()))
            try:
                jobTitle = str(result[i].getText())
            except:
                jobTitle = 'Information not available'
            jobTitles.append(jobTitle)
            job_link = str(jobstreet_main_link + str(result[i].get('href')))
            print("Job link " + str(i) + " is " + job_link)
            job_URL.append(job_link)

            #Company
            #clicking into the link from the website in order to get more information like JD, requirements, etc
            job_res = requests.get(job_link)
            try:
                job_res.raise_for_status()
            except Exception as exc:
                print('Problem due to exception ' + str(exc))
            job_data = bs4.BeautifulSoup(job_res.text, 'html.parser')
            job_result_company = job_data.select_one('[data-automation="detailsTitle"]')
            print("Job result for " + str(i) + " is " + str(job_result_company.getText()))
            #since the company name is together with the job name, I will remove the job name
            company = "".join(a for a in list(job_result_company.getText())[len(jobTitle):])
            print("Company for result number " + str(i) + " is " + company)
            companies.append(company)

            job_result_jd = job_data.select_one('[data-automation="jobDescription"]')
            print("Job result for " + str(i) + " is " + str(job_result_jd.getText()))
            jobJD.append(str(job_result_jd))

            job_groupdetails = job_data.select_one('[class ="sx2jih0 h6p8rp0 h6p8rp3"]')
            print("Job Details " + str(job_groupdetails.getText()))
            #pay regex will catch SGD3,000 - SGD5,000 for example
            pay_regex = re.compile(r'SGD\s?\d,\d{3}\s-\sSGD\s?\d,\d{3}')
            job_pay = pay_regex.search(str(job_groupdetails.getText()))
            #sometimes the pay is not there
            try:
                pay.append(str(job_pay.group()))
            except:
                pay.append("")

            #--------------------------------location/pay/date--------------------------------
            location_regex = re.compile(r'(.{0,20})(SGD \d,\d{3}\s-\sSGD \d,\d{3})?(Posted.*)')
            job_ln_pay_date = location_regex.search(str(job_groupdetails.getText()))
            #sometimes the pay is not there so location will not be picked up
            #min information is location and date
            if job_ln_pay_date.group(2) is None:
                try:
                    locations.append(str(job_ln_pay_date.group(1)))
                    datePosted.append(str(job_ln_pay_date.group(3)))
                except:
                    locations.append('')
                    datePosted.append('')
            #all information is available
            else:
                try:
                    locations.append(str(job_ln_pay_date.group(1)))
                    pay.append(str(job_ln_pay_date.group(2)))
                    datePosted.append(str(job_ln_pay_date.group(3)))
                except:
                    locations.append('')
                    pay.append('')
                    datePosted.append('')

            # #--------------------------------posted on date--------------------------------
            # job_datePosted_regex = re.compile(r'(.*)(SGD\s?\d,\d{3}\s-\sSGD\s?\d,\d{3})?(Posted .*)')
            # job_datePosted = job_datePosted_regex.search(str(job_groupdetails.getText()))
            # #sometimes the pay is not there so date will not be picked up
            # try:
            #     datePosted.append(str(job_datePosted.group(2)))
            # except:
            #     datePosted.append(str(job_datePosted.group(1)))

            #--------------------------------Other Information--------------------------------
            job_groupdetails = job_data.select('[class ="sx2jih0 zcydq82q _18qlyvc0 _18qlyvcv _18qlyvc1 _1d0g9qk4 _18qlyvc9"]')
            print(len(job_groupdetails))
            temp =[]
            for i in range(0,len(job_groupdetails)):
                print(job_groupdetails[i].getText())
                temp.append(job_groupdetails[i].getText())
            otherInfo.append(" ".join(x for x in temp))

        # --------------------------------Go to next link--------------------------------
        href_regex = re.compile(r'href="(.*)"\srel')
        job_result_jd = soup.select('[data-automation="pagination"]')
        print('Printing the results of job results links ' + str(job_result_jd))
        if after_first_page_bool == False:
            print(len(job_result_jd))
            print((job_result_jd[0]))
            url = href_regex.search(str(job_result_jd[0]))
            print(url.group(1))
            link = jobstreet_main_link + str(url.group(1))
            print('link to go to next is ' + link)
            after_first_page_bool = True
            counter+=1
        else:
            href_regex = re.compile(r'href=.*href="(.*)"\srel')
            job_result_jd = soup.select('[data-automation="pagination"]')
            url = href_regex.search(str(job_result_jd[0]))
            print(url.group(1))
            link = jobstreet_main_link + str(url.group(1))
            print('link to go to next is ' + link)
            counter += 1


#write everything in an excel sheet

data = zip(*(jobTitles,
            companies,
            pay,
            locations,
            datePosted,
            otherInfo,
            jobJD,
            job_URL))

result_file = open("results_jobstreet_datascience_jobs_{}.csv".format(date.today()),'w', newline='', encoding='utf-8')
wr = csv.writer(result_file, quoting=csv.QUOTE_ALL)
for item in data:
    wr.writerow(item)