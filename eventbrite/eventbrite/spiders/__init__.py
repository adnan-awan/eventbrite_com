# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import jmespath


def jmes_get(pattern, data, default=None):
    result = jmespath.search(pattern, data)
    if result is None and default is not None:
        return default
    return result