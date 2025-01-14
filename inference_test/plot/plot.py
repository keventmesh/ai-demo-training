import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging (1)
import tensorflow as tf
tf.get_logger().setLevel('ERROR')  # Suppress TensorFlow logging (2)

import time
import numpy as np
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

# Enable GPU dynamic memory allocation
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

MODEL = os.environ.get("MODEL")
if not MODEL:
    print("Missing MODEL environment variable")
    exit(1)

TEST_IMAGES = [
    f"test_images/photo_2023-08-08 13.26.49.jpeg",
    f"test_images/photo_2023-08-08 13.26.52.jpeg",
    f"test_images/photo_2023-08-08 13.26.53.jpeg",
    f"test_images/photo_2023-08-08 13.26.56.jpeg",
]

PATH_TO_SAVED_MODEL = f"models/{MODEL}/saved_model"

PATH_TO_LABELS = "models/label_map.pbtxt"

OUTPUT_DIR = f"./output/{MODEL}"

print('Loading model...', end='')
start_time = time.time()

# Load saved model and build the detection function
detect_fn = tf.saved_model.load(os.path.join(SCRIPT_PATH, PATH_TO_SAVED_MODEL))

end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))

print("\n\n\n\n")
print("Model inputs and outputs: ")
print(detect_fn.signatures['serving_default'].pretty_printed_signature())
print("\n\n")

# %%
# Load label map data (for plotting)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Label maps correspond index numbers to category names, so that when our convolution network
# predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility
# functions, but anything that returns a dictionary mapping integers to appropriate string labels
# would be fine.

category_index = label_map_util.create_category_index_from_labelmap(os.path.join(SCRIPT_PATH, PATH_TO_LABELS),
                                                                    use_display_name=True)

# %%
# Putting everything together
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The code shown below loads an image, runs it through the detection model and visualizes the
# detection results, including the keypoints.
#
# Note that this will take a long time (several minutes) the first time you run this code due to
# tf.function's trace-compilation --- on subsequent runs (e.g. on new images), things will be
# faster.
#
# Here are some simple things to try out if you are curious:
#
# * Modify some of the input images and see if detection still works. Some simple things to try out here (just uncomment the relevant portions of code) include flipping the image horizontally, or converting to grayscale (note that we still expect the input image to have 3 channels).
# * Print out `detections['detection_boxes']` and try to match the box locations to the boxes in the image.  Notice that coordinates are given in normalized form (i.e., in the interval [0, 1]).
# * Set ``min_score_thresh`` to other values (between 0 and 1) to allow more detections in or to filter out more detections.

def load_image_into_numpy_array(path):
    """Load an image from file into a numpy array.

    Puts image into numpy array to feed into tensorflow graph.
    Note that by convention we put it into a numpy array with shape
    (height, width, channels), where channels=3 for RGB.

    Args:
      path: the file path to the image

    Returns:
      uint8 numpy array with shape (img_height, img_width, 3)
    """
    return np.array(Image.open(path))

for image_path in TEST_IMAGES:
    image_path = os.path.join(SCRIPT_PATH, image_path)
    image_path = os.path.abspath(image_path)

    print("\n\n\n\n")
    print("==================================")
    print('Running inference for {}... '.format(image_path))

    image_np = load_image_into_numpy_array(image_path)
    input_tensor = tf.convert_to_tensor(image_np)

    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    detection_start_time = time.time()

    detections = detect_fn(input_tensor)

    detection_end_time = time.time()
    detection_took = detection_end_time - detection_start_time
    print('Done! Took {} seconds'.format(detection_took))

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
    detections['num_detections'] = num_detections

    print("Number of detections: " + str(num_detections))

    print(detections)

    # detection_classes should be ints.
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    image_np_with_detections = image_np.copy()

    boxes = detections['detection_boxes']
    scores = detections['detection_scores']

    pil_img = Image.open(image_path)
    for i in range(boxes.shape[0]):
        if scores[i] < 0.3:
            continue
        box = tuple(boxes[i].tolist())
        ymin, xmin, ymax, xmax = box
        im_width, im_height = pil_img.size
        (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                      ymin * im_height, ymax * im_height)
        print(f"Detection box relative:{str(box)} score:{str(scores[i])}")
        print(f"Detection box absolute:{str((left, right, top, bottom))} score:{str(scores[i])}")

    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'],
        detections['detection_classes'],
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=.30,
        agnostic_mode=False)

    matplotlib.use("Qt5Agg")
    plt.figure()
    plt.imshow(image_np_with_detections)
    target_file_name = os.path.join(SCRIPT_PATH, OUTPUT_DIR, os.path.basename(image_path) + ".png")
    plt.savefig(target_file_name)
    print('Done')

plt.show()
