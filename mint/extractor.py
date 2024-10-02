import PyPDF2
import re
from typing import List, Dict


class ContentExtractor:
    def __init__(self, papers: List[Dict]):
        self.papers = papers
        self.equations_pattern = re.compile(r"\$(.*?)\$")
        self.caption_pattern = re.compile(r"Fig\.|Figure|Table(.*?)\.", re.IGNORECASE)

    def extract(self) -> Dict:
        content = {"equations": [], "captions": [], "text_blocks": []}

        for paper in self.papers:
            pdf_text = self._extract_text_from_pdf(paper["pdf_path"])

            equations = self.equations_pattern.findall(pdf_text)
            content["equations"].extend(equations)

            captions = self.caption_pattern.findall(pdf_text)
            content["captions"].extend(captions)

            paragraphs = [
                p.strip() for p in pdf_text.split("\n\n") if len(p.strip()) > 100
            ]
            content["text_blocks"].extend(paragraphs)

        return content

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
