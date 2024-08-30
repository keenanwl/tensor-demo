# tensor-demo
A demo project for verifying the following tech stack:
* React
* Python/Flask API
* Python/TensorFlow model training
* TensorFlow Serving
* Kubernetes / Docker
* Terraform
* Ansible

For demo purposes only: there are several security issues.

## Development
### Train & Serve on Linux (maybe mac?) [Locally]
> Dependency: [Nividia Toolkit for docker host](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
1. Run `make up` to train the model
2. Copy the saved model to the host (container ID: `docker ps`) `docker cp <container_id>:/app/saved_model ./`
3. Version the model `mkdir -p ./demo_model_server/1 && cp ./saved_model ./demo_model_server/1`
4. Serve locally with TensorFlow Serving
`docker run -it --rm -p 8501:8501 -v ./demo_model_server:/models/model tensorflow/serving:latest --build`
5. Running at: `http://localhost:8501/v1/models/model:predict` 

### Run the API server [Locally]
1. `DEFAULT_SERVER_IP='localhost:8501' python3 serve.py`
2. You can now fire manual requests: 
```bash
# Comitted token only for demo purposes
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Token: wApHyPeLdaNtORDownsEPIcKinARTHO" \
  -d '{
    "seed_text": "John: How are you, Mike?",
    "sequence_length": 100,
    "num_chars_to_generate": 10
  }' \
  http://localhost:5000/generate_text
```
### Run the React frontend
1. `cd frontend && yarn serve`
2. Username: `weekend` Password: `playbook`
3. Enter a prompt, and the model generates the next X characters. 
   Currently, the API version outputs nonsense since the output inference interpretation is broken.

# Deploy
Current setup deploys to DigitalOcean for simplicity using Terraform & Ansible.
1. `cd deploy`
2. `terraform plan` && `terraform apply` 
3. Init kube context: `terraform output kubeconfig > ~/.kube/config`
4. Copy model to TensorFlow Serving pod:
```bash
# Get the name of the first pod for a deployment
POD_NAME=$(kubectl get pods -l app=tfserving-demo -o jsonpath="{.items[0].metadata.name}")

# Copy files to the pod
kubectl cp ./demo_model_server/1 ${POD_NAME}:/models/model/
```
5. Verify the model is available `curl -X GET "http://<external_ip>:8501/v1/models/model/metadata"`
6. Update `DEFAULT_SERVER_IP` in `deploy/ansible/templates/gunicorn.service.j2` 
(this would ideally be automatic in a product deploy)
7. Deploy server config, frontend and API `cd deploy/ansible && make deployconfig`

## Optionally restart TensorFlow Serving (clears ephemeral FS)
`kubectl rollout restart deployment tfserving-demo`


