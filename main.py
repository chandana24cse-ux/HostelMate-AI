from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from dotenv import load_dotenv
from groq import Groq

import shutil
import os
import re


# Load environment variables
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# Create FastAPI app
app = FastAPI()


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Folder for uploaded PDFs
UPLOAD_FOLDER = "backend/uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# Store handbook pages
handbook_pages = []


# Home route
@app.get("/")
def home():

    return {
        "message": "Hostel Handbook Assistant backend is running!"
    }


# Upload handbook
@app.post("/upload-handbook")
async def upload_handbook(
    file: UploadFile = File(...)
):

    global handbook_pages

    # Check PDF
    if not file.filename.lower().endswith(".pdf"):

        return {
            "message": "Please upload a PDF file."
        }

    # Save PDF
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Read PDF
    reader = PdfReader(file_path)

    # Clear previous handbook
    handbook_pages = []

    # Extract each page separately
    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        page_text = page.extract_text()

        if page_text:

            handbook_pages.append({
                "page": page_number,
                "text": page_text
            })

    return {
        "message": "Handbook uploaded and read successfully!",
        "filename": file.filename,
        "pages": len(reader.pages)
    }


# Ask a question
@app.post("/ask")
async def ask_question(data: dict):

    global handbook_pages

    # Get question
    question = data.get(
        "question",
        ""
    ).strip()

    # Check question
    if not question:

        return {
            "answer": "Please enter a question.",
            "source": ""
        }

    # Check handbook
    if not handbook_pages:

        return {
            "answer": "Please upload the hostel handbook first.",
            "source": ""
        }

    try:

        # Combine pages with page numbers
        handbook_content = ""

        for item in handbook_pages:

            handbook_content += (
                f"\n\n--- PAGE {item['page']} ---\n"
            )

            handbook_content += item["text"]

        # Create prompt
        prompt = f"""
You are the Hostel Handbook Assistant.

Answer the student's question ONLY using the
information provided in the hostel handbook.

IMPORTANT:
1. Do not invent any information.
2. If the answer is not present, say:
"I couldn't find that information in the uploaded hostel handbook."
3. At the end of your answer, write:
SOURCE_PAGE: X

Replace X with the page number containing the
information used to answer the question.

If information comes from multiple pages, write:
SOURCE_PAGE: X, Y

Keep the answer simple and clear.

HOSTEL HANDBOOK:
----------------
{handbook_content}

STUDENT QUESTION:
-----------------
{question}
"""

        # Ask Groq
        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2
        )

        # Get AI response
        full_answer = response.choices[0].message.content

        # Find SOURCE_PAGE
        source_match = re.search(
            r"SOURCE_PAGE:\s*([0-9,\s]+)",
            full_answer,
            re.IGNORECASE
        )

        if source_match:

            source_pages = source_match.group(1).strip()

            # Remove source line from answer
            answer = re.sub(
                r"SOURCE_PAGE:\s*[0-9,\s]+",
                "",
                full_answer,
                flags=re.IGNORECASE
            ).strip()

            source = (
                f"📄 Source: Hostel Handbook "
                f"— Page {source_pages}"
            )

        else:

            answer = full_answer

            source = (
                "📄 Source: Hostel Handbook"
            )

        return {
            "answer": answer,
            "source": source
        }

    except Exception as e:

        print(
            "Groq error:",
            e
        )

        return {
            "answer": f"Groq error: {str(e)}",
            "source": ""
        }