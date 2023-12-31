build:
	docker build -t file_server_image:$(shell ./increment_version.sh) .

tag:
	docker tag file_server_image:$(shell cat version) 192.168.0.2:5000/file_server_image:$(shell cat version)

push:
	docker push 192.168.0.2:5000/file_server_image:$(shell cat version)

update:
	sed -i -r "s/file_server_image:[0-9]+\.[0-9]+\.[0-9]+/file_server_image:$(shell cat version)/g" file_server_deployment.yaml

commit:
	git checkout -b "release/$(shell cat version)"
	git add file_server_deployment.yaml
	git commit -m "Released version $(shell cat version)"
	git checkout master
	echo

run:
	docker run -d -p 60005:8000 --name file_server_container file_server_image:$(shell cat version)

prod:
	$(MAKE) build tag push update commit update