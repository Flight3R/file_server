docker build -t http_server_image .

docker run -d -p 60005:8000 --name http_server_container http_server_image

sudo firewall-cmd --zone=public --add-port=60005/tcp
