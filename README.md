# mlops-pytorch-pipeline
for the given work of mlops
Readme.md details

My github repo: https://github.com/prageetaeron/mlops-pytorch-pipeline 
git clone https://github.com/prageetaeron/mlops-pytorch-pipeline.git
cd mlops-pytorch-pipeline
git checkout -b develop
from local hot copy
scp /home/prageet/Documents/IITM_Class/MLOps/Assignment_3/PrimaryFiles da25g518@164.52.205.84:/mlops-pytorch-pipeline/Assignment_3

cd ~/mlops-pytorch-pipeline/Assignment_3
mkdir -p data checkpoints
ls -R
systemctl --user start docker
docker build -f docker/Dockerfile.train -t mlops-train:v1 .

#run local training test
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/checkpoints:/app/checkpoints \
  mlops-train:v1
  
ls -lh checkpoints/
#Next, build the serving container image:

docker build -f docker/Dockerfile.serve -t mlops-serve:v1 .
docker rm -f local-serve 2>/dev/null

docker run -d \
  --name local-serve \
  -p 8148:8080 \
  -v $(pwd)/checkpoints:/app/checkpoints \
  mlops-serve:v1

# test prediction endpoint
curl -X POST http://localhost:8148/predict -F "image=@sample.jpg"
  
#for week 1
# 1. Check modified files
git status

# 2. Stage code and configuration changes
git add requirements/ docker/ configs/ src/

# 3. Commit and push
git commit -m "Fix CPU PyTorch dependencies and NumPy compatibility"
git push origin main

Now stop and remove docker 
docker rm -f local-serve
#Running kubernetes from local machine
sudo systemctl start docker, sudo chmod 666 /var/run/docker.sock, and minikube start

minikube image load mlops-train:v1
minikube image load mlops-serve:v1

minikube image ls | grep mlops

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/training_job.yaml

# Get namespace name and running pods
kubectl get pods -A
# to view real time logs
kubectl logs -f ml-training-job-6sv6b -n ml-training

kubectl apply -f k8s/serving-deployment.yaml 
kubectl apply -f k8s/serving-service.yaml 
kubectl apply -f k8s/hpa.yaml








Report on MLOPs Assignment-3

I was able to run the Docker assignment on the given server provided by IITM, however, the space on the server was not sufficient and I was forced to run the kubernetes assignment on my local machine after a lot of challenges. During the docker training I constantly faced the challenge of cpu vs gpu versions, which i had to clarify from documentation and I chose only the cpu version given the resources. The basic pytorch code was not very difficult to write and I could check it offline as well. However on spinning our docker train , the training was extremely slow creating multiple timeouts for me. Ultimately the train and serve containers worked and I have captured the requisite screenshots for the runs. Both the docker and k8 local runs and their screen shots have been captured.  

Verification for the Docker Section:
# Build training image
docker build -f docker/Dockerfile.train -t mlops-train:v1 .

# Run training with mounted volumes
docker run --rm \
-v $(pwd)/data:/app/data \
-v $(pwd)/checkpoints:/app/checkpoints \
mlops-train:v1


# Build serving image
docker build -f docker/Dockerfile.serve -t mlops-serve:v1 .



# Run serving
docker run --rm -p 8148:8080 \
-v $(pwd)/checkpoints:/app/checkpoints \
mlops-serve:v1



# Test prediction endpoint
curl -X POST http://localhost:8080/predict \
-F "image=@test_image.png"


Kubernetes Section:

Demonstrate the full workflow running on your Kubernetes cluster:
1 Apply all manifests:
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/training-job.yaml


All manifests running

The actual pods running while training

The training post k8 initiation 



2 Once training completes, deploy the serving layer:
kubectl apply -f k8s/serving-deployment.yaml
kubectl apply -f k8s/serving-service.yaml
kubectl apply -f k8s/hpa.yaml



3 Verify pods are running and healthy:
kubectl get pods -n ml-training
kubectl describe deployment model-serving -n ml-training





Test the prediction endpoint:
# Port-forward for local testing
kubectl port-forward svc/model-serving 8080:80 -n ml-training
# Send a prediction request
curl -X POST http://localhost:8080/predict \
-F "image=@sample.jpg"






