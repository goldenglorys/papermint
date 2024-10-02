# import streamlit as st
# import os
# import subprocess
# import requests
# import tarfile
# import gzip
# import io
# import random
# import hashlib
# import shutil
# import re
# import json
# import pandas as pd
# from PIL import Image
# import pandoc
# from pandoc.types import *
# import tempfile
# import shutil
# import base64
# import time
# import concurrent.futures
# import threading
# import queue

# # Constants
# TEMP_DIR = "/tmp/papermint"
# ARXIV_CAT = "math"
# NUM_PAPERS = 100
# MAX_CONCURRENCY = 32
# FIGURE_PROB = 25
# EQUATION_PROB = 25
# MAX_SIZE = 2500000
# MIN_EQUATION_LENGTH = 5
# MAX_EQUATION_LENGTH = 120
# MIN_CAPTION_LENGTH = 20
# CHATGPT_TOPIC = "cybersecurity"
# QUIET = False
# SKIP_DOWNLOADING = False
# SKIP_REGENERATING_METADATA = False
# SKIP_EXTRACTING = False
# SKIP_FILTERING = False

# # Utility Functions
# def log(*args):
#     if not QUIET:
#         st.write(*args)

# def worker_wait():
#     while threading.active_count() > MAX_CONCURRENCY:
#         time.sleep(0.1)

# def rand_int(n=None):
#     if n is None:
#         return random.randint(0, 2**32 - 1)
#     else:
#         return random.randint(0, n - 1)

# def check_latex(latex_snippet):
#     try:
#         with tempfile.TemporaryDirectory() as tmpdir:
#             with open(os.path.join(tmpdir, "snippet.tex"), "w") as f:
#                 f.write(latex_snippet)
#             subprocess.run(["pdflatex", "-halt-on-error", "snippet.tex"], cwd=tmpdir, check=True)
#         return True
#     except subprocess.CalledProcessError:
#         return False

# # Main Procedures
# def download_papers():
#     if SKIP_DOWNLOADING:
#         return
#     log("Downloading papers...")
#     os.makedirs(os.path.join(TEMP_DIR, "images"), exist_ok=True)
#     os.makedirs(os.path.join(TEMP_DIR, "tex"), exist_ok=True)
#     os.makedirs(os.path.join(TEMP_DIR, "unknown_files"), exist_ok=True)

#     response = requests.get(f"https://arxiv.org/list/{ARXIV_CAT}/current?skip=0&show={NUM_PAPERS}")
#     urls = re.findall(r'href="/format/([^"]*)"', response.text)
#     urls = [f"https://arxiv.org/e-print/{url}" for url in urls]

#     def process_url(url):
#         worker_wait()
#         response = requests.get(url)
#         data = io.BytesIO(response.content)
#         try:
#             with tarfile.open(fileobj=data, mode="r") as tar:
#                 for member in tar.getmembers():
#                     if not member.isfile() or member.name.startswith(("..", "/")):
#                         continue
#                     ext = os.path.splitext(member.name)[1][1:].lower()
#                     if ext in ["jpg", "jpeg", "png", "tex"]:
#                         with open(os.path.join(TEMP_DIR, "images", f"{rand_int()}.{ext}"), "wb") as f:
#                             f.write(tar.extractfile(member).read())
#         except tarfile.ReadError:
#             data.seek(0)
#             with gzip.GzipFile(fileobj=data) as gz:
#                 with open(os.path.join(TEMP_DIR, "tex", f"{rand_int()}.tex"), "wb") as f:
#                     f.write(gz.read())

#     with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
#         executor.map(process_url, urls)

# def deduplicate():
#     if SKIP_DOWNLOADING:
#         return
#     log("Deduplicating files...")
#     for d in ["images", "tex"]:
#         hashes = {}
#         for filename in os.listdir(os.path.join(TEMP_DIR, d)):
#             filepath = os.path.join(TEMP_DIR, d, filename)
#             with open(filepath, "rb") as f:
#                 file_hash = hashlib.sha256(f.read()).hexdigest()
#             if file_hash in hashes:
#                 os.remove(filepath)
#             else:
#                 hashes[file_hash] = filepath

# def filter_large_files():
#     if SKIP_FILTERING:
#         return
#     log("Removing large files...")
#     os.makedirs(os.path.join(TEMP_DIR, "big_images"), exist_ok=True)
#     for filename in os.listdir(os.path.join(TEMP_DIR, "images")):
#         filepath = os.path.join(TEMP_DIR, "images", filename)
#         if os.path.getsize(filepath) > MAX_SIZE:
#             shutil.move(filepath, os.path.join(TEMP_DIR, "big_images", filename))

# def filter_diagrams():
#     if SKIP_FILTERING:
#         return
#     log("Filtering diagrams...")
#     os.makedirs(os.path.join(TEMP_DIR, "non_diagram_images"), exist_ok=True)
#     for filename in os.listdir(os.path.join(TEMP_DIR, "images")):
#         filepath = os.path.join(TEMP_DIR, "images", filename)
#         img = Image.open(filepath)
#         if img.getpixel((0, 0))[0] < 200 or img.getpixel((img.width - 1, img.height - 1))[0] < 200:
#             shutil.move(filepath, os.path.join(TEMP_DIR, "non_diagram_images", filename))

# def extract_captions():
#     if SKIP_EXTRACTING:
#         return
#     log("Extracting captions...")
#     captions = []
#     for filename in os.listdir(os.path.join(TEMP_DIR, "tex")):
#         with open(os.path.join(TEMP_DIR, "tex", filename), "r") as f:
#             content = f.read()
#         captions.extend(re.findall(r'\\caption\{([^\}]+)\}', content))
#     captions = [c for c in captions if len(c) >= MIN_CAPTION_LENGTH]
#     random.shuffle(captions)
#     with open(os.path.join(TEMP_DIR, "captions.txt"), "w") as f:
#         f.write("\n".join(captions))

# def extract_equations():
#     if SKIP_EXTRACTING:
#         return
#     log("Extracting equations...")
#     equations = []
#     for filename in os.listdir(os.path.join(TEMP_DIR, "tex")):
#         with open(os.path.join(TEMP_DIR, "tex", filename), "r") as f:
#             content = f.read()
#         equations.extend(re.findall(r'\$\$([^$]+)\$\$', content))
#     equations = [e for e in equations if MIN_EQUATION_LENGTH <= len(e) <= MAX_EQUATION_LENGTH]
#     random.shuffle(equations)
#     with open(os.path.join(TEMP_DIR, "equations.txt"), "w") as f:
#         f.write("\n".join(equations))

# def build_paper(url, output_file):
#     log("Building paper...")
#     if not url.endswith((".html", ".php")) and not re.match(r'http.*\/[^.]*$', url):
#         response = requests.get(url)
#         with open(os.path.join(TEMP_DIR, f"input.{url.split('.')[-1]}"), "wb") as f:
#             f.write(response.content)
#         url = os.path.join(TEMP_DIR, f"input.{url.split('.')[-1]}")

#     with open(os.path.join(TEMP_DIR, "metadata.md"), "r") as f:
#         metadata = f.read()

#     with open(os.path.join(TEMP_DIR, "captions.txt"), "r") as f:
#         captions = f.readlines()

#     with open(os.path.join(TEMP_DIR, "equations.txt"), "r") as f:
#         equations = f.readlines()

#     def process_line(line):
#         if rand_int(FIGURE_PROB) == 1:
#             line += f"\n\n![{random.choice(captions)}]({random.choice(os.listdir(os.path.join(TEMP_DIR, 'images')))})\n\n"
#         if rand_int(EQUATION_PROB) == 1:
#             line += f"\n\n{random.choice(equations)}\n\n"
#         return line

#     with open(url, "r") as f:
#         content = f.read()

#     content = "\n".join(process_line(line) for line in content.split("\n"))
#     content = metadata + content

#     with tempfile.TemporaryDirectory() as tmpdir:
#         with open(os.path.join(tmpdir, "output.md"), "w") as f:
#             f.write(content)
#         subprocess.run(["pandoc", "-f", "markdown", "-t", "latex", "-o", os.path.join(tmpdir, "output.tex"), os.path.join(tmpdir, "output.md")], check=True)
#         subprocess.run(["pdflatex", "-halt-on-error", "output.tex"], cwd=tmpdir, check=True)
#         shutil.copy(os.path.join(tmpdir, "output.pdf"), output_file)

# def main():
#     st.title("PaperMint: Automated Research Paper Generator")
#     url = st.text_input("Enter the URL or file path:")
#     output_file = st.text_input("Enter the output file name:")
#     if st.button("Generate Paper"):
#         with st.spinner("Generating paper..."):
#             download_papers()
#             deduplicate()
#             filter_large_files()
#             filter_diagrams()
#             extract_captions()
#             extract_equations()
#             build_paper(url, output_file)
#         st.success(f"Paper generated successfully! Saved as {output_file}")

# if __name__ == "__main__":
#     main()

# import streamlit as st
# import tempfile
# import os
# from mint.downloader import ArxivDownloader
# from mint.extractor import ContentExtractor
# from mint.generator import PaperGenerator
# from mint.converter import PDFConverter

# st.set_page_config(page_title="Academic Paper Generator", layout="wide")


# def main():
#     st.title("Automated Academic Paper Generator")

#     col1, col2 = st.columns(2)

#     with col1:
#         arxiv_category = st.selectbox(
#             "arXiv Category",
#             ["cs.AI", "cs.CL", "cs.CR", "math.CO", "physics.optics"],
#             help="Select the academic field for your paper",
#         )

#         num_papers = st.slider(
#             "Number of papers to analyze",
#             min_value=10,
#             max_value=100,
#             value=50,
#             help="More papers may lead to better content but slower generation",
#         )

#     with col2:
#         paper_title = st.text_input(
#             "Custom Paper Title (optional)", help="Leave blank for auto-generated title"
#         )

#         author_name = st.text_input(
#             "Author Name",
#             value="Dr. AI Generator",
#             help="Enter the author name for the paper",
#         )

#     if st.button("Generate Paper", type="primary"):
#         with st.spinner("Generating your academic paper..."):
#             try:
#                 # Step 1: Download papers
#                 with st.status("Downloading papers from arXiv...") as status:
#                     downloader = ArxivDownloader(arxiv_category, num_papers)
#                     papers = downloader.download()
#                     status.update(
#                         label="Papers downloaded successfully!", state="complete"
#                     )

#                 # Step 2: Extract content
#                 with st.status("Extracting content from papers...") as status:
#                     extractor = ContentExtractor(papers)
#                     content = extractor.extract()
#                     status.update(
#                         label="Content extracted successfully!", state="complete"
#                     )

#                 # Step 3: Generate paper
#                 with st.status("Generating new paper...") as status:
#                     generator = PaperGenerator(content)
#                     latex_content = generator.generate(
#                         title=paper_title, author=author_name
#                     )
#                     status.update(
#                         label="Paper generated successfully!", state="complete"
#                     )

#                 # Step 4: Convert to PDF
#                 with st.status("Converting to PDF...") as status:
#                     converter = PDFConverter(latex_content)
#                     pdf_path = converter.convert()
#                     status.update(label="PDF created successfully!", state="complete")

#                 # Display and download options
#                 with open(pdf_path, "rb") as pdf_file:
#                     st.download_button(
#                         "Download Generated Paper (PDF)",
#                         pdf_file,
#                         file_name="generated_paper.pdf",
#                         mime="application/pdf",
#                     )

#                 st.success("Paper generated successfully! Click above to download.")

#             except Exception as e:
#                 print(e)
#                 st.error(f"An error occurred: {str(e)}")


# if __name__ == "__main__":
#     main()


import streamlit as st
from mint import (
    download_papers,
    extract_captions,
    extract_equations,
    filter_images,
    generate_metadata,
    latex_template,
    pandoc_utils,
    requirements_check,
)


def main():
    st.title("Paperify: Turn Any Document into a Research Paper")

    # Sidebar options
    st.sidebar.header("Options")
    temp_dir = st.sidebar.text_input("Temporary Directory", "/tmp/paperify")
    arxiv_category = st.sidebar.text_input("arXiv Category", "math")
    num_papers = st.sidebar.number_input("Number of Papers", value=100)
    max_concurrency = st.sidebar.number_input("Max Concurrency", value=32)
    figure_prob = st.sidebar.number_input("Figure Frequency", value=25)
    equation_prob = st.sidebar.number_input("Equation Frequency", value=25)
    max_size = st.sidebar.number_input("Max Image Size (bytes)", value=2500000)
    min_equation_length = st.sidebar.number_input("Min Equation Length", value=5)
    max_equation_length = st.sidebar.number_input("Max Equation Length", value=120)
    min_caption_length = st.sidebar.number_input("Min Caption Length", value=20)
    chatgpt_token = st.sidebar.text_input("ChatGPT Token")
    chatgpt_topic = st.sidebar.text_input("ChatGPT Topic", "cybersecurity")
    quiet = st.sidebar.checkbox("Quiet Mode")
    skip_downloading = st.sidebar.checkbox("Skip Downloading")
    skip_extracting = st.sidebar.checkbox("Skip Extracting")
    skip_metadata = st.sidebar.checkbox("Skip Metadata")
    skip_filtering = st.sidebar.checkbox("Skip Filtering")

    # Main content
    st.header("Upload Document or Enter URL")
    input_type = st.radio("Choose input type", ["Upload File", "Enter URL"])

    if input_type == "Upload File":
        uploaded_file = st.file_uploader(
            "Choose a file", type=["pdf", "docx", "md", "html", "txt"]
        )
        if uploaded_file is not None:
            with open(f"{temp_dir}/input_file", "wb") as f:
                f.write(uploaded_file.getbuffer())
            input_file = f"{temp_dir}/input_file"
    else:
        input_url = st.text_input("Enter URL")
        if input_url:
            input_file = input_url

    if st.button("Generate Paper"):
        if input_type == "Upload File" and uploaded_file is None:
            st.error("Please upload a file or enter a URL.")
            return
        if input_type == "Enter URL" and not input_url:
            st.error("Please enter a URL.")
            return

        # Check requirements
        requirements_check.check_requirements()

         # Dump LaTeX template
        latex_template.dump_latex_template(temp_dir)

        # Download papers
        if not skip_downloading:
            download_papers.download_papers(
                temp_dir, arxiv_category, num_papers, max_concurrency
            )

        # Filter images
        if not skip_filtering:
            filter_images.filter_large_files(temp_dir, max_size)
            filter_images.filter_diagrams(temp_dir)

        # Extract captions and equations
        if not skip_extracting:
            extract_captions.extract_captions(
                temp_dir, min_caption_length, max_concurrency, quiet
            )
            extract_equations.extract_equations(
                temp_dir,
                min_equation_length,
                max_equation_length,
                max_concurrency,
                quiet,
            )

        # Generate metadata
        if not skip_metadata:
            generate_metadata.generate_metadata(temp_dir, chatgpt_token, chatgpt_topic)

        # Build paper
        output_file = f"{temp_dir}/output.pdf"
        pandoc_utils.build_paper(
            input_file, output_file, temp_dir, figure_prob, equation_prob, quiet
        )

        # Display the generated paper
        with open(output_file, "rb") as f:
            st.download_button(
                "Download Generated Paper", f, file_name="generated_paper.pdf"
            )


if __name__ == "__main__":
    main()
