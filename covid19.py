import scrapy
from scrapy_splash import SplashRequest
from no_accent_vietnamese import no_accent_vietnamese
import re

class Covid19Spider(scrapy.Spider):
    name = 'covid19'
    allowed_domains = ['www.web.archive.org']
    script = '''
        function main(splash, args)
           url = args.url
           assert(splash:go(url))
           assert(splash:wait(5))
           return splash:html()
        end
    '''
    def start_requests(self):
        yield SplashRequest(url="https://web.archive.org/web/20210907023426/https://ncov.moh.gov.vn/vi/web/guest/dong-thoi-gian",callback=self.parse,endpoint="execute",args={
            'lua_source': self.script
        })
        
    def parse(self, response):
        for currency in response.xpath("//div[contains(@class, 'timeline-detail')]"):
            yield {
                'time' : currency.xpath(".//div[1]/h3/text()").get(),
                'new_case' : int(re.sub(r'\D','',no_accent_vietnamese(currency.xpath(".//div[2]/p[2]/text()").get())))
            }
        
        next_page = response.xpath("//ul[contains(@class, 'lfr-pagination-buttons pager')]/li[2]/a/@href")  #next_page = link trong chữ tiếp theo
        if next_page is not None :   #nếu nó không none
            next_page = response.urljoin(next_page)  #thực hiện response.urljoin
            yield scrapy.Request(next_page,callback=self.parse)  #request tới cái link đó
