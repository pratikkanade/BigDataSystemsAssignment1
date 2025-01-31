import os
import re
import requests
import base64
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Function to clean extracted text
def clean_text(text):
    """Remove unnecessary characters and ensure UTF-8 encoding."""
    cleaned_text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    cleaned_text = cleaned_text.encode("utf-8", "ignore").decode("utf-8")  # Ensure UTF-8 encoding
    return cleaned_text.strip()

# Function to convert extracted HTML to Markdown sequentially and download images
def convert_to_markdown(soup, image_dir):
    """Converts HTML content to structured Markdown format sequentially and downloads images."""
    markdown_content = ""

    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'img', 'a']):
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
                
                # Download image and add to Markdown
                image_name = download_image(src, image_dir)
                if image_name:
                    markdown_content += f"![Image](images/{image_name})\n\n"
        
        elif element.name == 'a' and element.get('href'):
            link_text = element.get_text(strip=True)
            link_url = element['href']
            markdown_content += f"[{link_text}]({link_url})\n\n"

    return markdown_content

# Function to download images
def download_image(url, image_dir):
    """Downloads an image and saves it in the specified directory."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file extension
        ext = os.path.splitext(url.split("?")[0])[-1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            ext = '.jpg'  # Default to JPG if extension is missing or unknown

        # Save the image
        image_name = f"image_{len(os.listdir(image_dir)) + 1}{ext}"
        image_path = os.path.join(image_dir, image_name)

        with open(image_path, 'wb') as img_file:
            for chunk in response.iter_content(1024):
                img_file.write(chunk)

        return image_name
    except Exception as e:
        print(f"Failed to download image {url}: {e}")
        return None

# Function to scrape webpage using Selenium
def scrape_webpage_selenium(url):
    """Scrapes a webpage to extract images, tables, and text using Selenium."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url)
    time.sleep(5)  # Allow some time for content to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Remove unwanted tags
    for script in soup(["script", "style", "header", "footer", "nav", "aside", "noscript"]):
        script.extract()

    # Prepare image storage directory
    image_dir = "scraped_content/images"
    os.makedirs(image_dir, exist_ok=True)

    # Convert text to Markdown format
    markdown_text = convert_to_markdown(soup, image_dir)

    # Extract tables
    tables = [str(table) for table in soup.find_all('table')]

    return {
        "tables": tables,
        "text": markdown_text[:50000]  # Limit text size
    }

# Function to save content (Markdown text and tables)
def save_content(content_dict, base_dir="scraped_content"):
    """Saves extracted content (text, tables) to separate folders."""
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Save text content in Markdown format
    text_dir = os.path.join(base_dir, "text")
    os.makedirs(text_dir, exist_ok=True)
    text_file_path = os.path.join(text_dir, "content.md")

    with open(text_file_path, "w", encoding="utf-8") as file:
        file.write(content_dict['text'])

    print(f"Text content saved as Markdown: {text_file_path}")

    # Save tables as CSV
    tables_dir = os.path.join(base_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)
    for idx, table_html in enumerate(content_dict['tables']):
        try:
            soup = BeautifulSoup(table_html, 'html.parser')
            table = soup.find('table')
            df = pd.read_html(str(table))[0]  # Convert table to DataFrame

            # Save as CSV
            table_file_path = os.path.join(tables_dir, f"table_{idx}.csv")
            df.to_csv(table_file_path, index=False, encoding="utf-8")
            print(f"Saved table {idx} as CSV: {table_file_path}")
        except Exception as e:
            print(f"Failed to save table {idx} as CSV: {e}")

    print(f"Content saved in '{base_dir}' directory.")

if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Machine_learning"

    print("Scraping webpage content using Selenium...")
    scraped_content = scrape_webpage_selenium(url)

    if scraped_content["text"] or scraped_content["tables"]:
        print("Saving content to separate folders...")
        save_content(scraped_content)
    else:
        print("No content found on the webpage.")
