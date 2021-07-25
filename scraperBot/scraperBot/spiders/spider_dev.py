import scrapy

class QuoteSpider(scrapy.Spider):
    name = "KreepyKrawler"
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def start_requests(self):
        url = 'http://quotes.toscrape.com/'

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield{
                'text': quote.css("span.text::text").get(),
                'author': quote.css("small.author::text").get()
            }
        
        next_page = response.css("li.next a")
        if next_page is not None:
            yield from response.follow_all(next_page, self.parse)

