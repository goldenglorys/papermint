import os
import re
import concurrent.futures
from mint.pandoc_utils import check_latex


def extract_captions(temp_dir, min_caption_length, max_concurrency, quiet):
    unchecked_captions_file = os.path.join(temp_dir, "unchecked_captions.txt")
    captions_file = os.path.join(temp_dir, "captions.txt")

    with open(unchecked_captions_file, "w") as f:
        for file in os.listdir(os.path.join(temp_dir, "tex")):
            file_path = os.path.join(temp_dir, "tex", file)
            if os.path.isfile(file_path):  # Ensure it's a file, not a directory
                with open(file_path, "r") as tex_file:
                    f.write(
                        "\n".join(re.findall(r"\\caption\{([^\{]+)\}", tex_file.read()))
                    )

    with open(unchecked_captions_file, "r") as f:
        captions = [
            line.strip() for line in f if len(line.strip()) >= min_caption_length
        ]

    def process_caption(caption):
        if check_latex(caption):
            return caption
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        results = list(executor.map(process_caption, captions))

    with open(captions_file, "w") as f:
        f.write("\n".join(filter(None, results)))
