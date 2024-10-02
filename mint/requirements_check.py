import subprocess


def check_requirements():
    required_commands = ["pandoc", "curl", "python3", "pdflatex", "iconv"]
    for command in required_commands:
        try:
            subprocess.run(
                [command, "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            raise Exception(
                f"{command} must be installed and on the PATH for this app to run."
            )
