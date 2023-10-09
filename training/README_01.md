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
mkdir workspace/training_01
mkdir workspace/training_01/annotations
mkdir workspace/training_01/exported-models
mkdir workspace/training_01/images
mkdir workspace/training_01/images/test
mkdir workspace/training_01/images/train
mkdir workspace/training_01/models
mkdir workspace/training_01/pre-trained-models

touch workspace/.gitkeep
touch workspace/training_01/.gitkeep
touch workspace/training_01/annotations/.gitkeep
touch workspace/training_01/exported-models/.gitkeep
touch workspace/training_01/images/.gitkeep
touch workspace/training_01/images/test/.gitkeep
touch workspace/training_01/images/train/.gitkeep
touch workspace/training_01/models/.gitkeep
touch workspace/training_01/pre-trained-models/.gitkeep

cd ../..
```

Install labelImg for annotating images:
```shell
pip install labelImg
```

Annotate images:
```shell
labelImg training/TensorFlow/workspace/training_01/images
# In the tool:
# - Change save location to training/TensorFlow/workspace/training_01/images
# - Use class `knative`
# - Press `w` to draw a box, `a`/`d` to go to the previous/next image
```

Then manually partition images in `training/TensorFlow/workspace/training_01/images` into `test` and `train` folders.

Create the label map:
```shell
cat <<EOF >>training/TensorFlow/workspace/training_01/annotations/label_map.pbtxt
item {
    id: 1
    name: 'knative'
}
EOF
```

Create TensorFlow records:
```shell
pip install pandas

# create a directory for the upcoming script
mkdir -p training/TensorFlow/scripts/preprocessing
cd training/TensorFlow/scripts/preprocessing

# download the script to generate TFRecords
curl -L https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/_downloads/da4babe668a8afb093cc7776d7e630f3/generate_tfrecord.py -o generate_tfrecord.py

# Create train data:
python generate_tfrecord.py -x ../../workspace/training_01/images/train -l ../../workspace/training_01/annotations/label_map.pbtxt -o ../../workspace/training_01/annotations/train.record

# Create test data:
python generate_tfrecord.py -x ../../workspace/training_01/images/test  -l ../../workspace/training_01/annotations/label_map.pbtxt -o ../../workspace/training_01/annotations/test.record

cd ../../../..
```

Download pre-trained model:
```shell
cd training/TensorFlow/workspace/training_01/pre-trained-models

# download the model archive
curl -L http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8.tar.gz -o model.tar.gz
tar xvzf model.tar.gz

cd ../../../../..
```

Copy model config:
```shell
mkdir training/TensorFlow/workspace/training_01/models/my_ssd_resnet50_v1_fpn

cp training/TensorFlow/workspace/training_01/pre-trained-models/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8/pipeline.config training/TensorFlow/workspace/training_01/models/my_ssd_resnet50_v1_fpn/pipeline.config
```

Manually change the model config in `training/TensorFlow/workspace/training_01/models/my_ssd_resnet50_v1_fpn/pipeline.config`

Train the model:
```shell
# copy the script to run the training
cp training/TensorFlow/models/research/object_detection/model_main_tf2.py training/TensorFlow/workspace/training_01

# start the training
cd training/TensorFlow/workspace/training_01
# this takes too much time without a GPU... I gave up on my MacBook Pro after 3.5 hours.
# On my Mac, per-step time at step #100 was 21.8 seconds.
# On a PC with GPU (Intel i7 10700F, Nvidia GeForce RTX 3070), per-step time at step #100 was 1.43 seconds. There's a ~15x speedup.
# On the PC, the training took 1 hour and 15 minutes.
python model_main_tf2.py --model_dir=models/my_ssd_resnet50_v1_fpn --pipeline_config_path=models/my_ssd_resnet50_v1_fpn/pipeline.config

# sample output
# I0808 20:34:46.699280  2904 model_lib_v2.py:705] Step 2500 per-step time 1.065s
# INFO:tensorflow:{'Loss/classification_loss': 0.06834849,
#  'Loss/localization_loss': 0.01116436,
#  'Loss/regularization_loss': 0.21596497,
#  'Loss/total_loss': 0.29547784,
#  'learning_rate': 0.039953373}

# KILL when you see a totalLoss < 1

cd ../../../..
```

Once trained, upload it to Google Cloud Storage:
```shell
# make sure you do https://cloud.google.com/storage/docs/gsutil_install#authenticate first
# e.g. gsutil config
# I the following for authentication using a service account:
# used gsutil.config -e
# I went to the bucket and gave admin permissions to the service account on the bucket

# bucket is there already
gsutil cp -r training/TensorFlow/workspace/training_01/models/ gs://knative-ai-demo

```

Export the model:
```shell
# copy the script to run the export
cp training/TensorFlow/models/research/object_detection/exporter_main_v2.py training/TensorFlow/workspace/training_01/

cd training/TensorFlow/workspace/training_01/
# export the model
python exporter_main_v2.py --input_type image_tensor --pipeline_config_path ./models/my_ssd_resnet50_v1_fpn/pipeline.config --trained_checkpoint_dir ./models/my_ssd_resnet50_v1_fpn/ --output_directory ./exported-models/my_model

# upload it to Google Cloud Storage:
gsutil cp -r training/TensorFlow/workspace/training_01/exported-models/ gs://knative-ai-demo

cd ../../../..
```


Troubleshooting:

---

`Could not locate zlibwapi.dll. Please make sure it is in your library path`

Follow: https://stackoverflow.com/a/72458201

---

### Try on your machine

When you clone this repo, stuff above will be there for you, except some files that can't be checked in to Git because they are big.

If you want to start from scratch and do the training, start by downloading pre-trained model:
```shell
cd training/TensorFlow/workspace/training_01/pre-trained-models

# download the model archive
curl -L http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8.tar.gz -o model.tar.gz
tar xvzf model.tar.gz

cd ../../../../..
```

If you don't want to train on top of the model I've trained, download the model I trained:
```shell

gsutil cp -r gs://knative-ai-demo/models/my_ssd_resnet50_v1_fpn/ training/TensorFlow/workspace/training_01/models/

```

If you're not interested in any of the training, but you want to get the exported model:
```shell
gsutil cp -r gs://knative-ai-demo/exported-models/my_model training/TensorFlow/workspace/training_01/exported-models/
```
