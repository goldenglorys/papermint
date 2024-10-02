import arxiv
import tempfile
import os
from typing import List, Dict


class ArxivDownloader:
    def __init__(self, category: str, num_papers: int):
        self.category = category
        self.num_papers = num_papers
        self.temp_dir = tempfile.mkdtemp()

    def download(self) -> List[Dict]:
        client = arxiv.Client()

        search = arxiv.Search(
            query=f"cat:{self.category}",
            max_results=self.num_papers,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

        papers = []
        for result in client.results(search):
            paper = {
                "title": result.title,
                "abstract": result.summary,
                "authors": [author.name for author in result.authors],
                "pdf_url": result.pdf_url,
                "categories": result.categories,
            }

            pdf_path = os.path.join(self.temp_dir, f"{result.get_short_id()}.pdf")
            result.download_pdf(filename=pdf_path)
            paper["pdf_path"] = pdf_path

            papers.append(paper)

        return papers
