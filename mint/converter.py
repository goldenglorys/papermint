import tempfile
import os
import subprocess
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape


class PDFConverter:
    def __init__(self, latex_content: str):
        self.latex_content = latex_content
        self.temp_dir = tempfile.mkdtemp()

    def convert(self) -> str:
        tex_path = os.path.join(self.temp_dir, "paper.tex")
        with open(tex_path, "w") as f:
            f.write(self.latex_content)

        try:
            subprocess.run(
                ["pdflatex", "-output-directory", self.temp_dir, tex_path],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"PDF generation failed: {e.stderr.decode()}")

        pdf_path = os.path.join(self.temp_dir, "paper.pdf")
        if not os.path.exists(pdf_path):
            raise Exception("PDF file was not generated")

        return pdf_path
    
    def convert3(self) -> str:
        # Create a temporary LaTeX document
        doc = Document(documentclass='article', document_options='12pt')
        
        # Add the provided LaTeX content to the document
        doc.append(NoEscape(self.latex_content))

        # Generate the PDF
        pdf_path = os.path.join(self.temp_dir, "paper.pdf")
        doc.generate_pdf(filepath=pdf_path, clean_tex=False, compiler='pdflatex')

        if not os.path.exists(pdf_path):
            raise Exception("PDF file was not generated")

        return pdf_path
