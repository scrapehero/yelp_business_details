from lxml import html  
import json
import requests
from exceptions import ValueError
from time import sleep
import re,urllib
import argparse

def parse(url):
	# url = "https://www.yelp.com/biz/frances-san-francisco"
	response = requests.get(url).text
	parser = html.fromstring(response)
	print "Parsing the page"
	raw_name = parser.xpath("//h1[contains(@class,'page-title')]//text()")
	raw_claimed = parser.xpath("//span[contains(@class,'claim-status_icon--claimed')]/parent::div/text()")
	raw_reviews = parser.xpath("//div[contains(@class,'biz-main-info')]//span[contains(@class,'review-count rating-qualifier')]//text()")
	raw_category  = parser.xpath('//div[contains(@class,"biz-page-header")]//span[@class="category-str-list"]//a/text()')
	hours_table = parser.xpath("//table[contains(@class,'hours-table')]//tr")
	details_table = parser.xpath("//div[@class='short-def-list']//dl")
	raw_map_link = parser.xpath("//a[@class='biz-map-directions']/img/@src")
	raw_phone = parser.xpath(".//span[@class='biz-phone']//text()")
	raw_address = parser.xpath('//div[@class="mapbox-text"]//div[contains(@class,"map-box-address")]//text()')
	raw_wbsite_link = parser.xpath("//span[contains(@class,'biz-website')]/a/@href")
	raw_price_range = parser.xpath("//dd[contains(@class,'price-description')]//text()")
	raw_health_rating = parser.xpath("//dd[contains(@class,'health-score-description')]//text()")
	rating_histogram = parser.xpath("//table[contains(@class,'histogram')]//tr[contains(@class,'histogram_row')]")
	raw_ratings = parser.xpath("//div[contains(@class,'biz-page-header')]//div[contains(@class,'rating')]/@title")

	working_hours = []
	for hours in hours_table:
		raw_day = hours.xpath(".//th//text()")
		raw_timing = hours.xpath("./td//text()")
		day = ''.join(raw_day).strip()
		timing = ''.join(raw_timing).strip()
		working_hours.append({day:timing})
	info = []
	for details in details_table:
		raw_description_key = details.xpath('.//dt//text()')
		raw_description_value = details.xpath('.//dd//text()')
		description_key = ''.join(raw_description_key).strip()
		description_value = ''.join(raw_description_value).strip()
		info.append({description_key:description_value})

	ratings_histogram = [] 
	for ratings in rating_histogram:
		raw_rating_key = ratings.xpath(".//th//text()")
		raw_rating_value = ratings.xpath(".//td[@class='histogram_count']//text()")
		rating_key = ''.join(raw_rating_key).strip()
		rating_value = ''.join(raw_rating_value).strip()
		ratings_histogram.append({rating_key:rating_value})
	
	name = ''.join(raw_name).strip()
	phone = ''.join(raw_phone).strip()
	address = ' '.join(' '.join(raw_address).split())
	health_rating = ''.join(raw_health_rating).strip()
	price_range = ''.join(raw_price_range).strip()
	claimed_status = ''.join(raw_claimed).strip()
	reviews = ''.join(raw_reviews).strip()
	category = ','.join(raw_category)
	cleaned_ratings = ''.join(raw_ratings).strip()

	if raw_wbsite_link:
		decoded_raw_website_link = urllib.unquote(raw_wbsite_link[0])
		website = re.findall("biz_redir\?url=(.*)&website_link",decoded_raw_website_link)[0]
	else:
		website = ''
	
	if raw_map_link:
		decoded_map_url =  urllib.unquote(raw_map_link[0])
		map_coordinates = re.findall("center=([+-]?\d+.\d+,[+-]?\d+\.\d+)",decoded_map_url)[0].split(',')
		latitude = map_coordinates[0]
		longitude = map_coordinates[1]
	else:
		latitude = ''
		longitude = ''

	if raw_ratings:
		ratings = re.findall("\d+[.,]?\d+",cleaned_ratings)[0]
	else:
		ratings = 0
	
	data={'working_hours':working_hours,
		'info':info,
		'ratings_histogram':ratings_histogram,
		'name':name,
		'phone':phone,
		'ratings':ratings,
		'address':address,
		'health_rating':health_rating,
		'price_range':price_range,
		'claimed_status':claimed_status,
		'reviews':reviews,
		'category':category,
		'website':website,
		'latitude':latitude,
		'longitude':longitude,
		'url':url
	}
	return data
	
if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument('url',help = 'yelp bussiness url')
	args = argparser.parse_args()
	url = args.url
	scraped_data = parse(url)
	yelp_id = url.split('/')[-1]
	with open("scraped_data-%s.json"%(yelp_id),'w') as fp:
		json.dump(scraped_data,fp,indent=4)
