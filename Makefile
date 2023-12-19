
build:
	docker build -t http_server_image .
tag:
	docker tag http_server_image 192.168.0.2:5000/http_server_image
push:
	docker push 192.168.0.2:5000/http_server_image
run:
	docker run -d -p 60005:8000 --name http_server_container http_server_image

