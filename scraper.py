# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful


import logging
import scraperwiki
import sqlite3
import time
import urllib2
import lxml.html
from splinter import Browser

def getrecord(html):
  root = lxml.html.fromstring(html)
  appid=root.xpath('//table[1]//tr[(@class="alternateRow") or (@class="normalRow")]/td[1]/a//text()')
  dadate=root.xpath('//table[1]//tr[(@class="alternateRow") or (@class="normalRow")]/td[2]//text()')
  descr=root.xpath('//tr[not(@class="pagerRow")]/td[3]//text()')
  addr=root.xpath('//tr[not(@class="pagerRow")]/td[6]/a//text()')
  info_url="https://eservices.lithgow.nsw.gov.au/ePropertyProd/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=%24P1.ETR.APPDET.VIW&ApplicationId="
  record={}
  for index in range(len(appid)):
    record['council_reference'] = appid[index]
    record['description'] = descr[index]
    record['address'] = addr[index]
    record['date_received'] = dadate[index]
    record['info_url']=info_url + appid[index]
    record['comment_url']='mailto:council@lithgow.nsw.gov.au?subject=Development%20Application%20Enquiry%20' + appid[index]
    try:
      if scraperwiki.sqlite.select('* FROM data WHERE council_reference="%s"' % record['council_reference']):
	logging.info('Skipping existing record in sqlite: ' + record['council_reference'])
	continue
    except sqlite3.OperationalError, e:
      if 'no such table:' in e.message:
	logging.info('Sqlite data does not exist yet. Will be created.')
	pass
      else:
	raise

    scraperwiki.sqlite.save(unique_keys=['council_reference'], data=record)



#logging.basicConfig(level=logging.DEBUG)

scrape_url='https://eservices.lithgow.nsw.gov.au/ePropertyProd/P1/eTrack/eTrackApplicationSearchResults.aspx?Field=S&Period=L7&r=P1.WEBGUEST&f=%24P1.ETR.SEARCH.SL7'

# browser
with Browser('phantomjs', load_images=False) as browser:
  browser.visit(scrape_url)
  html=browser.html
  getrecord(html)
  links=browser.find_link_by_partial_href('Page$2')
  if (links.is_empty()==False):
    browser.click_link_by_partial_href('Page$2')
    html=browser.html
    getrecord(html)
