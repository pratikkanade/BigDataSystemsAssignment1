import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import boto3
from io import BytesIO


def upload_file_to_s3(file_content, bucket_name, s3_path):

    #load_dotenv()
    load_dotenv(r'C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Assignment 1\environment\s3_adobe_access.env')

    #s3 = boto3.client('s3')
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    s3.upload_fileobj(file_content, bucket_name, s3_path)



# Function to convert extracted HTML to Markdown sequentially and download images & tables
def convert_to_markdown(url, soup, bucket_name):
    """Converts HTML content to structured Markdown format sequentially and downloads images and tables."""

    parser_prefix = f"{url}/BeautifulSoup"
    image_prefix = f"{parser_prefix}/images/"
    table_prefix = f"{parser_prefix}/tables/"
    markdown_path = f"{parser_prefix}/{url}.md"

    markdown_content = ""
    table_count = 0
    image_counter = 0

    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'img', 'a', 'table']):
        if element.name.startswith('h'):
            level = int(element.name[1])
            markdown_content += f"{'#' * level} {element.get_text(separator=' ', strip=True)}\n\n"

        elif element.name == 'p':
            paragraph_text = element.get_text(separator=' ', strip=True)
            paragraph_text = re.sub(r'\s+', ' ', paragraph_text)  # Normalize excessive spaces
            markdown_content += f"{paragraph_text}\n\n"

        elif element.name == 'ul':
            for li in element.find_all('li'):
                markdown_content += f"- {li.get_text(separator=' ', strip=True)}\n"
            markdown_content += "\n"

        elif element.name == 'ol':
            for idx, li in enumerate(element.find_all('li'), start=1):
                markdown_content += f"{idx}. {li.get_text(separator=' ', strip=True)}\n"
            markdown_content += "\n"

        elif element.name == 'img':
            src = element.get('src')
            if src:
                if src.startswith('//'):
                    src = 'https:' + src  # Fix protocol-less URLs

                #response = requests.get(src)
                #image_data = BytesIO(response.content)

                response = requests.get(src, stream=True)
                response.raise_for_status()
        
                # Get file extension
                ext = os.path.splitext(url.split("?")[0])[-1].lower()
                if ext not in ['.jpg', '.jpeg', '.png']:
                    ext = '.jpg'  # Default to JPG if extension is missing or unknown

                #image_filename = f"image_{image_counter + 1}.png"
                image_filename = f"image_{image_counter + 1}.{ext}"

                s3_image_path = f"{image_prefix}{image_filename}"
                upload_file_to_s3(BytesIO(response.content), bucket_name, s3_image_path)

                markdown_content += f"![Image](images/{image_filename})\n\n"


        elif element.name == 'table':

            df = pd.read_html(str(element))[0]
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False, encoding="utf-8")
            #df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            table_filename = f"table{table_count + 1}.csv"
            s3_table_path = f"{table_prefix}{table_filename}"

            upload_file_to_s3(csv_buffer, bucket_name, s3_table_path)

            markdown_content += f"[Table {table_count}]({table_filename})\n\n"

            table_count += 1

        elif element.name == 'a' and element.get('href'):
            link_text = element.get_text(strip=True)
            link_url = element['href']
            markdown_content += f"[{link_text}]({link_url})\n\n"

    # Upload markdown directly to S3
    markdown_buffer = BytesIO(markdown_content.encode("utf-8"))
    upload_file_to_s3(markdown_buffer, bucket_name, markdown_path)

    return markdown_path


# Function to scrape webpage using Beautiful Soup
def parse_with_bs(url, bucket_name):
    """Scrapes a webpage to extract images, tables, and text using Selenium."""

    options = Options()
    #options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url)
    
    time.sleep(5)  # Allow some time for content to load

    url = url.replace('/', '_') 

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Remove unwanted tags
    for script in soup(["script", "style", "header", "footer", "nav", "aside", "noscript"]):
        script.extract()

    # Convert text to Markdown format with images and tables
    markdown_path = convert_to_markdown(url, soup, bucket_name)
    return markdown_path


#bucket_name = 'bigdatasystems'
#url = "https://en.wikipedia.org/wiki/Machine_learning"

#print("Scraping webpage content using Selenium...")
#scraped_content = parse_with_bs(url, bucket_name)

