import os
import subprocess
import random
import re
import requests


def check_latex(content):
    dir = os.path.join(temp_dir, "latex_check")
    os.makedirs(dir, exist_ok=True)
    with open(os.path.join(dir, "content.md"), "w") as f:
        f.write(content)
    subprocess.run(
        [
            "pandoc",
            "--from",
            "markdown",
            "--to",
            "latex",
            "--template",
            "template.tex",
            "--output",
            os.path.join(dir, "out.tex"),
            os.path.join(dir, "content.md"),
        ],
        check=True,
    )
    result = subprocess.run(
        ["pdflatex", "-output-directory", dir, "out.tex"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.returncode == 0


def build_paper(input_file, output_file, temp_dir, figure_prob, equation_prob, quiet):
    if input_file.startswith("http"):
        response = requests.get(input_file)
        with open(os.path.join(temp_dir, "input_file"), "wb") as f:
            f.write(response.content)
        input_file = os.path.join(temp_dir, "input_file")

    with open(os.path.join(temp_dir, "metadata.md"), "r") as f:
        metadata = f.read()

    with open(input_file, "r") as f:
        content = f.read()

    def insert_random_elements(line):
        if random.randint(1, figure_prob) == 1:
            with open(os.path.join(temp_dir, "captions.txt"), "r") as f:
                captions = f.readlines()
            if captions:
                line += f"\n\n![{random.choice(captions).strip()}]({random.choice(os.listdir(os.path.join(temp_dir, 'images')))})\n\n"
        if random.randint(1, equation_prob) == 1:
            with open(os.path.join(temp_dir, "equations.txt"), "r") as f:
                equations = f.readlines()
            if equations:
                line += f"\n\n{random.choice(equations).strip()}\n\n"
        return line

    content = "\n".join(insert_random_elements(line) for line in content.splitlines())

    with open(os.path.join(temp_dir, "output.md"), "w") as f:
        f.write(metadata + content)

    subprocess.run(
        [
            "pandoc",
            "--from",
            "markdown",
            "--to",
            "latex",
            "--template",
            os.path.join(temp_dir, "template.tex"),
            "--output",
            os.path.join(temp_dir, "output.tex"),
            os.path.join(temp_dir, "output.md"),
        ],
        check=True,
    )
    subprocess.run(
        ["pdflatex", "-output-directory", temp_dir, "output.tex"], check=True
    )

    os.rename(os.path.join(temp_dir, "output.pdf"), output_file)
