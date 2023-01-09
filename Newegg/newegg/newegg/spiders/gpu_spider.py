import scrapy
import csv
import datetime

class GpuSpider(scrapy.Spider):
    name = "gpu_prices"



    def start_requests(self):
        urls = [
            'https://www.newegg.com/global/sg-en/p/pl?d=rtx+3070',
            'https://www.newegg.com/global/sg-en/p/pl?d=rtx+3080',
            'https://www.newegg.com/global/sg-en/p/pl?d=rtx+4070',
            'https://www.newegg.com/global/sg-en/p/pl?d=rtx+4080'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        def return_timestamp():
            dt_time = datetime.datetime.today()
            return str(10000000000*dt_time.year + 100000000*dt_time.month + 1000000*dt_time.day + 10000*dt_time.hour + 100*dt_time.minute + dt_time.second)

        datetime_now = return_timestamp()
        item = response.url.split('+')[-1]
        filename = f'gpu-{item}.csv'
        products = []

        header = ['name','brand','price','linky','datetime']

        for product in response.xpath("//div[@class='item-cell']"):
            products.append(
                [product.xpath(".//div[@class='item-info']/a/text()").get(),
                product.xpath(".//div[@class='item-branding']/a//img/@title").get(),
                product.xpath(".//li[@class='price-current']//strong/text()").get(),
                product.xpath(".//div[@class='item-info']/a/@href").get(),
                datetime_now]
            )


        # self.log(f'header {header}')
        # self.log(f'products {products}')

        with open(filename, 'w', newline='') as f:
            write = csv.writer(f)
            write.writerow(header)
            write.writerows(products)
        
        self.log(f'Saved file {filename}')