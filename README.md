## Context-Aware AI Chatbot with Private Document Retrieval

This project is a private, local, AI assistant designed for organizations to build their own chatbot based on internal documents. It uses a Retrieval-Augmented Generation (RAG) architecture, combining document search with a LLM for smart, context-aware answers.

---
##  Key Features
-  Ask questions based on your own internal PDF documents
-  Uses RAG (Retrieval-Augmented Generation) to provide accurate answers
-  Runs locally – no data is sent to the cloud
-  No coding skills required to use
-  Supports adding metadata like expert contacts via Excel
-  Simple web interface using Streamlit

---
##  How It Works
1. Documents (PDFs) are split into smaller parts.
2. Text chunks are converted into embeddings and stored in a local vector database using Chroma.
3. When a user asks a question, the system retrieves the most relevant chunks and uses an LLM to generate a natural-language answer.

---
##  How to Use
1. Add your PDF files, to the project folder.
   - Example: `Company-Policy.pdf`, `Employee-Handbook.pdf`

2. (Optional) Add an Excel file with expert info or additional metadata.
   - Example: `your-data.xlsx`

3. Run the setup script once to process your documents:
   
   python vector.py

4. Launch the chatbot:
streamlit run app.py

---
## Customization
You can update:
    The list of PDF files in vector.py
    The template and chatbot behavior in app.py
    Logo, branding, and topics covered

---
## Installation
Install all required libraries with:
    pip install -r requirements.txt

---
## 


