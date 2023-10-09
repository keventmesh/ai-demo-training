import asyncio
import os
from PIL import Image

SRC_DIR = "original"
TARGET_DIR = "scaled"
TARGET_WIDTH = 640
TARGET_HEIGHT = 480
TARGET_ASPECT_RATIO = TARGET_HEIGHT / TARGET_WIDTH
EPSILON = 0.01


async def scale_down(src_file):
    src_file_path = os.path.join(SRC_DIR, src_file)
    target_file_path = os.path.join(TARGET_DIR, src_file)
    print(f"scale down {src_file_path} to {target_file_path}")
    image = Image.open(src_file_path)
    width, height = image.size
    aspect_ratio = height / width
    if aspect_ratio > 1:
        print(f"rotating {src_file_path}")
        # rotate the image
        image = image.rotate(90, expand=True)
        aspect_ratio = 1 / aspect_ratio

    if aspect_ratio < TARGET_ASPECT_RATIO - EPSILON or aspect_ratio > TARGET_ASPECT_RATIO + EPSILON: ## floating point shit requires epsilon
        # stop processing
        print(f"Image aspect ratio {aspect_ratio} ({width}x{height}) is not the same with the target aspect ratio: {TARGET_ASPECT_RATIO}")
        exit(-1)

    image.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    image.save(target_file_path, "PNG")

async def main():
    files = []

    # get the image files in the directory
    for file in os.listdir(SRC_DIR):
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
            files.append(file)

    async with asyncio.TaskGroup() as tg:
        for file in files:
            await tg.create_task(scale_down(file))


if __name__ == '__main__':
    asyncio.run(main())
