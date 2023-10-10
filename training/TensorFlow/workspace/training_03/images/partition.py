import os
import random
import shutil

SRC_DIR = "03_scaled"
TEST_DIR = "test"
TRAIN_DIR = "train"
TEST_TO_TRAIN_RATIO = 0.1

def xml_file_for_image(image_file):
    return image_file.replace(".png", ".xml")

def main():
    # lets use the same seed for determinism
    random.seed(123456789)

    images = []

    for file in os.listdir(SRC_DIR):
        if file.endswith(".png"):
            images.append(file)

    random.shuffle(images)

    test_count = int(len(images) * TEST_TO_TRAIN_RATIO)
    test_images = images[:test_count]
    train_images = images[test_count:]

    # copy over the training images
    for image in train_images:
        src = os.path.join(SRC_DIR, image)
        dest = os.path.join(TRAIN_DIR, image)
        shutil.copyfile(src, dest)

        xml_src = os.path.join(SRC_DIR, xml_file_for_image(image))
        xml_dest = os.path.join(TRAIN_DIR, xml_file_for_image(image))
        shutil.copyfile(xml_src, xml_dest)

    # copy over the test images
    for image in test_images:
        src = os.path.join(SRC_DIR, image)
        dest = os.path.join(TEST_DIR, image)
        shutil.copyfile(src, dest)

        xml_src = os.path.join(SRC_DIR, xml_file_for_image(image))
        xml_dest = os.path.join(TEST_DIR, xml_file_for_image(image))
        shutil.copyfile(xml_src, xml_dest)

if __name__ == '__main__':
    main()
