build:
	docker build -t http_server_image:$(shell ./increment_version.sh) .
tag:
	docker tag http_server_image:$(shell cat version) 192.168.0.2:5000/http_server_image:$(shell cat version)
push:
	docker push 192.168.0.2:5000/http_server_image:$(shell cat version)
update:
	sed -i -r "s/http_server_image:[0-9]+\.[0-9]+\.[0-9]+/http_server_image:$(shell cat version)/g" http_server_deployment.yaml
commit:
	git checkout -b "release/$(shell cat version)"
	git add http_server_deployment.yaml
	git commit -m "Released version $(shell cat version)"
	git checkout master
run:
	docker run -d -p 60005:8000 --name http_server_container http_server_image:$(shell cat version)
prod:
	$(MAKE) build tag push update commit