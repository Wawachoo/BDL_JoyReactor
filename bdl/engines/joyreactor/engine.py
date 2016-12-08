import os
import urllib
import requests
import re
from lxml import etree as etree
from bdl.item import Item
from bdl.exceptions import *
import bdl.downloaders
import bdl.engine


class Engine(bdl.engine.Engine):

    # =========================================================================
    # BDL ENGINE API
    # =========================================================================

    @staticmethod
    def get_repo_name(url, **kwargs):
        return urllib.parse.urlparse(url).path[1:].split('/')[1]

    @staticmethod
    def is_reachable(url, **kwargs):
        return requests.head(url).ok

    def __init__(self, url, config, progress):
        super().__init__(url, config, progress)

    def pre_connect(self, **kwargs):
        # Set subject name and mode.
        paths = urllib.parse.urlparse(self.url).path[1:].split('/')
        self.config["tag"] = paths[1]
        self.config["order"] = len(paths) > 2 and paths[2] or "all"
        # Set effective URL.
        self.config["url"] = "http://joyreactor.com/tag/{tag}/{order}/{pageid}"
        # Set current page number.
        self.config["pageid"] = 1

    def pre_update(self, **kwargs):
        pass

    def count_all(self, **kwargs):
        rep = requests.get(self.url)
        tree = etree.fromstring(rep.text, etree.HTMLParser())
        return int(tree.find(".//*[@id='blogSubscribers']/span[2]").text)

    def count_new(self, last_item, last_position, **kwargs):
        return (self.count_all() - last_position)

    def update_all(self, **kwargs):
        config["pageid"] = 1
        update_new(None, None, kwargs)

    def update_new(self, last_item, last_position, **kwargs):
        session = requests.Session()
        parser = etree.HTMLParser()
        pagescount = self.get_pages_count(session, parser)
        self.logger.debug("Pages count: {}".format(pagescount))
        if last_item is not None:
            last_id = self.item_url_id(last_item.url)
        else:
            last_id = -1
        self.logger.debug("Last item ID: {}".format(last_id))
        for pageid in range(self.config["pageid"], pagescount+1):
            self.logger.debug("Processing page {} on {}".format(pageid, pagescount))
            self.config["pageid"] = pageid
            pageurl = self.config["url"].format(tag=self.config["tag"],
                                                order=self.config["order"],
                                                pageid=pageid)
            pageitems = [i for i in self.get_pages_items_urls(pageurl, session, parser) if self.item_url_id(i) > last_id]
            self.logger.debug("New items found: {}".format(len(pageitems)))
            last_id = self.item_url_id(pageitems[-1])
            self.logger.debug("Last item ID: {}".format(last_id))
            for item in bdl.downloaders.generic(pageitems, progress=self.progress):
                self.logger.debug("Yielding item: {}".format(item.url))
                yield item

    def update_selection(self, urls, **kwargs):
        for item in bdl.downloaders.generic(urls, progress=self.progress):
            yield item

    # =========================================================================
    # ENGINE-SPECIFIC
    # =========================================================================

    def get_pages_count(self, session, parser):
        """Returns the number of pages for the selected repository.
        """
        req = session.get(self.config["url"].format(tag=self.config["tag"],
                                                    order=self.config["order"],
                                                    pageid=1))
        tree = etree.fromstring(req.text, parser)
        node = tree.find(".//*/div[@class='pagination_expanded']/a[@href='/tag/{}/all']".format(self.config["tag"]))
        return int(node.text)

    def get_pages_items_urls(self, pageurl, session, parser):
        """Return the list of `pageurl` items URL.
        """
        req = session.get(pageurl)
        tree = etree.fromstring(req.text, parser)
        pageitems = []
        for post in tree.findall(".//*[@class='post_content']"):
            postitems = []
            for postmedia in post.findall(".//div[@class='image']"):
                for path, attr in [("img", "src"), ("span/a", "href")]:
                    try:
                        postitems.append(postmedia.find(path).attrib[attr])
                    except Exception:
                        pass
            postitems.reverse()
            [pageitems.append(item) for item in postitems]
        pageitems.reverse()
        return pageitems

    def item_url_id(self, url):
        """Returns an item ID from the URL.
        """
        return int(url.split('/')[-1].split('.')[0].split('-')[-1])
