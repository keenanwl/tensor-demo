# Configure the DigitalOcean Provider
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# Create a new Kubernetes cluster
resource "digitalocean_kubernetes_cluster" "tfserving_cluster" {
  name    = "tfserving-demo-cluster"
  region  = var.region
  version = "1.29.8-do.0"

  node_pool {
    name       = "worker-pool"
    size       = "s-1vcpu-2gb"
    node_count = 1  # Only one node for demo
  }
}

# Configure the Kubernetes provider
provider "kubernetes" {
  host                   = digitalocean_kubernetes_cluster.tfserving_cluster.endpoint
  token                  = digitalocean_kubernetes_cluster.tfserving_cluster.kube_config[0].token
  cluster_ca_certificate = base64decode(digitalocean_kubernetes_cluster.tfserving_cluster.kube_config[0].cluster_ca_certificate)
}

# Create a Kubernetes deployment for TensorFlow Serving
resource "kubernetes_deployment" "tfserving" {
  metadata {
    name = "tfserving-demo"
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "tfserving-demo"
      }
    }

    template {
      metadata {
        labels = {
          app = "tfserving-demo"
        }
      }

      spec {
        container {
          image = "tensorflow/serving:latest" # Use a version in production
          name  = "tfserving"

          port {
            container_port = 8501
          }

          # For demo purposes, we're using an emptyDir volume
          # In a real scenario, you'd want to use a persistent volume
          volume_mount {
            name       = "model-volume"
            mount_path = "/models/model"
          }

          args = ["--model_base_path=/models/model"]
        }

        # emptyDir so we can upload our model
        volume {
          name = "model-volume"
          empty_dir {}
        }
      }
    }
  }
}

# Create a Kubernetes service to expose the deployment
resource "kubernetes_service" "tfserving" {
  metadata {
    name = "tfserving-demo"
  }

  spec {
    selector = {
      app = kubernetes_deployment.tfserving.spec[0].template[0].metadata[0].labels.app
    }

    port {
      port        = 8501
      target_port = 8501
    }

    type = "LoadBalancer"
  }
}

# Variables
variable "do_token" {
  description = "DigitalOcean API Token"
  type        = string
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "ams3"
}

# Outputs
output "cluster_endpoint" {
  value = digitalocean_kubernetes_cluster.tfserving_cluster.endpoint
}

output "kubeconfig" {
  value     = digitalocean_kubernetes_cluster.tfserving_cluster.kube_config[0].raw_config
  sensitive = true
}

output "loadbalancer_ip" {
  value = kubernetes_service.tfserving.status[0].load_balancer[0].ingress[0].ip
}

output "droplet_ip" {
  value = digitalocean_droplet.ubuntu_instance.ipv4_address
}