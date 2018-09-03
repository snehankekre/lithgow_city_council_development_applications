# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful


import six
import logging
import scraperwiki
import sqlite3
import time
import urllib2
import lxml.html
from splinter import Browser
from selenium.common.exceptions import TimeoutException
from six import BytesIO

def getrecord(html):
  date_scraped = time.strftime('%Y-%m-%d')
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
    record['date_received'] =  time.strftime('%Y-%m-%d', time.strptime(dadate[index], '%d/%m/%Y'))
    record['info_url']=info_url + appid[index]
    record['comment_url']='mailto:council@lithgow.nsw.gov.au?subject=Development%20Application%20Enquiry%20' + appid[index]
    record['date_scraped']=date_scraped
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



logging.basicConfig(level=logging.INFO)

scrape_url='https://eservices.lithgow.nsw.gov.au/ePropertyProd/P1/eTrack/eTrackApplicationSearchResults.aspx?Field=S&Period=L7&r=P1.WEBGUEST&f=%24P1.ETR.SEARCH.SL7'

## fix data (only run these lines once)
#scraperwiki.sqlite.execute("update data set date_received=substr(date_received, 6, 4)||'-'||substr(date_received, 3, 2)||'-0'||substr(date_received, 1, 1) where date_received like '%2017' and length(date_received)=9")
#scraperwiki.sqlite.execute("update data set date_received=substr(date_received, 7, 4)||'-'||substr(date_received, 4, 2)||'-'||substr(date_received, 1, 2) where date_received like '%2017' and length(date_received)=10")
#scraperwiki.sqlite.execute("update data set date_scraped=substr(date_scraped, 6, 4)||'-'||substr(date_scraped, 3, 2)||'-0'||substr(date_scraped, 1, 1) where date_scraped like '%2017' and length(date_scraped)=9")
#scraperwiki.sqlite.execute("update data set date_scraped=substr(date_scraped, 7, 4)||'-'||substr(date_scraped, 4, 2)||'-'||substr(date_scraped, 1, 2) where date_scraped like '%2017' and length(date_scraped)=10")
#scraperwiki.sqlite.commit() 
#print scraperwiki.sqlite.select('* from data')
#scraperwiki.sqlite.execute("update data set date_scraped=date_received")


# browser/scraper
with Browser() as browser:
  browser.driver.set_page_load_timeout(300)
  try:
    browser.visit(scrape_url)
    html=browser.html
    getrecord(html)
    links=browser.find_link_by_partial_href('Page$2')
    if (links.is_empty()==False):
      browser.click_link_by_partial_href('Page$2')
      html=browser.html
      getrecord(html)
  except TimeoutException:
    logging.info('Process timed out')
    pass
