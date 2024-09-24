import streamlit as st
import os
import subprocess
import requests
import tarfile
import gzip
import io
import random
import hashlib
import shutil
import re
import json
import pandas as pd
from PIL import Image
import pandoc
from pandoc.types import *
import tempfile
import shutil
import base64
import time
import concurrent.futures
import threading
import queue

# Constants
TEMP_DIR = "/tmp/papermint"
ARXIV_CAT = "math"
NUM_PAPERS = 100
MAX_CONCURRENCY = 32
FIGURE_PROB = 25
EQUATION_PROB = 25
MAX_SIZE = 2500000
MIN_EQUATION_LENGTH = 5
MAX_EQUATION_LENGTH = 120
MIN_CAPTION_LENGTH = 20
CHATGPT_TOPIC = "cybersecurity"
QUIET = False
SKIP_DOWNLOADING = False
SKIP_REGENERATING_METADATA = False
SKIP_EXTRACTING = False
SKIP_FILTERING = False

# Utility Functions
def log(*args):
    if not QUIET:
        st.write(*args)

def worker_wait():
    while threading.active_count() > MAX_CONCURRENCY:
        time.sleep(0.1)

def rand_int(n=None):
    if n is None:
        return random.randint(0, 2**32 - 1)
    else:
        return random.randint(0, n - 1)

def check_latex(latex_snippet):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "snippet.tex"), "w") as f:
                f.write(latex_snippet)
            subprocess.run(["pdflatex", "-halt-on-error", "snippet.tex"], cwd=tmpdir, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# Main Procedures
def download_papers():
    if SKIP_DOWNLOADING:
        return
    log("Downloading papers...")
    os.makedirs(os.path.join(TEMP_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(TEMP_DIR, "tex"), exist_ok=True)
    os.makedirs(os.path.join(TEMP_DIR, "unknown_files"), exist_ok=True)

    response = requests.get(f"https://arxiv.org/list/{ARXIV_CAT}/current?skip=0&show={NUM_PAPERS}")
    urls = re.findall(r'href="/format/([^"]*)"', response.text)
    urls = [f"https://arxiv.org/e-print/{url}" for url in urls]

    def process_url(url):
        worker_wait()
        response = requests.get(url)
        data = io.BytesIO(response.content)
        try:
            with tarfile.open(fileobj=data, mode="r") as tar:
                for member in tar.getmembers():
                    if not member.isfile() or member.name.startswith(("..", "/")):
                        continue
                    ext = os.path.splitext(member.name)[1][1:].lower()
                    if ext in ["jpg", "jpeg", "png", "tex"]:
                        with open(os.path.join(TEMP_DIR, "images", f"{rand_int()}.{ext}"), "wb") as f:
                            f.write(tar.extractfile(member).read())
        except tarfile.ReadError:
            data.seek(0)
            with gzip.GzipFile(fileobj=data) as gz:
                with open(os.path.join(TEMP_DIR, "tex", f"{rand_int()}.tex"), "wb") as f:
                    f.write(gz.read())

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        executor.map(process_url, urls)

def deduplicate():
    if SKIP_DOWNLOADING:
        return
    log("Deduplicating files...")
    for d in ["images", "tex"]:
        hashes = {}
        for filename in os.listdir(os.path.join(TEMP_DIR, d)):
            filepath = os.path.join(TEMP_DIR, d, filename)
            with open(filepath, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            if file_hash in hashes:
                os.remove(filepath)
            else:
                hashes[file_hash] = filepath

def filter_large_files():
    if SKIP_FILTERING:
        return
    log("Removing large files...")
    os.makedirs(os.path.join(TEMP_DIR, "big_images"), exist_ok=True)
    for filename in os.listdir(os.path.join(TEMP_DIR, "images")):
        filepath = os.path.join(TEMP_DIR, "images", filename)
        if os.path.getsize(filepath) > MAX_SIZE:
            shutil.move(filepath, os.path.join(TEMP_DIR, "big_images", filename))

def filter_diagrams():
    if SKIP_FILTERING:
        return
    log("Filtering diagrams...")
    os.makedirs(os.path.join(TEMP_DIR, "non_diagram_images"), exist_ok=True)
    for filename in os.listdir(os.path.join(TEMP_DIR, "images")):
        filepath = os.path.join(TEMP_DIR, "images", filename)
        img = Image.open(filepath)
        if img.getpixel((0, 0))[0] < 200 or img.getpixel((img.width - 1, img.height - 1))[0] < 200:
            shutil.move(filepath, os.path.join(TEMP_DIR, "non_diagram_images", filename))

def extract_captions():
    if SKIP_EXTRACTING:
        return
    log("Extracting captions...")
    captions = []
    for filename in os.listdir(os.path.join(TEMP_DIR, "tex")):
        with open(os.path.join(TEMP_DIR, "tex", filename), "r") as f:
            content = f.read()
        captions.extend(re.findall(r'\\caption\{([^\}]+)\}', content))
    captions = [c for c in captions if len(c) >= MIN_CAPTION_LENGTH]
    random.shuffle(captions)
    with open(os.path.join(TEMP_DIR, "captions.txt"), "w") as f:
        f.write("\n".join(captions))

def extract_equations():
    if SKIP_EXTRACTING:
        return
    log("Extracting equations...")
    equations = []
    for filename in os.listdir(os.path.join(TEMP_DIR, "tex")):
        with open(os.path.join(TEMP_DIR, "tex", filename), "r") as f:
            content = f.read()
        equations.extend(re.findall(r'\$\$([^$]+)\$\$', content))
    equations = [e for e in equations if MIN_EQUATION_LENGTH <= len(e) <= MAX_EQUATION_LENGTH]
    random.shuffle(equations)
    with open(os.path.join(TEMP_DIR, "equations.txt"), "w") as f:
        f.write("\n".join(equations))

def build_paper(url, output_file):
    log("Building paper...")
    if not url.endswith((".html", ".php")) and not re.match(r'http.*\/[^.]*$', url):
        response = requests.get(url)
        with open(os.path.join(TEMP_DIR, f"input.{url.split('.')[-1]}"), "wb") as f:
            f.write(response.content)
        url = os.path.join(TEMP_DIR, f"input.{url.split('.')[-1]}")

    with open(os.path.join(TEMP_DIR, "metadata.md"), "r") as f:
        metadata = f.read()

    with open(os.path.join(TEMP_DIR, "captions.txt"), "r") as f:
        captions = f.readlines()

    with open(os.path.join(TEMP_DIR, "equations.txt"), "r") as f:
        equations = f.readlines()

    def process_line(line):
        if rand_int(FIGURE_PROB) == 1:
            line += f"\n\n![{random.choice(captions)}]({random.choice(os.listdir(os.path.join(TEMP_DIR, 'images')))})\n\n"
        if rand_int(EQUATION_PROB) == 1:
            line += f"\n\n{random.choice(equations)}\n\n"
        return line

    with open(url, "r") as f:
        content = f.read()

    content = "\n".join(process_line(line) for line in content.split("\n"))
    content = metadata + content

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "output.md"), "w") as f:
            f.write(content)
        subprocess.run(["pandoc", "-f", "markdown", "-t", "latex", "-o", os.path.join(tmpdir, "output.tex"), os.path.join(tmpdir, "output.md")], check=True)
        subprocess.run(["pdflatex", "-halt-on-error", "output.tex"], cwd=tmpdir, check=True)
        shutil.copy(os.path.join(tmpdir, "output.pdf"), output_file)

def main():
    st.title("PaperMint: Automated Research Paper Generator")
    url = st.text_input("Enter the URL or file path:")
    output_file = st.text_input("Enter the output file name:")
    if st.button("Generate Paper"):
        with st.spinner("Generating paper..."):
            download_papers()
            deduplicate()
            filter_large_files()
            filter_diagrams()
            extract_captions()
            extract_equations()
            build_paper(url, output_file)
        st.success(f"Paper generated successfully! Saved as {output_file}")

if __name__ == "__main__":
    main()