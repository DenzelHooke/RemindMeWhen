from itemloaders.processors import Identity, MapCompose, TakeFirst, Join
from w3lib.html import remove_tags
from scrapy.loader import ItemLoader 

# ---- Input Processors ----

def join_url(rel_url):
    return f"https://www.amazon.com{rel_url}"

def str_to_float(string):
    return float(string)

def replace_char(string):
    string = string.replace('$', '')

    if ',' in string:
        string = string.replace(',','')

    return string    

def clean_ws(string):
    return string.strip()

def shorten_str(string):
    return string[:50]

def user_shorten_str(string):
    return string[:30]

# -------------


class ProductLoader(ItemLoader):

    default_output_processor = TakeFirst()
    
    name_in = MapCompose(remove_tags, clean_ws, shorten_str)
    url_in = MapCompose(remove_tags)
    price_in = MapCompose(remove_tags, replace_char, str_to_float)

 