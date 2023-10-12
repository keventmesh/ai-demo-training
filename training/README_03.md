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
cd training/TensorFlow/workspace/training_03/images

python scale.py

cd ../../../../..
```

Check if the resized images have correct annotations:
```shell
labelImg training/TensorFlow/workspace/training_03/images/03_scaled training/TensorFlow/workspace/training_03/annotations/label_map.pbtxt training/TensorFlow/workspace/training_03/images/03_scaled
```

Then partition images into `test` and `train` folders:

```shell
cd training/TensorFlow/workspace/training_03/images

python partition.py

cd ../../../../..
```

===============
OK, TIME TO SWITCH TO WINDOWS NOW
===============

Create TensorFlow records:
```shell
pip install pandas==2.0.3

# create a directory for the upcoming script
mkdir -p training/TensorFlow/scripts/preprocessing
cd training/TensorFlow/scripts/preprocessing

# download the script to generate TFRecords
curl -L https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/_downloads/da4babe668a8afb093cc7776d7e630f3/generate_tfrecord.py -o generate_tfrecord.py

# Create train data:
python generate_tfrecord.py -x ../../workspace/training_03/images/train -l ../../workspace/training_03/annotations/label_map.pbtxt -o ../../workspace/training_03/annotations/train.record

# Create test data:
python generate_tfrecord.py -x ../../workspace/training_03/images/test  -l ../../workspace/training_03/annotations/label_map.pbtxt -o ../../workspace/training_03/annotations/test.record

cd ../../../..
```

Download pre-trained model:
```shell
cd training/TensorFlow/workspace/training_03/pre-trained-models

# download the model archive
curl -L http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8.tar.gz -o model.tar.gz
tar xvzf model.tar.gz

cd ../../../../..
```

Copy model config:
```shell
mkdir training/TensorFlow/workspace/training_03/models/my_ssd_resnet50_v1_fpn

cp training/TensorFlow/workspace/training_03/pre-trained-models/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8/pipeline.config training/TensorFlow/workspace/training_03/models/my_ssd_resnet50_v1_fpn/pipeline.config
```

Manually change the model config in `training/TensorFlow/workspace/training_03/models/my_ssd_resnet50_v1_fpn/pipeline.config`

Train the model:
```shell
# copy the script to run the training
cp training/TensorFlow/models/research/object_detection/model_main_tf2.py training/TensorFlow/workspace/training_03


# Following helps with OOMs:
TF_GPU_ALLOCATOR=cuda_malloc_async
# Windows:
set TF_GPU_ALLOCATOR=cuda_malloc_async

# start the training
cd training/TensorFlow/workspace/training_03
# this takes too much time without a GPU... I gave up on my MacBook Pro after 3.5 hours.
# On my Mac, per-step time at step #100 was 21.8 seconds.
# On a PC with GPU (Intel i7 10700F, Nvidia GeForce RTX 3070), per-step time at step #100 was 1.43 seconds. There's a ~15x speedup.
# On the PC, the training took 1 hour and 15 minutes.
python model_main_tf2.py --model_dir=models/my_ssd_resnet50_v1_fpn --pipeline_config_path=models/my_ssd_resnet50_v1_fpn/pipeline.config 

# sample output
# I1011 16:15:53.689812 19240 model_lib_v2.py:705] Step 13100 per-step time 1.322s
#INFO:tensorflow:{'Loss/classification_loss': 0.04079358,
# 'Loss/localization_loss': 0.006503464,
# 'Loss/regularization_loss': 0.34737733,
# 'Loss/total_loss': 0.39467436,
# 'learning_rate': 0.021092184}

# KILL when you see a totalLoss < 0.4.
# Although the advise was to have something < 1, I found that it doesn't work that way. I am not an expert though.

cd ../../../..
```

Once trained, upload it to Google Cloud Storage:
```shell
# install gsutil first
pip install gsutil==5.26

# make sure you do https://cloud.google.com/storage/docs/gsutil_install#authenticate first
# e.g. gsutil config
# I the following for authentication using a service account:
# used gsutil.config -e
# I went to the bucket and gave admin permissions to the service account on the bucket

# bucket is there already
gsutil cp -r training/TensorFlow/workspace/training_03/models/ knative-ai-demo/models/training_03
```

Export the model:
```shell
# copy the script to run the export
cp training/TensorFlow/models/research/object_detection/exporter_main_v2.py training/TensorFlow/workspace/training_03/

cd training/TensorFlow/workspace/training_03/
# export the model
python exporter_main_v2.py --input_type image_tensor --pipeline_config_path ./models/my_ssd_resnet50_v1_fpn/pipeline.config --trained_checkpoint_dir ./models/my_ssd_resnet50_v1_fpn/ --output_directory ./exported-models/training_03

# upload it to Google Cloud Storage:
gsutil cp -r training/TensorFlow/workspace/training_03/exported-models/training_03 gs://knative-ai-demo/exported-models/training_03

cd ../../../..
```

Info:
```shell
> python --version
Python 3.9.12


> pip freeze

absl-py==1.4.0
aiohttp==3.8.6
aiosignal==1.3.1
apache-beam==2.46.0
argcomplete==3.1.2
array-record==0.4.1
astunparse==1.6.3
async-timeout==4.0.3
attrs==23.1.0
avro-python3==1.10.2
bleach==6.1.0
boto==2.49.0
cachetools==5.3.1
certifi==2023.7.22
cffi==1.16.0
charset-normalizer==3.3.0
click==8.1.7
cloudpickle==2.2.1
colorama==0.4.6
contextlib2==21.6.0
contourpy==1.1.1
crcmod==1.7
cryptography==41.0.4
cycler==0.12.1
Cython==3.0.0
dill==0.3.1.1
dm-tree==0.1.8
docopt==0.6.2
etils==1.5.0
fastavro==1.8.4
fasteners==0.19
flatbuffers==23.5.26
fonttools==4.43.1
frozenlist==1.4.0
fsspec==2023.9.2
gast==0.4.0
gcs-oauth2-boto-plugin==3.0
gin-config==0.5.0
google-api-core==2.12.0
google-api-python-client==2.102.0
google-apitools==0.5.32
google-auth==2.23.2
google-auth-httplib2==0.1.1
google-auth-oauthlib==0.4.6
google-pasta==0.2.0
google-reauth==0.1.1
googleapis-common-protos==1.60.0
grpcio==1.34.1
gsutil==5.26
h5py==3.1.0
hdfs==2.7.2
httplib2==0.20.4
idna==3.4
immutabledict==3.0.0
importlib-metadata==6.8.0
importlib-resources==6.1.0
joblib==1.3.2
kaggle==1.5.16
keras==2.10.0
keras-nightly==2.5.0.dev2021032900
Keras-Preprocessing==1.1.2
kiwisolver==1.4.5
libclang==16.0.6
lvis==0.5.3
lxml==4.9.3
Markdown==3.5
MarkupSafe==2.1.3
matplotlib==3.8.0
monotonic==1.6
multidict==6.0.4
numpy==1.24.4
oauth2client==4.1.3
oauthlib==3.2.2
object-detection @ file:///C:/Users/ali/Desktop/ai-demo-training/training/TensorFlow/models/research
objsize==0.6.1
opencv-python==4.8.1.78
opencv-python-headless==4.8.1.78
opt-einsum==3.3.0
orjson==3.9.7
packaging==23.2
pandas==2.0.3
Pillow==10.0.1
portalocker==2.8.2
promise==2.3
proto-plus==1.22.3
protobuf==3.19.6
psutil==5.9.5
py-cpuinfo==9.0.0
pyarrow==9.0.0
pyasn1==0.5.0
pyasn1-modules==0.3.0
pycocotools @ git+https://github.com/philferriere/cocoapi.git@2929bd2ef6b451054755dfd7ceb09278f935f7ad#subdirectory=PythonAPI
pycparser==2.21
pydot==1.4.2
pymongo==3.13.0
pyOpenSSL==23.2.0
pyparsing==2.4.7
PyQt5==5.15.9
PyQt5-Qt5==5.15.2
PyQt5-sip==12.12.2
python-dateutil==2.8.2
python-slugify==8.0.1
pytz==2023.3.post1
pyu2f==0.1.5
pywin32==306
PyYAML==5.4.1
regex==2023.10.3
requests==2.31.0
requests-oauthlib==1.3.1
retry-decorator==1.1.1
rsa==4.7.2
sacrebleu==2.2.0
scikit-learn==1.3.1
scipy==1.11.3
sentencepiece==0.1.99
seqeval==1.2.2
six==1.15.0
tabulate==0.9.0
tensorboard==2.10.1
tensorboard-data-server==0.6.1
tensorboard-plugin-wit==1.8.1
tensorflow==2.10.1
tensorflow-addons==0.21.0
tensorflow-datasets==4.9.0
tensorflow-estimator==2.10.0
tensorflow-hub==0.15.0
tensorflow-io==0.31.0
tensorflow-io-gcs-filesystem==0.31.0
tensorflow-metadata==1.13.0
tensorflow-model-optimization==0.7.5
tensorflow-text==2.10.0
termcolor==1.1.0
text-unidecode==1.3
tf-models-official==2.10.1
tf-slim==1.1.0
threadpoolctl==3.2.0
toml==0.10.2
tqdm==4.66.1
typeguard==2.13.3
typing-extensions==3.7.4.3
tzdata==2023.3
uritemplate==4.1.1
urllib3==2.0.6
webencodings==0.5.1
Werkzeug==3.0.0
wrapt==1.12.1
yarl==1.9.2
zipp==3.17.0
zstandard==0.21.0

```