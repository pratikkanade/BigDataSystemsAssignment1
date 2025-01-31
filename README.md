# BigDataSystemsAssignment1
Project Summary: AI-Powered Document Processing & Standardization
Overview
This project explores the feasibility of using open-source and enterprise tools for extracting, processing, and standardizing unstructured data from PDFs and web pages. The goal is to develop a prototype AI application that automates data extraction, converts content into a structured Markdown format, and organizes files efficiently in an Amazon S3 storage system.

The project evaluates the trade-offs between open-source libraries like PyMuPDF, and BeautifulSoup versus an enterprise-grade service like Adobe PDF Services, comparing their performance, accuracy, and scalability. The extracted content is standardized using Docling and MarkItDown, with a comparison of their suitability for Markdown conversion.

A full pipeline is implemented, consisting of:

Data Extraction: Parsing PDFs and scraping web pages
Content Standardization: Formatting extracted text with Markdown
Cloud Storage: Organizing processed files in an S3 bucket
API Development: Providing endpoints via FastAPI
User Interface: A web-based interface built using Streamlit
Key Features
1. Data Extraction & Processing
PDF Parsing:
Open-source: PyMuPDF
Enterprise: Adobe Services
Web Scraping:
Open-source: BeautifulSoup
Enterprise: Apify
Comparison: Evaluation of tool accuracy, text quality, table/image preservation, and scalability
2. Standardization & Markdown Conversion
Docling: Specialized for structured linguistic processing
MarkItDown: More flexible for generic Markdown formatting
Comparison: Pros/cons of both approaches in content structuring and integration
3. File Organization & Storage (S3)
Naming Conventions: Organized by source (pdfs, webpages), type (raw, processed), and date
Metadata Tagging: Content type, processing status for easy retrieval
Best Practices: Encryption, access control, and lifecycle policies for storage optimization
4. API Development with FastAPI
/backend_fastapi/routes/fetch.py → defines a FastAPI endpoint that retrieves and returns the contents of a parsed file such as PDF or Web page from an Amazon S3 bucket. Fetches parsed markdown content from specific locations in an S3 bucket, with the location determined by the filename and the type of parser used.
/backend_fastapi/routes/upload.py → defines two FastAPI endpoints for processing and uploading PDF files and webpages.
 /pdf endpoint: Accepts a PDF file upload and a parser type. Based on the parser type ("Open Source" or "Enterprise"), it processes the PDF using different functions. It uploads the processed content to an S3 bucket and returns a success message with the S3 file path.
/backend_fastapi/main.py → handles PDF uploads, parsing, and fetching of parsed Markdown files from S3
The structure contains:
The /upload endpoints handle PDF uploads and processing
The /fetch endpoints retrieve parsed content
This setup provides a clear organization for the API's functionality, separating upload and fetch operations into distinct modules
5. Web Interface with Streamlit
User uploads PDFs or inputs webpage URLs
API triggers processing pipeline
Processed Markdown files can be downloaded
Deployed on Amazon Web Services for accessibility
Evaluation & Findings
The project documents a detailed comparison between open-source tools and enterprise solutions, highlighting factors such as:
1. Accuracy of text, table, and image extraction
2. Ease of integration into a larger pipeline
3. Cost-effectiveness and scalability for enterprise use

Proof of Concept (PoC):
This Proof of Concept (PoC) aims to validate the feasibility of automating document processing and standardization using AI-driven tools. The objective is to extract, process, and structure unstructured data from PDFs and web pages, converting them into a standardized Markdown format, and storing the processed content efficiently in an Amazon S3 storage system. The project evaluates open-source and enterprise-grade tools for data extraction, content transformation, and storage management.

Implementation Pipeline

1. Data Extraction & Processing

PDF Parsing

Open-source: PyMuPDF

Enterprise: Adobe PDF Services

Web Scraping

Open-source: BeautifulSoup

Enterprise: Apify

Comparison Metrics

Text extraction accuracy

Table and image preservation quality

Scalability and performance

Ease of integration

2. Standardization & Markdown Conversion

Docling: Specialized in structured linguistic processing

MarkItDown: Flexible for generic Markdown formatting

Comparison Metrics

Content structuring effectiveness

Markdown conversion accuracy

Ease of integration into the pipeline

3. File Organization & Storage (Amazon S3)

Naming Conventions: Files categorized by source (PDFs, web pages), type (raw, processed), and date

Metadata Tagging: Includes content type and processing status for easy retrieval

Storage Best Practices: Encryption, access control, and lifecycle policies for storage optimization

4. API Development (FastAPI)
The structure contains:
The /upload endpoints handle PDF uploads and processing
The /fetch endpoints retrieve parsed content

5. Web Interface (Streamlit)
Allows user to upload PDFs or input webpage URLs
Triggers processing pipeline via API calls
Provides downloadable processed Markdown files
Deployed on Amazon Web Services for accessibility

Evaluation & Findings
Performance Comparison
Feature	                        PyMuPDF	             Adobe PDF Services	         BeautifulSoup	     Apify
Text Extraction Accuracy	        High	               Very High	                 Moderate	          High
Table/Image Preservation	       Limited	              Advanced	                    N/A	            High
Scalability	                     Moderate	                 High	                    Moderate	         High
Ease of Integration	              High	                 Moderate	                    High	           High

Key Findings

Open-source solutions provide cost-effectiveness but require additional optimizations for accuracy and scalability.

Enterprise solutions offer higher accuracy and better integration but may have licensing costs.

For PDF extraction, Adobe PDF Services outperforms PyMuPDF in table and image extraction accuracy.

For web scraping, Apify provides a scalable, structured solution compared to BeautifulSoup.

Docling is useful for structured text, while MarkItDown is more flexible for general Markdown conversion.

A structured file organization strategy in S3 ensures efficient storage and retrieval of processed documents.

Conclusion & Next Steps

Enhance Open-source Solutions: Improve Apify and BeautifulSoup integration for better text and table extraction.

Optimize Pipeline Efficiency: Automate metadata tagging and processing using AI-based classification.

Deploy Prototype for Testing: Implement in a real-world environment and gather user feedback.

Evaluate Cost-Effectiveness: Assess long-term costs of enterprise tools versus enhanced open-source solutions.

This PoC demonstrates the viability of an AI-powered document processing pipeline and provides a foundation for scaling the solution in enterprise applications.

