import json
import re

import scrapy

from ..items import News


class NewsSpider(scrapy.Spider):
    name = "news_sp"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state = {'news': set()}

    def start_requests(self):
        if 'news' not in self.state.keys():
            self.state['news'] = set()

        yield scrapy.Request('https://finance.yahoo.com/news/', self.parse, dont_filter=True)

    def parse(self, response, **kwargs):
        main_list = 0
        side_list = 1

        news_script = response.xpath('//script[contains(text(),"root.App.main")]').get()
        news_json = re.search('{.*};', news_script).group(0)[:-1]
        news_parser = json.loads(news_json)
        streams = news_parser['context']['dispatcher']['stores']['StreamStore']['streams']
        news = list(streams.values())[main_list]['data']['stream_items']
        articles = [x for x in news if x.get('type') == 'article']

        for x in articles:
            news = News(url=x.get('url'),
                        title=x.get('title'),
                        summary=x.get('summary'),
                        date=x.get('pubtime'),
                        category=x.get('categoryLabel'),
                        tickers=[tick.get('symbol') for tick in x.get('stockTickers')])

            if news.title not in self.state['news']:
                self.state['news'].add(news.title)
                yield news
