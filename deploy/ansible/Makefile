deployconfig:
	(cd ../../frontend/tensor-demo/ && yarn build)
	ansible-playbook -i hosts.cfg deploy_api_app.yml -u root --private-key=~/.ssh/id_terraform