import asyncio
import os
from PIL import Image
import xml.etree.ElementTree as ET
from pathlib import Path
import math

SRC_DIR = "01_rotated"
TARGET_DIR = "02_augmented"
TARGET_ASPECT_RATIO = 3 / 4
EPSILON = 0.01

# TODO: doesn't work with any other rotation in between
ROTATIONS = [0, 90, 180, 270]

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


async def augment(src_file):
    src_file_base_name = os.path.basename(src_file)
    src_file_base_name_without_ext = os.path.splitext(src_file_base_name)[0]
    src_xml_file = f"{src_file_base_name_without_ext}.xml"
    src_file_path = os.path.join(SCRIPT_DIR, SRC_DIR, src_file)
    src_xml_file_path = os.path.join(SCRIPT_DIR, SRC_DIR, src_xml_file)

    image = Image.open(src_file_path)
    width, height = image.size

    annotation_xml_file_content = Path(src_xml_file_path).read_text()

    for rotation in ROTATIONS:
        target_file_name = f"{src_file_base_name_without_ext}_r{rotation}.png"
        target_file_path = os.path.join(SCRIPT_DIR, TARGET_DIR, target_file_name)
        target_xml_file_path = os.path.join(SCRIPT_DIR, TARGET_DIR, f"{src_file_base_name_without_ext}_r{rotation}.xml")
        print(f"Augment {src_file_path} by {rotation} degrees")
        new_image = image.rotate(rotation,
                                 expand=False)  # maintain AR of the image, even though there are black regions in the corners

        root = ET.fromstring(annotation_xml_file_content)

        root.findall("./folder")[0].text = TARGET_DIR
        root.findall("./filename")[0].text = target_file_name
        root.findall("./path")[0].text = target_file_path

        xmin = int(root.findall("./object/bndbox/xmin")[0].text)
        ymin = int(root.findall("./object/bndbox/ymin")[0].text)
        xmax = int(root.findall("./object/bndbox/xmax")[0].text)
        ymax = int(root.findall("./object/bndbox/ymax")[0].text)

        # pixel location after rotation:
        # x' = a * cos(theta) - b * sin(theta)
        # y' = a * sin(theta) + b * cos(theta)

        a = width / 2
        b = height / 2
        xmin_delta = xmin - a
        ymin_delta = ymin - b
        xmax_delta = xmax - a
        ymax_delta = ymax - b
        cos = math.cos(math.radians(-rotation))
        sin = math.sin(math.radians(-rotation))

        xmin_new = int(xmin_delta * cos - ymin_delta * sin + a)
        ymin_new = int(xmin_delta * sin + ymin_delta * cos + b)

        xmax_new = int(xmax_delta * cos - ymax_delta * sin + a)
        ymax_new = int(xmax_delta * sin + ymax_delta * cos + b)

        root.findall("./object/bndbox/xmin")[0].text = str(min(xmin_new, xmax_new))
        root.findall("./object/bndbox/ymin")[0].text = str(min(ymin_new, ymax_new))
        root.findall("./object/bndbox/xmax")[0].text = str(max(xmin_new, xmax_new))
        root.findall("./object/bndbox/ymax")[0].text = str(max(ymin_new, ymax_new))

        if root.findall("./object/name")[0].text != "knative":
            print(f"Error: {src_xml_file_path} annotation does not contain knative")

        # root.findall("./object/name")[0].text = "knative_augmented"

        new_image.save(target_file_path, "PNG")
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
            tg.create_task(augment(file))


if __name__ == '__main__':
    asyncio.run(main())
