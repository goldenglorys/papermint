import random
from typing import Dict, Optional


class PaperGenerator:
    def __init__(self, content: Dict):
        self.content = content
        self.sections = [
            "Introduction",
            "Related Work",
            "Methodology",
            "Experimental Results",
            "Discussion",
            "Conclusion",
        ]

    def generate(
        self, title: Optional[str] = None, author: str = "AI Researcher"
    ) -> str:
        if not title:
            title = self._generate_title()

        abstract = self._generate_abstract()
        sections = self._generate_sections()

        latex_content = self._create_latex_document(title, author, abstract, sections)
        return latex_content

    def _generate_title(self) -> str:
        adjectives = ["Novel", "Robust", "Advanced", "Innovative", "Efficient"]
        verbs = ["Approach to", "Framework for", "Method for", "Analysis of"]
        topics = [
            "Deep Learning",
            "Neural Networks",
            "Machine Learning",
            "Data Analysis",
        ]

        return f"A {random.choice(adjectives)} {random.choice(verbs)} {random.choice(topics)}"

    def _generate_abstract(self) -> str:
        abstract_parts = random.sample(self.content["text_blocks"], 3)
        return " ".join(abstract_parts)[:500] + "."

    def _generate_sections(self) -> Dict[str, str]:
        sections = {}
        for section in self.sections:
            content = self._generate_section_content(section)
            sections[section] = content
        return sections

    def _generate_section_content(self, section: str) -> str:
        num_paragraphs = random.randint(2, 4)
        paragraphs = []

        for _ in range(num_paragraphs):
            paragraph = random.choice(self.content["text_blocks"])

            if section in ["Methodology", "Experimental Results"]:
                if random.random() < 0.3 and self.content["equations"]:
                    equation = random.choice(self.content["equations"])
                    paragraph += f"\n\n$${equation}$$\n\n"

            if section == "Experimental Results":
                if random.random() < 0.3 and self.content["captions"]:
                    caption = random.choice(self.content["captions"])
                    paragraph += f"\n\nAs shown in Figure X, {caption}\n\n"

            paragraphs.append(paragraph)

        return "\n\n".join(paragraphs)

    def _create_latex_document(
        self, title: str, author: str, abstract: str, sections: Dict[str, str]
    ) -> str:
        latex_content = f"""
\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{graphicx}}
\\title{{{title}}}
\\author{{{author}}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

"""
        for section, content in sections.items():
            latex_content += f"""
\\section{{{section}}}
{content}

"""

        latex_content += "\\end{document}"
        return latex_content
