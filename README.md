
# Installation and Setup Instructions (Using Docker)

## Installing Docker

- Download and install docker from [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- [Installation guide](https://docs.docker.com/desktop/install/windows-install/#install-docker-desktop-on-windows)

## Building the Project (One time setup)

1. Download and extract the source code.
  - Click `Code` and choose `Download Zip`.

2. Create a file named `.env` at project's root with following contents

```
NEO4J_URL=bolt://fluantigen-neo4j-db
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD='<database password>'
```

3. Create a file named `.env.neo4j` at project's root with following contents

```
NEO4J_AUTH='neo4j/<database password (same as in .env)>'
```

4. Open Command prompt or Power Shell, run as administrator.
  - Go to Start -> Search for cmd -> Right click and choose "Run as administrator".

5. `cd` into the project's directory.
  - (or) Copy the path of project's folder from File explorer, and paste `(ctrl + insert)` it in command prompt after `cd`.

6. Run the command `docker compose build --no-cache`. Wait untill it builds the images for Neo4j and the backend.

## Run the project

Run the command `docker compose up` (From inside project's root folder). It will spin up the service containers for Neo4j and backend.

## Import data into database (One time)

Open another instance of CMD or Power shell (as administrator) and run the comman `docker exec -it fluantigen-web-server python3 /neo4j-import/run.py`

## Stop the project

Run the command `docker compose down`. It will stop the services.

---
--- Legacy instructions (Without docker) ---
---

# Demo

## Installation
1. Install neo4j following the instruction on https://neo4j.com/docs/operations-manual/current/installation/
2. pip install neo4j
3. pip install -r flask-import/requirements.txt

## Start the Service
1. go to the dir you install neo4j and locate bin. Execute "./neo4j start"
<img width="485" alt="image" src="https://user-images.githubusercontent.com/61766749/172868376-5fb8b07a-2769-459d-8e96-8d0c8761b56d.png">  
2. cd neo4j-import && python run.py (The password and account number should be aligned with the localhost server's you loged in)<br>
<br>
default user:neo4j,password:123456 in this repo<br>
(Or in demo folder, you need to change the user and password in ./js/graph.js in line 4-5 and 26-28, in ./database/indel.html in line 366-367.) <br>
<br>
3. cd flask-import && python webserver.py (remember move model file to this dir like cnn_saved,cnn_saved_H3N2)  <br>
4. cd demo && open index.html  


## Notes
1. Remember to change the port number in file if the port is used by other application.
# ai
