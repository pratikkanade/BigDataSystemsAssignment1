from pathlib import Path
import streamlit as st
import requests

st.title("Data Extractor and Retriever")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Services", ["Extraction", "Retrieval"])


# Set FastAPI URL
API_BASE_URL = "http://127.0.0.1:8000"

if page == "Extraction":

    st.header("Extract Content")

    # Sidebar input selection
    input_source = st.selectbox("Select Input Source", ["PDF Upload", "Web Page URL"])

    if input_source == "PDF Upload":
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        extraction_method = st.selectbox(
            "Select Extraction Method of File",
            ["Adobe PDF Services (Enterprise)", "PyMuPDF (Open Source)"]
        )

    elif input_source == "Web Page URL":
        url = st.text_input("Enter Web Page URL")

        extraction_method = st.selectbox(
            "Select Extraction Method of File",
            ["Adobe PDF Services (Enterprise)", "Beautiful Soup (Open Source)"]
        )


    if st.button("Extract Data"):
        if input_source == "PDF Upload" and uploaded_file:
            st.info("Uploading PDF for processing...")
            files = {"file": uploaded_file}


            try:
                #files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                params = {"parser_type": extraction_method}
                response = requests.post(f"{API_BASE_URL}/upload/pdf", files=files, params=params)


                if response.status_code == 200:
                    st.success("File uploaded and parsed successfully!")
                    #st.write(f"File URL: {response.json().get('file_url')}")
                else:
                    #st.error(response.json()["detail"])
                    st.error(f"Error: {response.json()['detail']}")

            except Exception as e:
                st.error(f"Error during PDF upload: {str(e)}")

        elif input_source == "Web Page URL" and url:
            st.info("Processing Web Page...")

            parser_type = "Open Source"
            params = {"url": url, "parser_type": parser_type}

            response = requests.post(f"{API_BASE_URL}/upload/webpage", params=params)

            if response.status_code == 200:
                st.success("Web page processed successfully!")
            else:
                #st.error(response.json()["detail"])
                st.error(f"Error: {response.json()['detail']}")

        else:
            st.error("Please provide valid input before extraction.")

else:

    # Fetch Parsed Content
    st.header("Fetch Extracted Content")
    filename = st.text_input("Enter file name to fetch parsed content")

    extraction_method = st.selectbox(
            "Select Extraction Method of File",
            ["Adobe PDF Services (Enterprise)", "PyMuPDF (Open Source)", "Beautiful Soup (Open Source)"]
        )

    if st.button("Fetch Extracted Content"):
        params = {"filename": filename, "parser_type": extraction_method}
        response = requests.get(f"{API_BASE_URL}/fetch/file", params=params)

        if response.status_code == 200:
            st.success("File Fetched Successfully!")
            data = response.json()

            # Display markdown content
            #st.text_area("Extracted Content", response.text, height=300)
            st.markdown(data)

            st.download_button(
                label="Download Markdown",
                data=data,
                file_name=f"content.md",
                mime="text/markdown"
            )

        else:
            st.error(f"Error: Status Code {response.status_code}")

            
