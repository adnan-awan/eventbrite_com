import json
from copy import deepcopy

from scrapy import Selector, Request
from scrapy.spiders import SitemapSpider

from eventbrite.items import EventbriteItemLoader
from eventbrite.spiders import jmes_get


class Eventbrite(SitemapSpider):
    name = 'eventbrite'
    rotate_user_agent = True

    sitemap_urls = ['https://www.eventbrite.com/sitemap_xml/sitemap_index.xml']
    sitemap_rules = [
        ('/e/', 'parse_event'),
    ]

    def __init__(self, *args, **kwargs):
        super(Eventbrite, self).__init__(*args, **kwargs)
        self.event_url = kwargs.get('event_url')

    def start_requests(self):
        if self.event_url:
            yield Request(self.event_url, self.parse_event)
        else:
            for url in self.sitemap_urls:
                yield Request(url, self._parse_sitemap)

    def parse_event(self, response):
        loader = EventbriteItemLoader(response=response, selector=Selector(response=response))
        loader.add_css('name', '.listing-hero-title::text')
        loader.add_value('url', response.url)
        loader.add_css('description', '.structured-content-rich-text ::text')
        loader.add_css('cost', '.js-panel-display-price::text')
        data = self.get_js_data(response)
        loader.add_value('location', jmes_get('venue.display_full_address', data))
        loader.add_value('image_url', jmes_get('image', data))
        loader.add_value('canonical_url', jmes_get('canonical_url', data))
        loader.add_value('summary', jmes_get('summary', data))
        loader.add_value('response_url', response.url)
        # loader.add_value('meta_description', jmes_get('meta_description', data))
        loader.add_value('id', response.url, re=r'-(\d+)$')
        base_item = loader.load_item()
        series = jmes_get('listing_series_events', data, default=[])
        if not series:
            self.logger.debug(f'No sub events found {response.url}')
            yield base_item
            return

        for s in series:
            sloader = EventbriteItemLoader(item=deepcopy(base_item))
            sloader.add_value('parent_id', base_item['id'])
            sloader.replace_value('id', jmes_get('id', s))
            sloader.add_value('status', jmes_get('status', s))
            sloader.add_value('locale', jmes_get('locale', s))
            sloader.add_value('end_datetime', jmes_get('end.local', s))
            sloader.add_value('end_timezone', jmes_get('end.timezone', s))
            sloader.add_value('start_datetime', jmes_get('start.local', s))
            sloader.add_value('start_timezone', jmes_get('start.timezone', s))
            sloader.replace_value('url', jmes_get('url', s))
            yield sloader.load_item()

    def get_js_data(self, response):
        # resp = response.replace(
        #     body=response.body.decode('unicode-escape')
        # )
        query = 'script:contains("model: {")'
        regex = r',\s*model:\s*({"display_date".*?}),\s*collection'
        js_string = response.css(query).re_first(regex)
        try:
            data = json.loads(js_string)
        except (ValueError, TypeError):
            self.logger.warning(f'Error while parsing json {response.url}')
            return

        return data
