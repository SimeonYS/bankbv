import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbankbvItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BbankbvSpider(scrapy.Spider):
	name = 'bankbv'
	start_urls = ['https://www.bankbv.com/customer-service/about/news']

	def parse(self, response):
		post_links = response.xpath('//li[@class="medium-4 cell"]/a[1]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@title="Go to next page"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = ' '.join(response.xpath('//div[@class="content"]//p//text()').getall()[:5])
		date = re.findall(r'\w+\s\d+\,\s\d+', date)
		if not date:
			date = ' '.join(response.xpath('//div[@class="cell medium-7"]/p//text()|//div[@class="content"]/h3/text()').getall()[:2])
			date = re.findall(r'\w+\s\d+\,\s\d+', date)
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//div[@class="content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbankbvItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
