Based on https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/index.html

Create environment, install dependencies:
```shell
mkdir training
cd training

# create a new virtual environment and activate it
python3 -m venv .venv
source .venv/bin/activate
# Windows
.venv\Scripts\activate.bat

# install tensorflow
pip install --ignore-installed --upgrade tensorflow==2.5.0

# verify if tensorflow is installed properly
python -c "import tensorflow as tf;print(tf.reduce_sum(tf.random.normal([1000, 1000])))"

# go back to `<root>`
cd ..
```

GPU Support on Windows: NOT DOCUMENTED HERE

Download TensorFlow Model Garden:
```shell
cd training

# download TensorFlow Model Garden at commit 4e797d7010a437b189ea0e52cfb398ebb74ac75f
mkdir TensorFlow
cd TensorFlow
curl -L https://github.com/tensorflow/models/archive/4e797d7010a437b189ea0e52cfb398ebb74ac75f.zip -o models.zip
unzip models.zip
mv models-4e797d7010a437b189ea0e52cfb398ebb74ac75f models

# back to `<root>`
cd ../..
```

Compile Protobufs:
```shell
# install Protocol Buffers and have it in your PATH
# I have it already, figure it out yourself
#

# go into `<root>/training/TensorFlow/models/research/`
cd training/TensorFlow/models/research/

# compile Protobufs
protoc object_detection/protos/*.proto --python_out=.

# back to `<root>`
cd ../../../..
```

Install COCO API, but custom:
```shell
# install pycocotools
pip install cython==3.0.0
pip install git+https://github.com/philferriere/cocoapi.git@2929bd2ef6b451054755dfd7ceb09278f935f7ad#subdirectory=PythonAPI
```

Install TensorFlow Object Detection API:
```shell
cd training/TensorFlow/models/research/

cp object_detection/packages/tf2/setup.py .
python -m pip install .


# It is ok to get errors/warnings like
#            By 2023-Oct-30, you need to update your project and remove deprecated calls
#            or your builds will no longer be supported.
#    
#            See https://setuptools.pypa.io/en/latest/userguide/declarative_config.html for details.


cd ../../../..
```

Test if everything is installed properly:
```shell
cd training/TensorFlow/models/research/

python object_detection/builders/model_builder_tf2_test.py

# Good output:
# Ran 24 tests in 31.777s

cd ../../../..
```

Create TensorFlow workspace:
```shell
cd training/TensorFlow

mkdir workspace
mkdir workspace/training_03
mkdir workspace/training_03/annotations
mkdir workspace/training_03/exported-models
mkdir workspace/training_03/images
mkdir workspace/training_03/images/test
mkdir workspace/training_03/images/train
mkdir workspace/training_03/models
mkdir workspace/training_03/pre-trained-models

touch workspace/.gitkeep
touch workspace/training_03/.gitkeep
touch workspace/training_03/annotations/.gitkeep
touch workspace/training_03/exported-models/.gitkeep
touch workspace/training_03/images/.gitkeep
touch workspace/training_03/images/test/.gitkeep
touch workspace/training_03/images/train/.gitkeep
touch workspace/training_03/models/.gitkeep
touch workspace/training_03/pre-trained-models/.gitkeep

cd ../..
```

Put images under `training/TensorFlow/workspace/training_03/images/00_original` manually.

As they should have same aspect ratio, do a rotation first:
```shell
cd training/TensorFlow/workspace/training_03/images

python rotate.py

cd ../../../../..
```

Create the label map:
```shell
cat <<EOF >>training/TensorFlow/workspace/training_03/annotations/label_map.pbtxt
item {
    id: 1
    name: 'knative'
}
EOF
```

Install labelImg for annotating images:
```shell
pip install labelImg
```

Annotate images:
```shell
labelImg training/TensorFlow/workspace/training_03/images/01_rotated training/TensorFlow/workspace/training_03/annotations/label_map.pbtxt training/TensorFlow/workspace/training_03/images/01_rotated
# In the tool:
# - Change save location to training/TensorFlow/workspace/training_03/scaled/images
# - Use class `knative`
# - Press `w` to draw a box, `a`/`d` to go to the previous/next image
```

NOTE: if `labelImg` crashes, it might be because of this: https://github.com/HumanSignal/labelImg/issues/885
In that case, create a new virtual environment using Python 3.8 and install `labelImg` there.
Like:
```shell
brew install python@3.8 --no-binaries # do not link shit
python3.8 -m venv /tmp/labelImg_venv
source /tmp/labelImg_venv/bin/activate
```

Create variations of the images:
```shell
cd training/TensorFlow/workspace/training_03/images

python augment.py

cd ../../../../..
```

Check if the augmented images have correct annotations:
```shell
labelImg training/TensorFlow/workspace/training_03/images/02_augmented training/TensorFlow/workspace/training_03/annotations/label_map.pbtxt training/TensorFlow/workspace/training_03/images/02_augmented
```

Scale down images:
```shell
cd training/TensorFlow/workspace/training_02/images

python scale.py

cd ../../../../..
```

Check if the resized images have correct annotations:
```shell
labelImg training/TensorFlow/workspace/training_03/images/03_scaled training/TensorFlow/workspace/training_03/annotations/label_map.pbtxt training/TensorFlow/workspace/training_03/images/03_scaled
```

Then partition images into `test` and `train` folders:

```shell
cd training/TensorFlow/workspace/training_02/images

python partition.py

cd ../../../../..
```
