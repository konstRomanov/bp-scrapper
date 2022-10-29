import json
import re

import scrapy

from ..items import News


class TickerNewsSpider(scrapy.Spider):
    name = "ticker_news_sp"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.state = {'news': {}}

    def start_requests(self):
        tickers = ['META', 'AMZN', 'AAPL', 'NFLX', 'GOOGL']

        if 'news' not in self.state.keys():
            self.state['news'] = dict()

        for ticker in tickers:
            if ticker not in self.state['news'].keys():
                self.state['news'][ticker] = set()

            yield scrapy.Request(f'https://finance.yahoo.com/quote/{ticker}/news?p={ticker}',
                                 self.parse,
                                 dont_filter=True)

    def parse(self, response, **kwargs):
        news_list = 0

        ticker_news_script = response.xpath('//script[contains(text(),"root.App.main")]').get()
        ticker_news_json = re.search('{.*};', ticker_news_script).group(0)[:-1]
        ticker_news_parser = json.loads(ticker_news_json)
        stores = ticker_news_parser['context']['dispatcher']['stores']

        symbol = stores['QuoteSummaryStore']['symbol']

        streams = stores['StreamStore']['streams']
        news = list(streams.values())[news_list]['data']['stream_items']
        articles = [x for x in news if x['type'] == 'article']

        for x in articles:
            news = News(url=x.get('url'),
                        tickers=[symbol],
                        title=x.get('title'),
                        summary=x.get('summary'),
                        date=x.get('pubtime'))

            if news.title not in self.state['news'][symbol]:
                self.state['news'][symbol].add(news.title)
                yield news
