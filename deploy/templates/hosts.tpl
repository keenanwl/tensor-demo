[webservers]
%{ for index, droplet in droplets ~}
app-server-${index + 1} ansible_host=${droplet.ipv4_address}
%{ endfor ~}

[all:vars]
ansible_python_interpreter=/usr/bin/python3