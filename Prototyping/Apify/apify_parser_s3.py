import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from apify_client import ApifyClient
import boto3
from io import BytesIO
from dotenv import load_dotenv

# Load AWS Credentials **ONCE**
load_dotenv(r's3_adobe_access.env')

# Initialize S3
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
BUCKET_NAME = os.getenv("BUCKET_NAME")


def upload_file_to_s3(file_content, s3_path):
    """Uploads a file to S3 and returns the public URL."""
    s3.upload_fileobj(file_content, BUCKET_NAME, s3_path)
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_path}"


# Initialize the Apify client (Replace with your actual API key)
API_TOKEN = "apify_api_TZa3vfX3DwXbl8JRX09lPILiyFedKY226np2"
client = ApifyClient(API_TOKEN)

# Define the Apify Web Scraper input with a required `pageFunction`
scraper_input = {
    "startUrls": [{"url": "https://en.wikipedia.org/wiki/Machine_learning"}],
    "maxPagesPerCrawl": 1,
    "proxyConfiguration": {"useApifyProxy": True},
    "pageFunction": """async function pageFunction(context) {
        return { html: context.content };
    }"""
}

# Run the Apify Web Scraper actor
run = client.actor("apify/web-scraper").call(run_input=scraper_input)

# Get the dataset ID
dataset_id = run["defaultDatasetId"]

# Fetch the scraped data
data = client.dataset(dataset_id).list_items()

# Extract and process the scraped content
for item in data.items:
    url = item.get("url", "")
    title = item.get("title", "Untitled Page")
    file_name = title.replace(" ", "_")

    # Define S3 paths
    parser_prefix = f"{file_name}/Apify"
    image_prefix = f"{parser_prefix}/images/"
    table_prefix = f"{parser_prefix}/tables/"
    markdown_path = f"{parser_prefix}/{file_name}.md"

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(item.get("html", ""), "html.parser")

    # Extract main text
    text_content = "\n".join([p.text for p in soup.find_all("p")])

    # Upload text content to S3
    text_buffer = BytesIO(text_content.encode("utf-8"))
    text_s3_path = f"{parser_prefix}/{file_name}.txt"
    text_url = upload_file_to_s3(text_buffer, text_s3_path)

    # Extract and save tables as CSV to S3
    table_urls = []
    tables = soup.find_all("table", class_="wikitable")

    for i, table in enumerate(tables):
        try:
            df = pd.read_html(str(table))[0]  # Convert HTML table to DataFrame
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            table_filename = f"table_{i+1}.csv"
            s3_table_path = f"{table_prefix}{table_filename}"
            table_url = upload_file_to_s3(csv_buffer, s3_table_path)

            table_urls.append(table_url)
            print(f"✅ Uploaded table {i+1} to S3: {table_url}")
        except Exception as e:
            print(f"❌ Error processing table {i+1}: {e}")

    # Download and upload images to S3
    image_urls = []
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if img_url.startswith("//"):
            img_url = "https:" + img_url  # Fix Wikipedia image URLs
        
        img_name = os.path.basename(img_url).split("?")[0]
        s3_image_path = f"{image_prefix}{img_name}"

        try:
            img_data = requests.get(img_url).content
            image_buffer = BytesIO(img_data)
            image_url = upload_file_to_s3(image_buffer, s3_image_path)
            image_urls.append(image_url)

            print(f"✅ Uploaded image to S3: {image_url}")
        except Exception as e:
            print(f"❌ Failed to download {img_url}: {e}")

    # Create Markdown content with extracted data
    markdown_content = f"# {title}\n\n"
    markdown_content += f"URL: [{url}]({url})\n\n"
    markdown_content += f"## Extracted Text:\n\n[View Text File]({text_url})\n\n"

    # Append images to Markdown
    if image_urls:
        markdown_content += "## Images:\n\n"
        for img_url in image_urls:
            markdown_content += f"![Image]({img_url})\n\n"

    # Append tables to Markdown
    if table_urls:
        markdown_content += "## Tables:\n\n"
        for table_url in table_urls:
            markdown_content += f"- [View Table]({table_url})\n"

    # Upload Markdown file to S3
    markdown_buffer = BytesIO(markdown_content.encode("utf-8"))
    markdown_s3_url = upload_file_to_s3(markdown_buffer, markdown_path)

    print(f"✅ Uploaded Markdown file to S3: {markdown_s3_url}")

print("\n🎯 Scraping complete. Data saved in S3.")
