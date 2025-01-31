import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from apify_client import ApifyClient

# Initialize the Apify client (Replace with your actual API key)
API_TOKEN = "apify_api_TZa3vfX3DwXbl8JRX09lPILiyFedKY226np2"
client = ApifyClient(API_TOKEN)

# Define the Apify Web Scraper input
scraper_input = {
    "startUrls": [{"url": "https://en.wikipedia.org/wiki/Machine_learning"}],
    "maxPagesPerCrawl": 1,
    "proxyConfiguration": {"useApifyProxy": True},
    "pageFunction": """async function pageFunction(context) {
        const $ = context.jQuery;
        return {
            title: $('h1').text(),  
            text: $('p').text(),  
            html: $('html').html(),  
            images: $('img').map((i, el) => $(el).attr('src')).get(),  
            tables: $('table.wikitable').map((i, el) => $(el).html()).get()  
        };
    }"""
}

# Run the Apify Web Scraper actor with the correct input
run = client.actor("apify/web-scraper").call(run_input=scraper_input)

# Get the dataset ID
dataset_id = run["defaultDatasetId"]

# Fetch the scraped data correctly
data = client.dataset(dataset_id).list_items()

# ✅ FIX: Use `.items` to access the list
for item in data.items:
    url = item.get("url", "")
    title = item.get("title", "Untitled Page")
    text_content = item.get("text", "")

    # Create directories for storage
    output_dir = "scraped_data"
    images_dir = os.path.join(output_dir, "images")
    tables_dir = os.path.join(output_dir, "tables")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)

    # Parse the HTML to extract images and tables
    soup = BeautifulSoup(item.get("html", ""), "html.parser")

    # Download images
    image_paths = []
    for img_url in item.get("images", []):
        if img_url.startswith("//"):
            img_url = "https:" + img_url  # Fix Wikipedia image URLs
        
        img_name = os.path.basename(img_url).split("?")[0]
        img_path = os.path.join(images_dir, img_name)
        image_paths.append(img_path)

        try:
            img_data = requests.get(img_url).content
            with open(img_path, "wb") as img_file:
                img_file.write(img_data)
            print(f"Downloaded image: {img_name}")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

    # Save tables as CSV
    table_paths = []
    for i, table_html in enumerate(item.get("tables", [])):
        try:
            df = pd.read_html(table_html)[0]  # Convert HTML table to DataFrame
            csv_path = os.path.join(tables_dir, f"table_{i+1}.csv")
            df.to_csv(csv_path, index=False)
            table_paths.append(csv_path)
            print(f"Saved table {i+1} as CSV")
        except Exception as e:
            print(f"Error processing table {i+1}: {e}")

    # Create Markdown file with extracted data
    markdown_content = f"# {title}\n\n"
    markdown_content += f"URL: [{url}]({url})\n\n"
    markdown_content += "## Extracted Text:\n\n" + text_content + "\n\n"

    # Append paths to extracted images
    if image_paths:
        markdown_content += "## Images:\n\n"
        for img_path in image_paths:
            markdown_content += f"![{os.path.basename(img_path)}](./{img_path})\n\n"

    # Append paths to extracted tables
    if table_paths:
        markdown_content += "## Tables:\n\n"
        for table_path in table_paths:
            markdown_content += f"- [{os.path.basename(table_path)}](./{table_path})\n"

    # Save the Markdown file
    md_path = os.path.join(output_dir, "machine_learning.md")
    with open(md_path, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)
    print(f"Saved text to markdown file: {md_path}")

print("\n✅ Scraping complete. Data saved in 'scraped_data' folder.")
