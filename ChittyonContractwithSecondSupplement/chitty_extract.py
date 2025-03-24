import extract_citations
import fitz
import re
import os
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json


def get_citations_from_docx(docx_path):
    citations = []
    if os.path.exists(docx_path):
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            citation_match = re.findall(r"\[\d+\]", para.text)
            if citation_match:
                citations.extend(citation_match)
    return citations


def extract_text_to_markdown(pdf_path, markdown_path):
    doc = fitz.open(pdf_path)
    sections = {}
    current_section = None
    current_chapter = None
    current_subsection = None

    with open(markdown_path, "w", encoding="utf-8") as md_file:
        for page in doc:
            text = page.get_text("text")
            lines = text.split("\n")

            for line in lines:
                chapter_match = re.match(r"(Chapter\s+\d+.*)", line.strip())
                if chapter_match:
                    current_chapter = chapter_match.group(1)
                    md_file.write(f"# {current_chapter}\n\n")

                section_match = re.match(r"(Section\s+\d+\.\s+-\s+.*)", line.strip())
                if section_match:
                    current_section = section_match.group(1)
                    sections[current_section] = {
                        "text": "",
                        "chapter": current_chapter,
                        "subsections": {},
                    }
                    current_subsection = None
                    md_file.write(f"## {current_section}\n\n")

                subsection_match = re.match(r"(\d{2}-\d{3})", line.strip())
                if subsection_match:
                    if current_section:
                        current_subsection = subsection_match.group(1)
                        sections[current_section]["subsections"][current_subsection] = ""
                        md_file.write(f"### {current_subsection}\n\n")
                    else:
                        print(f"Warning: Subsection {subsection_match.group(1)} found without a section. Skipping.")
                        current_subsection = None

                elif current_section:
                    if current_subsection:
                        sections[current_section]["subsections"][current_subsection] += (line.strip() + " ")
                    else:
                        sections[current_section]["text"] += line.strip() + " "
                    md_file.write(line.strip() + " ")

            md_file.write("\n\n")

    return sections


def chunk_text_chitty(pdf_folder_path, docx_folder_path):
    os.makedirs(pdf_folder_path, exist_ok=True)
    os.makedirs(docx_folder_path, exist_ok=True)

    pdf_files = [f for f in os.listdir(pdf_folder_path) if f.endswith(".pdf")]

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder_path, pdf_file)
        base_name = os.path.splitext(pdf_file)[0]
        markdown_path = os.path.join(pdf_folder_path, f"{base_name}.md")
        docx_path = os.path.join(docx_folder_path, f"{base_name}.docx")
        
        # Extract citations from docx file
        citations = extract_citations(docx_path)
        
        # Extract text and save to markdown file
        sections = extract_text_to_markdown(pdf_path, markdown_path)
        
        # --- Commented out the following chunking and JSON saving part ---
        # chunks = chunk_text_recursive(sections, 800, base_name, citations)
        # all_chunks.extend(chunks)
        # sample_output = all_chunks[:20] + all_chunks[-5:] if len(all_chunks) > 10 else all_chunks
        # with open(r"/workspaces/Cleaning-Extraction/chitty_chunks.json", "w", encoding="utf-8") as json_file:
        #     json.dump(sample_output, json_file, indent=4, ensure_ascii=False)

    print("Extraction to Markdown completed.")

chunk_text_chitty(r"Chitty on Contract with Second Supplement/Chitty Chapters 1- 30", r"Chitty on Contract with Second Supplement/docs/docs")