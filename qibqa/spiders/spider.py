import scrapy

from scrapy.loader import ItemLoader

from ..items import QibqaItem
from itemloaders.processors import TakeFirst


class QibqaSpider(scrapy.Spider):
	name = 'qibqa'
	start_urls = ['https://www.qib.com.qa/en/news-list/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="learn-more"]/@href').getall()
		for post in post_links:
			url = post.split('8443/qib')[1]
			yield response.follow(url, self.parse_post)

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').getall()
		next_page = [u.split('8443/qib')[1] for u in next_page]
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="media-detail"]/p//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//h3[@class="news-date"]/text()').get()

		item = ItemLoader(item=QibqaItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
