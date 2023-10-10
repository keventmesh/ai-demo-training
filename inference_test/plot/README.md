```shell
mkdir inference_test
cd inference_test

# TODO: need Python 3.8
# python3.8 -m venv .venv
# source .venv/bin/activate

# .venv\Scripts\activate.bat
..\training\.venv\Scripts\activate.bat

# install tensorflow
pip install --ignore-installed --upgrade tensorflow==2.5.0 matplotlib==3.6.3 pyqt5==5.15.9

# install TensorFlow object detection API from local
cd ../training/TensorFlow/models/research/
python -m pip install .
cd ../../../../inference_test

# verify dependencies
python -c "import tensorflow as tf;print(tf.reduce_sum(tf.random.normal([1000, 1000])))"
python -c "import matplotlib;"
python -c "import numpy;"
python -c "import PIL;"
python -c "import object_detection;"

# go back to `<root>`
cd ..
```

Download the models:
```shell
cd inference_test/plot/models
gsutil cp -r gs://knative-ai-demo/exported-models/training_01 ./
gsutil cp -r gs://knative-ai-demo/exported-models/training_02 ./
cd ../..
```

Run the inference tests:
```shell
cd inference_test/plot
MODEL="training_01" python plot.py
# OR
MODEL="training_02" python plot.py
cd ../..
``` 

You will see:
- GUI window with the image and the bounding boxes
- Image will be saved to `inference_test/plot/` with the bounding boxes
