import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import os
import csv

urls = pd.read_csv('data/URL_list.csv')
urls_list = urls['max(page)'].tolist()
urls_list_shorten = urls_list[:240]
#print(len(urls_list_shorten))
#print(urls_list)

def check_url_validation(urls_list):
    urls_responsive = []
    for url in urls_list:
        try:
            response = requests.get(url, timeout=5)  
            print("Processing current url", url)
            if response.status_code == 200:
                urls_responsive.append(url)
        except requests.exceptions.RequestException:
            #print(f"Error with URL {url}: {e}")
            continue
    return urls_responsive

responsive = check_url_validation(urls_list_shorten)
print(len(responsive))

def get_content_from_script(url):
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')
    script_tag = soup.find('script', id='viewed_product')
    if script_tag:
        script_content = script_tag.string
        if script_content:
            name_match = re.search(r'Name:\s*"(.*?)"', script_content)
            if name_match:
                name = name_match.group(1)
                print(f'Product Name: {name}')
            else:
                name = None
                print('Name not found')
            
            product_id_match = re.search(r'ProductID: (\d+)', script_content)
            if product_id_match:
                product_id = product_id_match.group(1)
                print(f'Product id: {product_id}')
            else:
                product_id = None
                print('Product id not found')
            
            categories_match = re.search(r'Categories: (\[.*?\])', script_content)
            if categories_match:
                categories = categories_match.group(1)
                print(f'Categories: {categories}')
            else:
                categories = None
                print('Categories not found')

            image_url_match = re.search(r'ImageURL: "(.*?)"', script_content)
            if image_url_match:
                image_url = image_url_match.group(1)
                print(f'Image url: {image_url}')
            else:
                image_url = None
                print('Image url not found')

            product_url_match = re.search(r'URL: "(.*?)"', script_content)
            if product_url_match:
                product_url = product_url_match.group(1)
                print(f'Product url: {product_url}')
            else:
                product_url = None
                print('Product url not found')

            brand_match = re.search(r'Brand: "(.*?)"', script_content)
            if brand_match:
                brand = brand_match.group(1)
                print(f'Brand: {brand}')
            else:
                brand = None
                print('Brand is not found')

            price_match = re.search(r'Price: "(.*?)"', script_content)
            if price_match:
                price = price_match.group(1)
                print(f'Price: {price}')
            else:
                price = None
                print('Price not found')

            compare_at_price_match = re.search(r'CompareAtPrice: "(.*?)"', script_content)
            if compare_at_price_match:
                compare_at_price = compare_at_price_match.group(1)
                print(f'Comapare at price: {compare_at_price}')
            else:
                compare_at_price = None
                print('Compare at price not found')

        else:
            print("No script content found")
    else:
        print("No matching <script> tag found")


def extracting_price(price_message):
    sale_price_match = re.search(r'Regular price\s*\$([\d,]+\.\d+)', price_message)
    compare_at_price_match = re.search(r'\(Was \$([\d,]+\.\d+)\)', price_message)

    sale_price = sale_price_match.group(1) if sale_price_match else "Unknown"
    compare_at_price = compare_at_price_match.group(1) if compare_at_price_match else "Unknown"

    return f"Price: ${sale_price}"#\nCompare at price: ${compare_at_price}"


def get_product_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    #product name
    #name = (soup.find('h1') or soup.find(class_='product-title') ).text.strip() if soup.find('h1') or soup.find(class_='product-title') else 'Unknown'
    product_name_tag = soup.find('meta', property="og:title")
    if product_name_tag:
        name = product_name_tag['content']
    else:
        name = "Unknown"

    #SKU
    sku = (soup.find('span', class_='product-sku') or soup.find('span', class_='productView-sku') or soup.find(string=re.compile('SKU'))).text.strip() if soup.find('span', class_='product-sku') or soup.find(string=re.compile('SKU')) else 'Unknown'
    if 'SKU:' in sku:
        sku = sku.replace('SKU:', '').strip()
    else:
        sku = "Unknown"


    #product url
    # product_url_tag = soup.find('meta', property='og:url')
    # if product_url_tag:
    #     product_url = product_url_tag['content']
    # else:
    #     product_url = url  # If no meta tag, use the URL passed to the function

    # #image url
    # image_url_tag = soup.find('meta', property='og:image')
    # if image_url_tag:
    #     image_url = image_url_tag['content']
    # else:
    #     image_url = "Unknown"  # If no meta tag, use the URL passed to the function


    #extracting price and currency
    price_tag = soup.find('meta', property='product:price:amount') or soup.find('meta', property='og:price:amount')
    if price_tag:
        price = price_tag['content']
    else: 
        price = 'Unknown'
    
    price_currency = soup.find('meta', property='product:price:currency') or soup.find('meta', property='og:price:currency')
    if price_currency:
        currency = price_currency['content']
    else:
        currency = ''
    

    return {
        "name": name,
        "sku": sku,
        "price": price,
        "currency": currency,
        #"url": product_url,
        #"image_url": image_url
    }

def tokenize(text):
    tokens = re.findall(r'\w+|\$[\d.]+|\S+', text)
    return tokens

def label_tokens(tokens, label_prefix):
    labeled_tokens = []
    for i, token in enumerate(tokens):
        if i == 0:
            labeled_tokens.append((token, f'B-{label_prefix}'))
        else:
            labeled_tokens.append((token, f'I-{label_prefix}'))
    return labeled_tokens

def save_to_csv(data, filename='data/products.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)

def clear_csv(filename='data/products.csv'):
    with open(filename, 'w') as f:
        f.truncate()


def process_data(url):
    extracted_data = get_product_data(url)

    # Tokenizing
    labeled_data = []
    for key, value in extracted_data.items():
        if value != 'Unknown':
            tokens = tokenize(value)
            labeled_tokens = label_tokens(tokens, key)
            labeled_data.extend([{"VALUE": token, "LABEL": label} for token, label in labeled_tokens])

    save_to_csv(labeled_data)


clear_csv()
for url in responsive:
    process_data(url)
