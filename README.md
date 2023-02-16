# MLM Mobileye Library Management
library management system that stores the library catalog tracks book check-outs and check-ins, and tracks due dates and fines.

## Documentation
see the [design doc](/docs/design.md) for more details about the system
see [APIs docs](https://app.swaggerhub.com/apis/mibenami/default-title/0.1) too  

## How to run
### use docker
you can pull an image or create your own one
#### pull image from [docker hub](https://hub.docker.com/r/mibenami/library_management)
````
docker pull mibenami/library_management:v1
````
#### create an image
clone the git repo
````
git clone https://github.com/Michal-BenAmi/Library.git
````
build docker image
````
docker build -t lib-image:v1 .
````
#### run the image
run the image you download / create
````
docker run --name lib-container -p 5000:5000 lib-image:v1
````
now you can do curl do requests to the server via port 5000.

if you have issues to access from your machine you can run a new command in a running container, and run the curls from there
````
docker exec -it lib-container /bin/bash
````
### run the code on your local machin
in case you want to run locally, clone the code
````
git clone https://github.com/Michal-BenAmi/Library.git
pip3 install -r requirements.txt
````
make sure you have a running mySql with DB **library_management**, user **libuser**, password **library123**

it can be done by
````
CREATE USER 'libuser'@'%' IDENTIFIED BY 'library123';
GRANT ALL PRIVILEGES ON *.* TO 'libuser'@'%';
FLUSH PRIVILEGES;
CREATE DATABASE library_management;
````
## some cURLs
create user admin
````
curl --location --request POST 'http://127.0.0.1:5000/api/users' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic Uml2a2EgR2ltOlJpdmthR2ltMTIzNDU=' \
--data-raw '{
"username": "Rivka Gim",
"email": "RivkaGim@gmail.com",
"password": "RivkaGim12345",
"is_admin": true
}'
````
create regular user

````
curl --location --request POST 'http://127.0.0.1:5000/api/users' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic Sm9uaSBMZXZ5OkpvbmlMZXZ5MTIz' \
--data-raw '{
"username": "Joni Levy",
"email": "JoniLevy@example.com2",
"password": "JoniLevy123"
}'
````

Add new book:
````
curl --location --request POST 'http://127.0.0.1:5000/api/books' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic Uml2a2EgR2ltOlJpdmthR2ltMTIzNDU=' \
--data-raw '    {
    "title":"Lord of the Flies",
    "author":"William Golding"
    }'
````
get books with filter:
````
curl --location --request GET 'http://127.0.0.1:5000/api/books?author=William%20Golding' \
--header 'Content-Type: application/json' \
--data-raw '{
"title":"Book Title",
"author":"Book Author"
}'
````
checkout a book:
````
curl --location --request POST 'http://127.0.0.1:5000/api/checkout' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic Sm9uaSBMZXZ5OkpvbmlMZXZ5MTIz' \
--data-raw '{
"book_id": "2"
}'
````
