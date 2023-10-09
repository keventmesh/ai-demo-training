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
mkdir workspace/training_02
mkdir workspace/training_02/annotations
mkdir workspace/training_02/exported-models
mkdir workspace/training_02/images
mkdir workspace/training_02/images/test
mkdir workspace/training_02/images/train
mkdir workspace/training_02/models
mkdir workspace/training_02/pre-trained-models

touch workspace/.gitkeep
touch workspace/training_02/.gitkeep
touch workspace/training_02/annotations/.gitkeep
touch workspace/training_02/exported-models/.gitkeep
touch workspace/training_02/images/.gitkeep
touch workspace/training_02/images/test/.gitkeep
touch workspace/training_02/images/train/.gitkeep
touch workspace/training_02/models/.gitkeep
touch workspace/training_02/pre-trained-models/.gitkeep

cd ../..
```

Put images under `training/TensorFlow/workspace/training_02/images/original` manually.

Then we need to resize them:
```shell
cd training/TensorFlow/workspace/training_02/images

python scale.py

cd ../../../../..

```

Important: images should have the same aspect ratio.
- See https://github.com/sglvladi/TensorFlowObjectDetectionTutorial/issues/23
- See https://stackoverflow.com/questions/48145456/tensorflow-object-detection-api-ssd-model-using-keep-aspect-ratio-resizer/48151450#48151450

Create the label map:
```shell
cat <<EOF >>training/TensorFlow/workspace/training_02/annotations/label_map.pbtxt
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
labelImg training/TensorFlow/workspace/training_02/images/scaled training/TensorFlow/workspace/training_02/annotations/label_map.pbtxt training/TensorFlow/workspace/training_02/images/scaled
# In the tool:
# - Change save location to training/TensorFlow/workspace/training_02/scaled/images
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

Then manually partition images in `training/TensorFlow/workspace/training_02/images/scaled` into `test` and `train` folders.

Create TensorFlow records:
```shell
pip install pandas==2.0.3

# create a directory for the upcoming script
mkdir -p training/TensorFlow/scripts/preprocessing
cd training/TensorFlow/scripts/preprocessing

# download the script to generate TFRecords
curl -L https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/_downloads/da4babe668a8afb093cc7776d7e630f3/generate_tfrecord.py -o generate_tfrecord.py

# Create train data:
python generate_tfrecord.py -x ../../workspace/training_02/images/train -l ../../workspace/training_02/annotations/label_map.pbtxt -o ../../workspace/training_02/annotations/train.record

# Create test data:
python generate_tfrecord.py -x ../../workspace/training_02/images/test  -l ../../workspace/training_02/annotations/label_map.pbtxt -o ../../workspace/training_02/annotations/test.record

cd ../../../..
```


===============
OK, TIME TO SWITCH TO WINDOWS NOW
===============

Download pre-trained model:
```shell
cd training/TensorFlow/workspace/training_02/pre-trained-models

# download the model archive
curl -L http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8.tar.gz -o model.tar.gz
tar xvzf model.tar.gz

cd ../../../../..
```

Copy model config:
```shell
mkdir training/TensorFlow/workspace/training_02/models/my_ssd_resnet50_v1_fpn

cp training/TensorFlow/workspace/training_02/pre-trained-models/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8/pipeline.config training/TensorFlow/workspace/training_02/models/my_ssd_resnet50_v1_fpn/pipeline.config
```

Manually change the model config in `training/TensorFlow/workspace/training_02/models/my_ssd_resnet50_v1_fpn/pipeline.config`

Train the model:
```shell
# copy the script to run the training
cp training/TensorFlow/models/research/object_detection/model_main_tf2.py training/TensorFlow/workspace/training_02

# start the training
cd training/TensorFlow/workspace/training_02
# this takes too much time without a GPU... I gave up on my MacBook Pro after 3.5 hours.
# On my Mac, per-step time at step #100 was 21.8 seconds.
# On a PC with GPU (Intel i7 10700F, Nvidia GeForce RTX 3070), per-step time at step #100 was 1.43 seconds. There's a ~15x speedup.
# On the PC, the training took 1 hour and 15 minutes.
python model_main_tf2.py --model_dir=models/my_ssd_resnet50_v1_fpn --pipeline_config_path=models/my_ssd_resnet50_v1_fpn/pipeline.config

# sample output
# I1009 21:57:20.599885 15148 model_lib_v2.py:708] {'Loss/classification_loss': 0.12144944,
# 'Loss/localization_loss': 0.060100622,
# 'Loss/regularization_loss': 0.71149987,
# 'Loss/total_loss': 0.8930499,
# 'learning_rate': 0.0159997}


# KILL when you see a totalLoss < 1

cd ../../../..
```


TODO: pip freeze at the end
TODO: also note the python version