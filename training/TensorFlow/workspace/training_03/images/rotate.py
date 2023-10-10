import asyncio
import os
from PIL import Image

SRC_DIR = "00_original"
TARGET_DIR = "01_rotated"
TARGET_ASPECT_RATIO = 3 / 4
EPSILON = 0.01


async def rotate(src_file):
    src_file_path = os.path.join(SRC_DIR, src_file)
    target_file_path = os.path.join(TARGET_DIR, src_file + ".png")
    image = Image.open(src_file_path)
    width, height = image.size

    print(f"rotating {src_file_path} to {target_file_path}")

    aspect_ratio = height / width
    if aspect_ratio > 1:
        print(f"rotating {src_file_path}")
        # rotate the image
        image = image.rotate(90, expand=True)
    else:
        print(f"not rotating {src_file_path}")

    image.save(target_file_path, "PNG")


async def main():
    files = []

    # get the image files in the directory
    for file in os.listdir(SRC_DIR):
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
            files.append(file)

    async with asyncio.TaskGroup() as tg:
        for file in files:
            await tg.create_task(rotate(file))


if __name__ == '__main__':
    asyncio.run(main())
