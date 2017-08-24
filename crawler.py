from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request, urllib.error, urllib.parse
import argparse
import re
import codecs
import time
import random
import sys

get_yelp_page = \
    lambda zipcode, page_num: \
		'https://www.yelp.com/search?find_desc=Dentists&find_loc={0}&ns=1&start={1}'.format(zipcode, page_num)

ZIP_URL = "zipcodes.txt"
FIELD_DELIM = '###'
LISTING_DELIM = '((('

def get_zips():
    """
    """
    f = open(ZIP_URL, 'r+')
    zips = [int(zz.strip()) for zz in f.read().split('\n') if zz.strip() ]
    f.close()
    return zips

def crawl_page(zipcode, page_num, verbose=False):
    """
    This method takes a page number, yelp GET param, and crawls exactly
    one page. We expect 10 listing per page.
    """
    try:
        page_url = get_yelp_page(zipcode, page_num)
        soup = BeautifulSoup(urllib.request.urlopen(page_url).read(),"html.parser")
    except Exception as e:
        print(str(e))
        return []

    dentists = soup.findAll('div', attrs={'class':re.compile
            (r'^search-result natural-search-result')})
    try:
        assert(len(dentists) == 10)
    except AssertionError as e:
        # We make a dangerous assumption that yelp has 10 listing per page,
        # however this can also be a formatting issue, so watch out
        print('we have hit the end of the zip code', str(e))
        # False is a special flag, returned when quitting
        return [], False

    extracted = [] # a list of tuples
    for r in dentists:
        img = ''
        yelpPage = ''
        title = ''
        rating = ''
        addr = ''
        phone = ''
        categories = ''
        website = ''
        try:
            img = r.div('div', {'class':'media-avatar'})[0].img['src']
        except Exception as e:
            if verbose: print('img extract fail', str(e))
        try:
            title = r.find('a', {'class':'biz-name'}).getText()
        except Exception as e:
            if verbose: print('title extract fail', str(e))
        try:
            yelpPage = r.find('a', {'class':['biz-name','js-analytics-click']})['href']
        except Exception as e:
            if verbose: print('yelp page link extraction fail', str(e))
            continue
        try:
            categories = r.findAll('span', {'class':'category-str-list'})
            categories = ', '.join([c.getText() for c in categories if c.getText()])
        except Exception as e:
            if verbose: print("category extract fail", str(e))
        try:
            rating = r.find('i', {'class':re.compile(r'^star-img')}).img['alt']
        except Exception as e:
            if verbose: print('rating extract fail', str(e))
        try:
            addr = r.find('div', {'class':'secondary-attributes'}).address.getText()
        except Exception as e:
            if verbose: print('address extract fail', str(e))

        time.sleep(random.randint(1, 2) * .931467298)
        try:
            soup2 = BeautifulSoup(urllib.request.urlopen(urljoin('http://www.yelp.com',
                                                        yelpPage)).read())
            try:
                website = soup2.find('span', {'class':"biz-website js-add-url-tagging"}).a.getText()
            except Exception as e:
                if verbose: print ('website extract fail', str(e))
            try:
                phone = soup2.find('span', {'class':'biz-phone'}).getText()
            except Exception as e:
                if verbose: print ('phone extract fail', str(e))
        except Exception as e:
            if verbose: print("**failed to get you a page", str(e))

        # if title: print('title:', title.strip(' \t\n\r'))
        # if categories: print('categories:', categories.strip(' \t\n\r'))
        # if rating: print('rating:', rating.strip(' \t\n\r'))
        # if img: print('img:', img.strip(' \t\n\r'))
        # if addr: print('address:', addr.strip(' \t\n\r'))
        # if phone: print('phone:', phone.strip(' \t\n\r'))
        # if website: print ('website:',website.strip(' \t\n\r'))
        
        print(title.strip(' \t\n\r') + ":" + addr.strip(' \t\n\r') + ":" + phone.strip(' \t\n\r') + ":" + website.strip(' \t\n\r'))

    return extracted, True

def crawl(zipcode=None):
    page = 0
    flag = True
    some_zipcodes = [zipcode]
    if not zipcode:
	    print ( 'Need to provide a valid zip code.' )
	    return []
    # some_zipcodes = [zipcode] if zipcode else get_zips()
    #  if zipcode is None:
        # print ( '\n**We are attempting to extract all zipcodes in America!**'

    for zipcode in some_zipcodes:
        print('\n===== Attempting extraction for zipcode <', zipcode, '>=====\n')
        while flag:
            extracted, flag = crawl_page(zipcode, page)
            if not flag:
                print('extraction stopped or broke at zipcode')
                break
            page += 10
            time.sleep(random.randint(1, 2) * .931467298)

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Extracts all yelp restaurant \
        # data from a specified zip code (or all American zip codes if nothing \
        # is provided)')
    # parser.add_argument('-z', '--zipcode', type=int, help='Enter a zip code \
        # you\'t like to extract from.')
    # args = parser.parse_args()
    zip = sys.argv[1]
    print ('Processing zipcode ' + zip)
    crawl(zip)