summary: Pdf and Web scraping content parsing Guide
id:  pdf-web-content_parsing-guide
categories: Machine Learning, Data Processing
status: Published
authors: Hishita Thakkar
feedback link: https://your-feedback-link.com

# Pdf and Web scraping content parsing Guide

This guide provides step-by-step instructions on building a prototype application to extract, process, and organize data from unstructured sources like PDFs and webpages. The application will utilize both open-source tools and enterprise services for a comprehensive comparison. Additionally, the guide covers storing processed data in AWS S3 and creating APIs and a user interface for interaction.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Part 1: Data Extraction](#part-1-data-extraction)
    - Extracting from PDFs
    - Scraping Webpages
4. [Part 2: Comparison of Tools](#part-2-comparison-of-tools)
5. [Part 3: Standardization with Docling and MarkItDown](#part-3-standardization)
6. [Part 4: File Organization and Storage in AWS S3](#part-4-file-organization)
7. [Part 5: API Development with FastAPI](#part-5-api-development)
8. [Part 6: Client-Facing Application with Streamlit](#part-6-client-app)
9. [Conclusion](#conclusion)

---

## Prerequisites
- Basic knowledge of Python
- Familiarity with REST APIs
- AWS Account with S3 access
- Installed tools: Python 3.x, pip, virtualenv, Git

## Setup Instructions
1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-repo/ai-data-processing.git
    cd ai-data-processing
    ```
2. **Create a Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
4. **Setup AWS CLI**
    ```bash
    aws configure
    ```

---

## Part 1: Data Extraction

### Extracting from PDFs
1. **Using Open-Source Tools (PyPDF2, pdfplumber)**
    - Create `pdf_extraction.py`:
    ```python
    import PyPDF2
    import pdfplumber

    def extract_text_pypdf2(pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return " ".join([page.extract_text() for page in reader.pages])

    def extract_text_pdfplumber(pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            return " ".join([page.extract_text() for page in pdf.pages])
    ```

2. **Using Enterprise Service (Microsoft Document Intelligence)**
    - Refer to Microsoft’s official documentation for API setup.

### Scraping Webpages
1. **Using Open-Source Tools (BeautifulSoup, Requests)**
    - Create `web_scraping.py`:
    ```python
    import requests
    from bs4 import BeautifulSoup

    def scrape_with_bs4(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    ```

2. **Using Enterprise Service (Microsoft Document Intelligence)**
    - Process webpage content through API calls similarly to PDF processing.

---

## Part 2: Comparison of Tools

### Evaluation Criteria
- **Performance:** Speed and resource usage
- **Accuracy:** Quality of extracted content (text, images, tables)
- **Ease of Use:** Documentation clarity and API simplicity
- **Cost:** Open-source (free) vs. Enterprise (subscription-based)

| Tool               | Performance | Accuracy | Ease of Use | Cost       |
|--------------------|-------------|----------|-------------|------------|
| PyPDF2/pdfplumber  | Moderate    | High     | Easy        | Free       |
| BeautifulSoup      | High        | Moderate | Easy        | Free       |
| Microsoft Document Intelligence | High     | Very High   | Moderate   | Paid Subscription |

---

## Part 3: Standardization with Docling and MarkItDown

### Integrating Docling and MarkItDown
1. **Install Tools**
    ```bash
    pip install docling markitdown
    ```

2. **Convert to Markdown**
    - Create `standardize.py`:
    ```python
    from docling import convert as docling_convert
    from markitdown import convert as markitdown_convert

    def convert_with_docling(text):
        return docling_convert(text)

    def convert_with_markitdown(text):
        return markitdown_convert(text)
    ```

### Pros and Cons
| Tool        | Pros                         | Cons                  |
|-------------|------------------------------|-----------------------|
| Docling     | Retains detailed structure   | Slightly complex API  |
| MarkItDown  | Simple and fast conversion   | Limited formatting    |

---

## Part 4: File Organization and Storage in AWS S3

### Organizing Files
1. **Setup S3 Buckets**
    ```bash
    aws s3 mb s3://your-bucket-name
    ```
2. **Upload Files with Metadata**
    - Create `upload_s3.py`:
    ```python
    import boto3

    s3 = boto3.client('s3')

    def upload_file(file_name, bucket, object_name=None, metadata={}):
        if object_name is None:
            object_name = file_name
        s3.upload_file(file_name, bucket, object_name, ExtraArgs={'Metadata': metadata})
    ```

### Best Practices
- **Naming Conventions:** Use clear and consistent names.
- **Data Partitioning:** Organize by file type, date, or source.
- **Security:** Enable encryption and apply appropriate IAM policies.

---

## Part 5: API Development with FastAPI

### Creating APIs
1. **Install FastAPI and Uvicorn**
    ```bash
    pip install fastapi uvicorn
    ```
2. **Create API (`api.py`)**
    ```python
    from fastapi import FastAPI, UploadFile, File
    from pdf_extraction import extract_text_pypdf2
    from web_scraping import scrape_with_bs4

    app = FastAPI()

    @app.post("/upload-pdf/")
    async def upload_pdf(file: UploadFile = File(...)):
        content = extract_text_pypdf2(file.file)
        return {"content": content}

    @app.post("/scrape-web/")
    async def scrape_web(url: str):
        content = scrape_with_bs4(url)
        return {"content": content}

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    ```

---

## Part 6: Client-Facing Application with Streamlit

### Building the Interface
1. **Install Streamlit**
    ```bash
    pip install streamlit
    ```
2. **Create Streamlit App (`app.py`)**
    ```python
    import streamlit as st
    import requests

    st.title("Data Processing Tool")

    option = st.selectbox("Choose an option:", ["Upload PDF", "Scrape Webpage"])

    if option == "Upload PDF":
        uploaded_file = st.file_uploader("Upload your PDF")
        if uploaded_file:
            response = requests.post("http://localhost:8000/upload-pdf/", files={"file": uploaded_file})
            st.write(response.json())
    elif option == "Scrape Webpage":
        url = st.text_input("Enter webpage URL")
        if url:
            response = requests.post("http://localhost:8000/scrape-web/", json={"url": url})
            st.write(response.json())
    ```
3. **Run the App**
    ```bash
    streamlit run app.py
    ```

---

## Conclusion

In this guide, you learned to:
- Extract data from PDFs and webpages using both open-source and enterprise tools.
- Standardize data formats using Docling and MarkItDown.
- Organize and store data in AWS S3 following best practices.
- Develop APIs with FastAPI and create a user interface with Streamlit.

You can now enhance this prototype into a more comprehensive data processing application.

---

## Additional Resources
- [Docling GitHub Repository](https://github.com/DS4SD/docling)
- [MarkItDown GitHub Repository](https://github.com/microsoft/markitdown)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

