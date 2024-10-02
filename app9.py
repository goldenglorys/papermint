import streamlit as st
import tempfile
import os
import subprocess
import shutil
import random
import re
import base64
import requests
import json
from pathlib import Path
import tarfile
import gzip
import io
from PIL import Image
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import concurrent.futures

# Constants
DEFAULT_TEMP_DIR = "/tmp/paperify"
DEFAULT_ARXIV_CAT = "math"
DEFAULT_NUM_PAPERS = 100
DEFAULT_MAX_CONCURRENCY = 32
DEFAULT_FIGURE_PROB = 25
DEFAULT_EQUATION_PROB = 25
DEFAULT_MAX_SIZE = 2500000
DEFAULT_MIN_EQUATION_LENGTH = 5
DEFAULT_MAX_EQUATION_LENGTH = 120
DEFAULT_MIN_CAPTION_LENGTH = 20
DEFAULT_CHATGPT_TOPIC = "cybersecurity"


# Utility functions
def generate_random_string(length: int) -> str:
    return base64.b64encode(os.urandom(length), altchars=b"__").decode("ascii")


def save_latex_template() -> str:
    template_path = Path("template.tex")
    template_content = """\\PassOptionsToPackage{unicode$for(hyperrefoptions)$,$hyperrefoptions$$endfor$}{hyperref}
    \\PassOptionsToPackage{hyphens}{url}
    % ... [rest of the LaTeX template content]
    """
    template_path.write_text(template_content)
    return str(template_path)


class PaperifyProcessor:
    def __init__(
        self,
        temp_dir: str = DEFAULT_TEMP_DIR,
        arxiv_cat: str = DEFAULT_ARXIV_CAT,
        num_papers: int = DEFAULT_NUM_PAPERS,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        figure_prob: int = DEFAULT_FIGURE_PROB,
        equation_prob: int = DEFAULT_EQUATION_PROB,
        max_size: int = DEFAULT_MAX_SIZE,
        min_equation_length: int = DEFAULT_MIN_EQUATION_LENGTH,
        max_equation_length: int = DEFAULT_MAX_EQUATION_LENGTH,
        min_caption_length: int = DEFAULT_MIN_CAPTION_LENGTH,
        chatgpt_topic: str = DEFAULT_CHATGPT_TOPIC,
    ):
        self.temp_dir = Path(temp_dir)
        self.arxiv_cat = arxiv_cat
        self.num_papers = num_papers
        self.max_concurrency = max_concurrency
        self.figure_prob = figure_prob
        self.equation_prob = equation_prob
        self.max_size = max_size
        self.min_equation_length = min_equation_length
        self.max_equation_length = max_equation_length
        self.min_caption_length = min_caption_length
        self.chatgpt_topic = chatgpt_topic

        self.images_dir = self.temp_dir / "images"
        self.tex_dir = self.temp_dir / "tex"
        self.unknown_files_dir = self.temp_dir / "unknown_files"

    def setup_directories(self):
        for directory in [
            self.temp_dir,
            self.images_dir,
            self.tex_dir,
            self.unknown_files_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def generate_metadata(self, chatgpt_token: Optional[str]) -> Dict[str, Any]:
        if chatgpt_token:
            # Generate metadata using ChatGPT API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {chatgpt_token}",
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a JSON generator for scientific research papers.",
                    },
                    {
                        "role": "user",
                        "content": f"Generate metadata for a paper about {self.chatgpt_topic}",
                    },
                ],
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions", headers=headers, json=data
            )
            return response.json()["choices"][0]["message"]["content"]
        else:
            # Return default metadata
            return {
                "journal_name": "International Journal of Research",
                "title": f"Advanced Research in {self.chatgpt_topic.title()}",
                "author_name": "Dr. Jane Smith",
                "author_organization": "Research Institute",
                "author_email": "jsmith@research.org",
                "thanks": "This research was supported by...",
                "abstract": f"This paper presents novel findings in {self.chatgpt_topic}...",
            }

    def download_papers(self) -> None:
        arxiv_url = f"https://arxiv.org/list/{self.arxiv_cat}/current?skip=0&show={self.num_papers}"
        response = requests.get(arxiv_url)
        paper_urls = re.findall(r'href="/format/([^"]*)"', response.text)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrency
        ) as executor:
            futures = [
                executor.submit(self.process_paper, f"https://arxiv.org/e-print/{url}")
                for url in paper_urls
            ]
            concurrent.futures.wait(futures)

    def process_paper(self, url: str) -> None:
        response = requests.get(url)
        if response.status_code != 200:
            return

        content = io.BytesIO(response.content)
        try:
            with tarfile.open(fileobj=content) as tar:
                for member in tar.getmembers():
                    if not self.is_safe_path(member.name):
                        continue
                    ext = Path(member.name).suffix.lower()[1:]
                    if ext in ["jpg", "jpeg", "png", "tex"]:
                        output_path = (
                            self.images_dir / f"{generate_random_string(24)}.{ext}"
                        )
                        with open(output_path, "wb") as f:
                            f.write(tar.extractfile(member).read())
        except:
            try:
                content.seek(0)
                decompressed = gzip.decompress(content.read())
                output_path = self.tex_dir / f"{generate_random_string(24)}.tex"
                output_path.write_bytes(decompressed)
            except:
                output_path = self.unknown_files_dir / generate_random_string(24)
                output_path.write_bytes(content.getvalue())

    def is_safe_path(self, path: str) -> bool:
        return not (path.startswith("..") or path.startswith("/"))

    def filter_images(self) -> None:
        # Filter large images
        for img_path in self.images_dir.glob("*"):
            if img_path.stat().st_size > self.max_size:
                shutil.move(str(img_path), str(self.unknown_files_dir / img_path.name))

        # Filter non-diagram images if Pillow is available
        try:
            for img_path in self.images_dir.glob("*"):
                with Image.open(img_path) as img:
                    if not self.is_diagram(img):
                        shutil.move(
                            str(img_path), str(self.unknown_files_dir / img_path.name)
                        )
        except ImportError:
            pass

    def is_diagram(self, img: Image.Image) -> bool:
        # Simple heuristic: check if corners are white or transparent
        corners = [img.getpixel((0, 0)), img.getpixel((img.width - 1, img.height - 1))]

        for corner in corners:
            if len(corner) == 4 and corner[3] == 0:  # Transparent
                continue
            if sum(corner[:3]) < 750:  # Not close to white
                return False
        return True

    def extract_content(self) -> Tuple[List[str], List[str]]:
        captions = []
        equations = []

        for tex_file in self.tex_dir.glob("*.tex"):
            content = tex_file.read_text()

            # Extract captions
            captions.extend(re.findall(r"\\caption{([^{}]+)}", content))

            # Extract equations
            equations.extend(re.findall(r"\$\$(.*?)\$\$", content, re.DOTALL))

        # Filter and validate
        captions = [c for c in captions if len(c) >= self.min_caption_length]
        equations = [
            e
            for e in equations
            if self.min_equation_length <= len(e) <= self.max_equation_length
        ]

        return captions, equations

    def build_paper(self, input_path: str, output_path: str, from_format: str) -> None:
        # Convert input to markdown
        md_content = self.convert_to_markdown(input_path, from_format)

        # Enhance content
        captions, equations = self.extract_content()
        enhanced_content = self.enhance_content(md_content, captions, equations)

        # Convert to PDF
        self.convert_to_pdf(enhanced_content, output_path)

    def convert_to_markdown(self, input_path: str, from_format: str) -> str:
        result = subprocess.run(
            [
                "pandoc",
                "--from",
                from_format,
                "--to",
                "gfm",
                "--wrap",
                "none",
                "--extract-media",
                str(self.temp_dir / "media"),
                input_path,
            ],
            capture_output=True,
            text=True,
        )
        return result.stdout

    def enhance_content(
        self, content: str, captions: List[str], equations: List[str]
    ) -> str:
        enhanced_lines = []
        for line in content.split("\n"):
            enhanced_lines.append(line)

            if (
                random.randint(1, self.figure_prob) == 1
                and captions
                and list(self.images_dir.glob("*"))
            ):
                caption = random.choice(captions)
                image = random.choice(list(self.images_dir.glob("*")))
                enhanced_lines.append(f"\n\n![{caption}]({image})\n\n")

            if random.randint(1, self.equation_prob) == 1 and equations:
                equation = random.choice(equations)
                enhanced_lines.append(f"\n\n$${equation}$$\n\n")

        return "\n".join(enhanced_lines)

    def convert_to_pdf(self, content: str, output_path: str) -> None:
        # Save enhanced content as markdown
        md_path = self.temp_dir / "enhanced.md"
        md_path.write_text(content)

        # Convert to PDF using pandoc and pdflatex
        subprocess.run(
            [
                "pandoc",
                "--from",
                "markdown",
                "--to",
                "latex",
                "--template",
                save_latex_template(),
                "--output",
                str(self.temp_dir / "output.tex"),
                str(md_path),
            ]
        )

        subprocess.run(
            [
                "pdflatex",
                "-output-directory",
                str(self.temp_dir),
                str(self.temp_dir / "output.tex"),
            ]
        )

        # Move final PDF to desired location
        shutil.move(str(self.temp_dir / "output.pdf"), output_path)


def main():
    st.title("Paperify - Turn Any Document into a Research Paper")

    st.sidebar.header("Settings")
    arxiv_cat = st.sidebar.text_input("arXiv Category", DEFAULT_ARXIV_CAT)
    num_papers = st.sidebar.number_input("Number of Papers", value=DEFAULT_NUM_PAPERS)
    chatgpt_topic = st.sidebar.text_input("Paper Topic", DEFAULT_CHATGPT_TOPIC)
    chatgpt_token = st.sidebar.text_input("OpenAI API Key (optional)", type="password")

    advanced_settings = st.sidebar.expander("Advanced Settings")
    with advanced_settings:
        figure_prob = st.number_input("Figure Frequency", value=DEFAULT_FIGURE_PROB)
        equation_prob = st.number_input(
            "Equation Frequency", value=DEFAULT_EQUATION_PROB
        )
        max_size = st.number_input("Max Image Size (bytes)", value=DEFAULT_MAX_SIZE)

    st.write("Upload a document or provide a URL to convert it into a research paper.")

    input_method = st.radio("Choose input method:", ["Upload File", "Enter URL"])

    processor = None
    try:
        if input_method == "Upload File":
            uploaded_file = st.file_uploader("Choose a file")
            if uploaded_file:
                with tempfile.TemporaryDirectory() as temp_dir:
                    processor = PaperifyProcessor(
                        temp_dir=temp_dir,
                        arxiv_cat=arxiv_cat,
                        num_papers=num_papers,
                        figure_prob=figure_prob,
                        equation_prob=equation_prob,
                        max_size=max_size,
                        chatgpt_topic=chatgpt_topic,
                    )

                    # Save uploaded file
                    input_path = Path(temp_dir) / uploaded_file.name
                    input_path.write_bytes(uploaded_file.getbuffer())

                    if st.button("Generate Research Paper"):
                        with st.spinner("Processing..."):
                            processor.setup_directories()
                            processor.download_papers()
                            processor.filter_images()

                            output_path = Path(temp_dir) / "final_paper.pdf"
                            processor.build_paper(
                                str(input_path),
                                str(output_path),
                                Path(uploaded_file.name).suffix[1:],
                            )

                            with open(output_path, "rb") as f:
                                st.download_button(
                                    "Download Generated Paper",
                                    f,
                                    file_name="generated_paper.pdf",
                                    mime="application/pdf",
                                )
        else:
            url = st.text_input("Enter URL")
            if url and st.button("Generate Research Paper"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    processor = PaperifyProcessor(
                        temp_dir=temp_dir,
                        arxiv_cat=arxiv_cat,
                        num_papers=num_papers,
                        figure_prob=figure_prob,
                        equation_prob=equation_prob,
                        max_size=max_size,
                        chatgpt_topic=chatgpt_topic,
                    )

                    with st.spinner("Processing..."):
                        processor.setup_directories()
                        processor.download_papers()
                        processor.filter_images()

                        output_path = Path(temp_dir) / "final_paper.pdf"
                        processor.build_paper(url, str(output_path), "html")

                        with open(output_path, "rb") as f:
                            st.download_button(
                                "Download Generated Paper",
                                f,
                                file_name="generated_paper.pdf",
                                mime="application/pdf",
                            )
    except Exception as e:
        print(e)
        st.error(f"An error occurred: {str(e)}")
