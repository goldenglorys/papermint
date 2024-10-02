import os
import arxiv
import requests
import tarfile
import gzip
import io
import base64
import concurrent.futures

def download_papers(temp_dir, arxiv_category, num_papers, max_concurrency):
    os.makedirs(f"{temp_dir}/images", exist_ok=True)
    os.makedirs(f"{temp_dir}/tex", exist_ok=True)
    os.makedirs(f"{temp_dir}/unknown_files", exist_ok=True)

    search = arxiv.Search(
        query=f"cat:{arxiv_category}",
        max_results=num_papers,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    def process_paper(paper):
        try:
            download_url = paper.pdf_url.replace("pdf", "e-print")
            response = requests.get(download_url)
            data = io.BytesIO(response.content)
            ext = lambda s: os.path.splitext(s)[1][1:].lower()
            rand = lambda n: base64.b64encode(os.urandom(n), altchars=b"__").decode("ascii")
            _filter = lambda m: m if (not (m.name.startswith("..") or m.name.startswith("/")) and m.isfile() and ext(m.name) in {"jpg", "jpeg", "png", "tex"}) else None
            randname = lambda f: f"./{rand(24)}.{ext(f)}"

            try:
                with tarfile.open(mode="r", fileobj=data) as f:
                    for member in f.getmembers():
                        if _filter(member):
                            with open(randname(member.name), "wb") as outfile:
                                outfile.write(f.extractfile(member).read())
            except tarfile.ReadError:
                data.seek(0)
                with open(randname("gzipped.tex"), "wb") as outfile:
                    outfile.write(gzip.decompress(data.read()))
            except Exception as e:
                print(f"Exception: {e}")
                with open(os.path.join(temp_dir, "unknown_files", rand(24)), "wb") as outfile:
                    outfile.write(data.read())
        except Exception as e:
            print(f"Error processing paper {paper.entry_id}: {e}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        executor.map(process_paper, search.results())

    for file in os.listdir(f"{temp_dir}/images"):
        os.rename(f"{temp_dir}/images/{file}", f"{temp_dir}/tex/{file}")