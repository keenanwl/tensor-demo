variable "ssh_public_key_path" {
  description = "Path to the public SSH key file"
  type        = string
  default     = "~/.ssh/id_terraform.pub"
}

resource "digitalocean_ssh_key" "terraform" {
  name       = "keenan-terraform"
  public_key = file(var.ssh_public_key_path)
}

resource "digitalocean_droplet" "ubuntu_instance" {
  image  = "ubuntu-24-04-x64"
  name   = "ubuntu-smallest-instance"
  region = var.region
  size   = "s-1vcpu-1gb"  # This is the smallest available size
  ssh_keys = [digitalocean_ssh_key.terraform.id]
}

# Define a locals block for the droplet
locals {
  droplets = [
    {
      name = digitalocean_droplet.ubuntu_instance.name
      ipv4_address = digitalocean_droplet.ubuntu_instance.ipv4_address
    }
  ]
}

# Create hosts.cfg file for Ansible
resource "local_file" "hosts_cfg" {
  content = templatefile("${path.module}/templates/hosts.tpl",
    {
      droplets = local.droplets
    }
  )
  filename = "./ansible/hosts.cfg"
}