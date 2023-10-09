Upload the model in a way that Kserve would like to have (see https://console.cloud.google.com/storage/browser/kfserving-examples/models/tensorflow/flowers as an example directory structure):
```shell

mkdir -p kserve_test/models/knative_01/

cp -R training/TensorFlow/workspace/training_01/exported-models/training_01/saved_model kserve_test/models/knative_01/0001

# upload to Google Cloud
gsutil cp -r kserve_test/models/knative_01/ gs://knative-ai-demo/kserve-models/
```

Install Kserve:
```shell
curl -s "https://raw.githubusercontent.com/kserve/kserve/release-0.10/hack/quick_install.sh" | bash
```

Do a sanity check with another simple service first:
```shell
kubectl create namespace kserve-test

kubectl apply -n kserve-test -f - <<EOF
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "sklearn-iris"
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "gs://kfserving-examples/models/sklearn/1.0/model"
EOF

# check status
kubectl get inferenceservices sklearn-iris -n kserve-test

# port forward
INGRESS_GATEWAY_SERVICE=$(kubectl get svc --namespace istio-system --selector="app=istio-ingressgateway" --output jsonpath='{.items[0].metadata.name}')
kubectl port-forward --namespace istio-system svc/${INGRESS_GATEWAY_SERVICE} 8080:80

export INGRESS_HOST=localhost
export INGRESS_PORT=8080

SERVICE_HOSTNAME=$(kubectl get inferenceservice sklearn-iris -n kserve-test -o jsonpath='{.status.url}' | cut -d "/" -f 3)
curl -H "Host: ${SERVICE_HOSTNAME}" "http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/sklearn-iris:predict" -d '{"instances": [[6.8,  2.8,  4.8,  1.4], [6.0,  3.4,  4.5,  1.6]]}'

> {"predictions": [1, 1]}
```

Run custom model:
```shell

kubectl create namespace knative-ai-demo

kubectl apply -n knative-ai-demo -f - <<EOF
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "demo01"
spec:
  predictor:
    tensorflow:
      storageUri: "gs://knative-ai-demo/kserve-models/knative_01"
      resources:
        limits:
          cpu: "5"
          memory: 12Gi
        requests:
          cpu: "5"
          memory: 12Gi
EOF

# check status
# it will take some time to download the model
kubectl get inferenceservices demo01 -n knative-ai-demo

SERVICE_HOSTNAME=$(kubectl get inferenceservice demo01 -n knative-ai-demo -o jsonpath='{.status.url}' | cut -d "/" -f 3)

# prepare request
# call with a proper but small image
# image path relative to repo root
IMAGE_PATH="./tensorflow_serving_test/test_smaller.jpeg"
# IMAGE_DATA will hold the image data as a list of lists of lists
IMAGE_DATA=$(python -c "from PIL import Image;import os;import numpy as np;print(np.array(Image.open(os.path.join(os.getcwd(), '${IMAGE_PATH}'))).tolist())")

INFERENCE_START=$(date +%s.%N)

# call the inference, which will return a JSON with the predictions
# there can be too many results, so, let's not print them right now
INFERENCE_RESULT=$(curl -H "Host: ${SERVICE_HOSTNAME}" "http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/demo01:predict" -d "{\"instances\": [ ${IMAGE_DATA} ]}")

INFERENCE_END=$(date +%s.%N)
DIFF=$(echo "$INFERENCE_END - $INFERENCE_START" | bc)
echo "Inference took ${DIFF} seconds."

PREDICTIONS=$(echo ${INFERENCE_RESULT} | jq '.predictions[0]')

echo "Made $(echo ${PREDICTIONS} | jq '.num_detections') detections in the image."

# print the information about the first detection
echo "First detection box: "
echo ${PREDICTIONS} | jq '.detection_boxes[0]'

echo "First detection score: "
echo ${PREDICTIONS} | jq '.detection_scores[0]'
```

Some links:
- https://kserve.github.io/website/0.10/modelserving/v1beta1/tensorflow/
- https://console.cloud.google.com/storage/browser/kfserving-examples/models/tensorflow/flowers
