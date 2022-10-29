import json
import re

import scrapy

from ..items import News


def get_main_list(streams):
    main_list = 'LISTID'

    for key, val in streams.items():
        if key.startswith(main_list):
            return val


def parse_tickers(finance):
    if finance is None or finance.get('stockTickers') is None:
        return []

    return [tick.get('symbol') for tick in finance.get('stockTickers')]


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
        news_script = response.xpath('//script[contains(text(),"root.App.main")]').get()
        news_json = re.search('{.*};', news_script).group(0)[:-1]
        news_parser = json.loads(news_json)
        streams = news_parser['context']['dispatcher']['stores']['StreamStore']['streams']
        news = get_main_list(streams)['data']['stream_items']
        articles = [x for x in news if x.get('type') == 'article']

        for x in articles:
            news = News(url=x.get('url'),
                        title=x.get('title'),
                        summary=x.get('summary'),
                        date=x.get('pubtime'),
                        category=x.get('categoryLabel'),
                        tickers=parse_tickers(x.get('finance')))

            if news.title not in self.state['news']:
                self.state['news'].add(news.title)
                yield news
