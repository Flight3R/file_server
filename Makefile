build:
	rm -rf docker-build-src
	mkdir docker-build-src
	cp -aL src/* docker-build-src/
	docker build -t file_server_image:$(shell ./increment_version.sh) .
	rm -rf docker-build-src

tag:
	docker tag file_server_image:$(shell cat version) 192.168.0.2:5000/file_server_image:$(shell cat version)

push:
	docker push 192.168.0.2:5000/file_server_image:$(shell cat version)

update:
	sed -i -r "s/file_server_image:[0-9]+\.[0-9]+\.[0-9]+/file_server_image:$(shell cat version)/g" deployment.yaml

run:
	docker run -d -p 60005:8000 --name file_server_container file_server_image:$(shell cat version)

commit:
	git add .
	git commit -m "deployment $(shell cat version)"

prod:
	$(MAKE) build tag push update commit
