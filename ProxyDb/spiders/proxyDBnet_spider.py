import re
import base64
from scrapy import Request, Spider


class proxyDBnetSpider(Spider):
    name = "proxyDB"

    def start_requests(self):
        urls = ['http://proxydb.net/']
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        for jsString in response.xpath("//div[@class='table-responsive']/table"
                                       "/tbody/tr/td/script/text()").extract():
            sub_js = jsString.split(";")

            ip_first = re.findall(r"'(.+?)'.split", sub_js[0])[0][::-1]

            bstr = re.findall(r"atob\('(.+?)'.replace", sub_js[1])[0]
            ip_second = ""
            for symb in re.findall(r"\\x([0-9A-Fa-f]{2})", bstr):
                ip_second = ip_second + chr(int(symb, 16))
            ip_second = re.findall(r"b'(.+)'",
                                   str(base64.b64decode(ip_second)))[0]

            data_atr = re.findall(r"querySelector\('\[(.+)\]'\)", sub_js[2])[0]
            data_div = response.xpath("//div[@" + re.findall(
                r"Selector\('\[(.+)\]'\)", sub_js[2])[0] + "]").extract_first()
            port = int(re.findall(r"\(([0-9]+)", sub_js[2])[0], 10) + int(
                re.findall(data_atr + '="(.+)">', data_div)[0], 10)
            yield {
                'ip': ip_first + ip_second,
                'port': port,
            }
        url = response.xpath(
            '//ul[contains(@class,"pagination")]/li[not(contains(@class,'
            '"disabled"))][last()]/a/@href').extract_first()
        yield Request(url=response.urljoin(url), callback=self.parse)
