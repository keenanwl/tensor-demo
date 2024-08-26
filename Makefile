up:
	sudo docker compose up -d
	sleep 2 # or whatever makes sense
	sudo docker exec -it tensorflow_gpu_container /bin/bash