#!python3
#webscrape_newegg_rtx3060 scrapes the website regularly for updates on the prices for rtx 3060

import requests, bs4

link = 'https://www.newegg.com/global/sg-en/p/pl?d=gpu+rtx3060&PageSize=96&N=4131'

names = ['Name']
prices = ['Price']
brands = ['Brand']
shipping = ['Shipping']

res = requests.get(link)
try:
    res.raise_for_status()
except Exception as exc:
    print('Error due to ' + str(exc))
soup = bs4.BeautifulSoup(res.text, 'html.parser')
product_name = soup.select('[class=item-title]')
product_price = soup.select('[class=price-current]')
product_shipping = soup.select('[class=price-ship]')

names.append(product_name[0].getText())
prices.append(product_price[0].getText())
shipping.append(str(product_shipping[0].getText())

print(product_shipping[0].getText())