import os
import sys
import shutil
import time
import tempfile
import hashlib
import random
import re
import requests
import subprocess
import unicodedata
import multiprocessing
from PIL import Image
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape
from argparse import ArgumentParser

# Constants and Variables
TEMP_DIR = "/tmp/paperify"
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
CHATGPT_TOKEN = None


def echo(*args):
    if args:
        print(*args)
    else:
        print()


def error(*args):
    print("\033[1m\033[31mError:\033[m", *args, file=sys.stderr)


def error_exit(*args):
    error(*args)
    sys.exit(1)


def log(*args):
    if not QUIET:
        print(*args, file=sys.stderr)


def worker_wait():
    while len(multiprocessing.active_children()) >= MAX_CONCURRENCY:
        time.sleep(0.1)


def rand_int(n=None):
    if n is None:
        return int.from_bytes(os.urandom(4), "big")
    else:
        return int.from_bytes(os.urandom(4), "big") % n


def check_latex(snippet):
    # Implement LaTeX compilation check
    pass


def usage():
    # Implement usage information
    pass


def args_required(expecting, *args):
    if len(args) <= expecting:
        error(f"{args[0]} requires {expecting} argument{'s' if expecting >= 2 else ''}")
        usage()
        sys.exit(1)


def check_requirements():
    required_packages = ["pandoc", "requests", "PIL", "PyPDF2", "pylatex"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            error_exit(f"{package} must be installed for {sys.argv[0]} to run.")


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--temp-dir", default=TEMP_DIR)
    parser.add_argument("--from-format", default=None)
    parser.add_argument("--arxiv-category", default=ARXIV_CAT)
    parser.add_argument("--num-papers", type=int, default=NUM_PAPERS)
    parser.add_argument("--max-concurrency", type=int, default=MAX_CONCURRENCY)
    parser.add_argument("--figure-frequency", type=int, default=FIGURE_PROB)
    parser.add_argument("--equation-frequency", type=int, default=EQUATION_PROB)
    parser.add_argument("--max-size", type=int, default=MAX_SIZE)
    parser.add_argument("--min-equation-length", type=int, default=MIN_EQUATION_LENGTH)
    parser.add_argument("--max-equation-length", type=int, default=MAX_EQUATION_LENGTH)
    parser.add_argument("--min-caption-length", type=int, default=MIN_CAPTION_LENGTH)
    parser.add_argument("--chatgpt-token", default=None)
    parser.add_argument("--chatgpt-topic", default=CHATGPT_TOPIC)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--skip-downloading", action="store_true")
    parser.add_argument("--skip-extracting", action="store_true")
    parser.add_argument("--skip-metadata", action="store_true")
    parser.add_argument("--skip-filtering", action="store_true")
    parser.add_argument("url_or_path")
    parser.add_argument("output_file")
    args = parser.parse_args()
    return args


def open_temp_dir():
    log(f"Creating directory {TEMP_DIR} for intermediate work...")
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.chdir(TEMP_DIR)


def dump_latex_template():
    with open("template.tex", "w") as f:
        f.write(
            r"""
        \documentclass{article}
        \usepackage{amsmath, amssymb, amsfonts}
        \usepackage{graphicx}
        \begin{document}
        \title{Title}
        \author{Author}
        \maketitle
        \section{Introduction}
        \end{document}
        """
        )


def dump_yaml_template():
    if SKIP_REGENERATING_METADATA and os.path.exists("metadata.md"):
        return
    elif CHATGPT_TOKEN and not SKIP_REGENERATING_METADATA:
        log("Generating paper metadata with ChatGPT...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {CHATGPT_TOKEN}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a JSON generator..."},
                    {"role": "user", "content": f"Generate a valid JSON object..."},
                ],
            },
        )
        metadata = response.json()["choices"][0]["message"]["content"]
        with open("metadata.json", "w") as f:
            f.write(metadata)
        log(f"Generated metadata for '{metadata['paper_title']}'")
        with open("metadata.md", "w") as f:
            f.write(
                f"""
            ---
            documentclass: IEEEtran
            classoption:
              - journal
              - letterpaper
            journal: |
              {metadata['journal_name']}
            title: |
              {metadata['paper_title']}
            thanks: |
              {metadata['thanks']}
            author: 
              - |
                {metadata['author_name']}

                {metadata['author_organization']}

                [{metadata['author_email']}](mailto:{metadata['author_email']})
            abstract: |
              {metadata['paper_abstract']}
            ...
            """
            )
    else:
        with open("metadata.md", "w") as f:
            f.write(
                """
            ---
            documentclass: IEEEtran
            classoption:
              - journal
              - letterpaper
            journal: |
              International Journal of Cybersecurity Research (IJCR)
            title: |
              Adaptive Threat Intelligence Framework for Proactive Cyber Defense
            thanks: |
              The authors would like to express their gratitude to the Cybersecurity
              Research Institute (CRI) for providing valuable resources and support
              during the research process
            author: 
              - |
                Emily Collins, PhD

                Cybersecurity Institute for Advanced Research (CIAR)

                [`ecollins@ciar.org`](mailto:ecollins@ciar.org)
            abstract: |
              In this paper, we present a novel approach for detecting advanced persistent
              threats (APTs) using deep learning techniques. APTs pose significant
              challenges to traditional security systems due to their stealthy and
              persistent nature. Our proposed method leverages a combination of
              convolutional neural networks and recurrent neural networks to analyze
              large-scale network traffic data. We introduce a novel attention mechanism
              that identifies subtle patterns in the data, enabling the detection of APTs
              with high accuracy. Experimental results on real-world datasets demonstrate
              the effectiveness of our approach in identifying previously unknown APTs
              while minimizing false positives. The framework offers a promising solution
              for enhancing the security posture of modern network infrastructures against
              sophisticated cyber threats.
            ...
            """
            )


def download_papers():
    if SKIP_DOWNLOADING:
        return
    log("Downloading papers...")
    os.makedirs("images", exist_ok=True)
    os.makedirs("tex", exist_ok=True)
    os.makedirs("unknown_files", exist_ok=True)
    response = requests.get(
        f"https://arxiv.org/list/{ARXIV_CAT}/current?skip=0&show={NUM_PAPERS}"
    )
    urls = re.findall(r'href="/format/[^"]*"', response.text)
    urls = [f"https://arxiv.org/e-print/{url[14:-1]}" for url in urls]
    for url in urls:
        worker_wait()
        response = requests.get(url)
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_file.flush()
            os.system(f"tar -xf {tmp_file.name} -C images/")
            os.remove(tmp_file.name)
    for root, dirs, files in os.walk("images"):
        for file in files:
            if file.endswith(".tex"):
                shutil.move(os.path.join(root, file), "tex/")


def deduplicate():
    if SKIP_DOWNLOADING:
        return
    for d in os.listdir():
        if os.path.isdir(d):
            log(f"Deduplicating {os.path.abspath(d)}...")
            hashes = {}
            for file in os.listdir(d):
                file_path = os.path.join(d, file)
                with open(file_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    if file_hash in hashes:
                        os.remove(file_path)
                    else:
                        hashes[file_hash] = file_path


def filter_large_files():
    if SKIP_FILTERING:
        return
    log(f"Removing images greater than {MAX_SIZE} bytes...")
    os.makedirs("big_images", exist_ok=True)
    for file in os.listdir("images"):
        file_path = os.path.join("images", file)
        if os.path.getsize(file_path) > MAX_SIZE:
            shutil.move(file_path, "big_images/")


def filter_diagrams():
    if not Image or SKIP_FILTERING:
        return
    log("Removing non-diagram images...")
    os.makedirs("non_diagram_images", exist_ok=True)
    total = len(os.listdir("images"))
    num = 0
    for file in os.listdir("images"):
        worker_wait()
        file_path = os.path.join("images", file)
        img = Image.open(file_path)
        if (
            img.getpixel((0, 0))[0] < 250
            or img.getpixel((img.width - 1, img.height - 1))[0] < 250
        ):
            shutil.move(file_path, "non_diagram_images/")
        num += 1
        if not QUIET:
            print(f"\r{100 * num // total}% complete...", end="", file=sys.stderr)
    print()


def extract_captions():
    if SKIP_EXTRACTING:
        return
    log("Generating and testing figure captions...")
    with open("unchecked_captions.txt", "w") as f:
        for file in os.listdir("tex"):
            with open(os.path.join("tex", file), "r") as tex_file:
                f.write("\n".join(re.findall(r"\\caption{[^{}]+}", tex_file.read())))
    with open("unchecked_captions.txt", "r") as f:
        captions = f.read().splitlines()
    captions = list(set(captions))
    captions = [caption for caption in captions if len(caption) >= MIN_CAPTION_LENGTH]
    random.shuffle(captions)
    with open("captions.txt", "w") as f:
        for caption in captions:
            if check_latex(caption):
                f.write(caption + "\n")


def extract_equations():
    if SKIP_EXTRACTING:
        return
    log("Generating and testing equations...")
    with open("equations.txt", "w") as f:
        for file in os.listdir("tex"):
            with open(os.path.join("tex", file), "r") as tex_file:
                equations = re.findall(r"\$\$.*?\$\$", tex_file.read())
                equations = [
                    eq
                    for eq in equations
                    if MIN_EQUATION_LENGTH <= len(eq) <= MAX_EQUATION_LENGTH
                ]
                random.shuffle(equations)
                for eq in equations:
                    if check_latex(eq):
                        f.write(eq + "\n")


def build_paper():
    if not re.search(r"\.(html|php)$", ORIGINAL_FILE_URL) and not re.search(
        r"http.*\/[^.]*$", ORIGINAL_FILE_URL
    ):
        log("Downloading input file...")
        response = requests.get(ORIGINAL_FILE_URL)
        with open(f"input.{FROM_FORMAT}", "wb") as f:
            f.write(response.content)
        ORIGINAL_FILE_URL = f"input.{FROM_FORMAT}"

    log("Building paper...")
    with open("output.md", "w") as f:
        f.write(
            subprocess.check_output(
                [
                    "pandoc",
                    "--from",
                    FROM_FORMAT,
                    "--to",
                    "gfm",
                    "--wrap",
                    "none",
                    "--extract-media",
                    "media",
                    ORIGINAL_FILE_URL,
                ]
            ).decode("utf-8")
        )

    with open("output.md", "r") as f:
        content = f.read()
    content = re.sub(r"cover\.\(jpe?g\|png\)", "", content)
    content = re.sub(r"!\[.*\](.*\.\(svg\|gif\))", "", content)
    lines = content.splitlines()
    with open("output.md", "w") as f:
        for line in lines:
            f.write(line + "\n")
            if rand_int(FIGURE_PROB) == 1:
                with open("captions.txt", "r") as captions_file:
                    captions = captions_file.read().splitlines()
                caption = random.choice(captions)
                with open("images", "r") as images_file:
                    images = images_file.read().splitlines()
                image = random.choice(images)
                f.write(f"\n\n![{caption}]({image})\n\n")
            elif rand_int(EQUATION_PROB) == 1:
                with open("equations.txt", "r") as equations_file:
                    equations = equations_file.read().splitlines()
                equation = random.choice(equations)
                f.write(f"\n\n{equation}\n\n")

    with open("output.md", "r") as f:
        content = f.read()
    content = (
        unicodedata.normalize("NFKD", content).encode("ascii", "ignore").decode("ascii")
    )
    with open("output.md", "w") as f:
        f.write(content)

    with open("metadata.md", "r") as f:
        metadata = f.read()
    with open("output.md", "r") as f:
        content = f.read()
    with open("output.tex", "w") as f:
        f.write(
            subprocess.check_output(
                [
                    "pandoc",
                    "--from",
                    "markdown",
                    "--to",
                    "latex",
                    "--template",
                    "template.tex",
                    "-",
                    metadata + content,
                ]
            ).decode("utf-8")
        )

    os.system("pdflatex output.tex")


def main():
    check_requirements()
    args = parse_args()
    global TEMP_DIR, FROM_FORMAT, ARXIV_CAT, NUM_PAPERS, MAX_CONCURRENCY, FIGURE_PROB, EQUATION_PROB, MAX_SIZE, MIN_EQUATION_LENGTH, MAX_EQUATION_LENGTH, MIN_CAPTION_LENGTH, CHATGPT_TOPIC, QUIET, SKIP_DOWNLOADING, SKIP_REGENERATING_METADATA, SKIP_EXTRACTING, SKIP_FILTERING, ORIGINAL_FILE_URL, OUTPUT_FILE
    TEMP_DIR = args.temp_dir
    FROM_FORMAT = args.from_format
    ARXIV_CAT = args.arxiv_category
    NUM_PAPERS = args.num_papers
    MAX_CONCURRENCY = args.max_concurrency
    FIGURE_PROB = args.figure_frequency
    EQUATION_PROB = args.equation_frequency
    MAX_SIZE = args.max_size
    MIN_EQUATION_LENGTH = args.min_equation_length
    MAX_EQUATION_LENGTH = args.max_equation_length
    MIN_CAPTION_LENGTH = args.min_caption_length
    CHATGPT_TOPIC = args.chatgpt_topic
    QUIET = args.quiet
    SKIP_DOWNLOADING = args.skip_downloading
    SKIP_REGENERATING_METADATA = args.skip_metadata
    SKIP_EXTRACTING = args.skip_extracting
    SKIP_FILTERING = args.skip_filtering
    ORIGINAL_FILE_URL = args.url_or_path
    OUTPUT_FILE = args.output_file

    open_temp_dir()
    dump_latex_template()
    dump_yaml_template()
    download_papers()
    deduplicate()
    filter_large_files()
    filter_diagrams()
    deduplicate()
    extract_captions()
    extract_equations()
    build_paper()
    shutil.copy("output.pdf", OUTPUT_FILE)


if __name__ == "__main__":
    main()
