# Use Ubuntu image
FROM ubuntu:20.04

# Set the working directory
WORKDIR /app
COPY . /app
# COPY src/ /app

# Update the system and install Python 3.11
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y software-properties-common
RUN apt-get install -y python3-pip

# Install requirements
RUN pip3 install -r requirements.txt

# Install MySQL server
RUN apt-get install -y mysql-server
RUN apt-get -y install python3-mysqldb

# Install curl
RUN apt-get -y install curl

# start sql and create the needed DB and user
RUN service mysql start && \
    mysql -u root -e "CREATE USER 'libuser'@'%' IDENTIFIED BY 'library123'; \
    GRANT ALL PRIVILEGES ON *.* TO 'libuser'@'%'; \
    FLUSH PRIVILEGES; \
    CREATE DATABASE library_management;"

# Set the default command to run when starting the container
CMD service mysql start && python3 run.py
