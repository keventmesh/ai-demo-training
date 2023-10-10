import asyncio
import os
from PIL import Image
import xml.etree.ElementTree as ET
from pathlib import Path
import math

SRC_DIR = "02_augmented"
TARGET_DIR = "03_scaled"
TARGET_WIDTH = 640
TARGET_HEIGHT = 480
TARGET_ASPECT_RATIO = TARGET_HEIGHT / TARGET_WIDTH
EPSILON = 0.01

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

async def scale_down(src_file):
    src_file_base_name = os.path.basename(src_file)
    src_file_base_name_without_ext = os.path.splitext(src_file_base_name)[0]
    src_xml_file = f"{src_file_base_name_without_ext}.xml"
    src_file_path = os.path.join(SCRIPT_DIR, SRC_DIR, src_file)
    src_xml_file_path = os.path.join(SCRIPT_DIR, SRC_DIR, src_xml_file)

    image = Image.open(src_file_path)

    annotation_xml_file_content = Path(src_xml_file_path).read_text()

    target_file_name = f"{src_file_base_name_without_ext}_scaled.png"
    target_file_path = os.path.join(SCRIPT_DIR, TARGET_DIR, target_file_name)
    target_xml_file_path = os.path.join(SCRIPT_DIR, TARGET_DIR, f"{src_file_base_name_without_ext}_scaled.xml")
    print(f"Scale down {src_file_path}")

    width, height = image.size

    root = ET.fromstring(annotation_xml_file_content)

    root.findall("./folder")[0].text = TARGET_DIR
    root.findall("./filename")[0].text = target_file_name
    root.findall("./path")[0].text = target_file_path

    xmin = int(root.findall("./object/bndbox/xmin")[0].text)
    ymin = int(root.findall("./object/bndbox/ymin")[0].text)
    xmax = int(root.findall("./object/bndbox/xmax")[0].text)
    ymax = int(root.findall("./object/bndbox/ymax")[0].text)

    xmin_new = int(TARGET_WIDTH / width * xmin)
    ymin_new = int(TARGET_HEIGHT / height * ymin)
    xmax_new = int(TARGET_WIDTH / width * xmax)
    ymax_new = int(TARGET_HEIGHT / height * ymax)

    root.findall("./object/bndbox/xmin")[0].text = str(min(xmin_new, xmax_new))
    root.findall("./object/bndbox/ymin")[0].text = str(min(ymin_new, ymax_new))
    root.findall("./object/bndbox/xmax")[0].text = str(max(xmin_new, xmax_new))
    root.findall("./object/bndbox/ymax")[0].text = str(max(ymin_new, ymax_new))

    if root.findall("./object/name")[0].text != "knative":
        print(f"Error: {src_xml_file_path} annotation does not contain knative")

    image.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    image.save(target_file_path, "PNG")
    tree = ET.ElementTree(root)
    tree.write(target_xml_file_path)

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
