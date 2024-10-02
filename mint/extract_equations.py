import os
import re
import concurrent.futures
from mint.pandoc_utils import check_latex


def extract_equations(
    temp_dir, min_equation_length, max_equation_length, max_concurrency, quiet
):
    unchecked_equations_file = os.path.join(temp_dir, "unchecked_equations.txt")
    equations_file = os.path.join(temp_dir, "equations.txt")

    with open(unchecked_equations_file, "w") as f:
        for file in os.listdir(os.path.join(temp_dir, "tex")):
            file_path = os.path.join(temp_dir, "tex", file)
            if os.path.isfile(file_path):  # Ensure it's a file, not a directory
                with open(file_path, "r") as tex_file:
                    f.write("\n".join(re.findall(r"\$\$([^\$]+)\$\$", tex_file.read())))

    with open(unchecked_equations_file, "r") as f:
        equations = [
            line.strip()
            for line in f
            if min_equation_length <= len(line.strip()) <= max_equation_length
        ]

    def process_equation(equation):
        if check_latex(f"$${equation}$$"):
            return equation
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        results = list(executor.map(process_equation, equations))

    with open(equations_file, "w") as f:
        f.write("\n".join(filter(None, results)))
