### Ad Insertion System

This repository contains a small example of an ad insertion system, deployable with Docker Compose.

## Setup

Run the docker-compose file to start the three components Flask, Redis and Postgres. The Postgres database
will start out empty, and can be filled by importing the advertising.sql dump file in the directory with the following command:

````md
docker exec postgres psql -U postgres my_db_name < dump.sql
````