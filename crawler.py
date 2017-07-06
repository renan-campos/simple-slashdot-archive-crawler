import os
import urllib2
from HTMLParser import HTMLParser

ARCHIVE_URL = "https://slashdot.org/archive.pl"
OUTPUT_DIR  = "articles"

class ArticleParser(HTMLParser, object):
    """
	Extracts article and comments.
    """
    def __init__(self):
        super(ArticleParser, self).__init__()
	self.divs = 0

    def feed(self, data, fp):
	self.fp = fp
	super(ArticleParser, self).feed(data)

    def handle_starttag(self, tag, attrs):
	if tag == 'div' \
           and len(attrs) > 0 \
           and attrs[0][0] == 'id' \
           and ('text-' in attrs[0][1] or 'comment_body_' in attrs[0][1]):
		assert self.divs == 0
		self.divs = 1
	if self.divs > 0 and tag == 'div':
		self.divs += 1

    def handle_endtag(self, tag):
	if tag == 'div' and self.divs > 0:
		self.divs -= 1
		if (self.divs == 0):
			self.fp.write("\n")

    def handle_data(self, data):
	if (self.divs > 0):
		data = data.strip()
		if (data):
			self.fp.write("%s" % data)

class ArchiveParser(HTMLParser, object):
    """
	Extracts article links from archive page, then calls comment parser.
    """
    def __init__(self):
        super(ArchiveParser, self).__init__()
	
	self.parser = ArticleParser()
	self.links = False 

    def handle_starttag(self, tag, attrs):
	if tag == 'div' and ('class', 'archive_breaks before') in attrs:
		self.links = True
	if self.links > 0 and tag == 'footer':
		self.links = False
	if self.links > 0 and tag == 'a':
		url = "http:" + attrs[0][1]
		title = os.path.join(OUTPUT_DIR, url.split("/")[-1])
		with open(title, 'w') as f:
			print "Extracting comments from %s" % title
			article = urllib2.urlopen(url).read()
			self.parser.feed(article, f)



if __name__ == '__main__':
	parser = ArchiveParser()
	archive = urllib2.urlopen(ARCHIVE_URL).read()
	parser.feed(archive)
