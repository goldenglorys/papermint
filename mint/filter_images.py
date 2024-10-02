import os
import shutil
from PIL import Image


def filter_large_files(temp_dir, max_size):
    os.makedirs(f"{temp_dir}/big_images", exist_ok=True)
    for file in os.listdir(f"{temp_dir}/images"):
        if os.path.getsize(f"{temp_dir}/images/{file}") > max_size:
            shutil.move(f"{temp_dir}/images/{file}", f"{temp_dir}/big_images/{file}")


def filter_diagrams(temp_dir):
    os.makedirs(f"{temp_dir}/non_diagram_images", exist_ok=True)
    for file in os.listdir(f"{temp_dir}/images"):
        img = Image.open(f"{temp_dir}/images/{file}")
        if img.getpixel((0, 0))[3] == 0 or sum(img.getpixel((0, 0))[:3]) < 750:
            shutil.move(
                f"{temp_dir}/images/{file}", f"{temp_dir}/non_diagram_images/{file}"
            )
