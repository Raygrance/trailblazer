```
  _________               __  __  __      __
 /___  ___/              /_/ / / / /     / /
    / /  ____  ____     __  / / / /_    / / ____   ____   ___    ____
   / /  / __/ / __ \   / / / / / __ \  / / / __ \ /_  /  / _ \  / __/
  / /  / /   / /_/ /  / / / / / /_/ / / / / /_/ /  / /_ / ___/ / /   
 /_/  /_/    \___/\_\/_/ /_/ /_____/ /_/  \___/\_\/___/ \___/ /_/    
```

# Trailblazer

Trailblazer is a practical end-to-end web API fuzzing tool.

The design of Trailblazer is described in our paper.

## Folder structure

```
Artifact
├── chrome_plugin: the Chrome plugin developed to capture API requests and responses (discussed in section 3.1)
│   └── *: there is no need to touch any file in this folder, the folder can be directly loaded into Chrome as a plugin
├── database: a Docker setup of Postgres database
|   ├── docker-compose.yml: the configuration to create a container running Postgres
│   └── init.sql: the initial setup script for the database, used by docker-compose.yml
├── trailblazer: the implementation of Trailblazer
|   ├── tests: content within this folder are generated and processed by Trailblazer
│   └── tb.py: the main executable (discussed in section 3.2 - 3.5)
├── README.md
├── server.py: a script to forward captured API traffic to a local database (see below for usage)
└── other folders: setup for example web applications
```

## Initial setup

To complete a full run of experiment, there are four components need to be set up.

### Local database

The local database stores the captured API traffic. We provide a `Dockerfile` to simplify the process to set it up. Trailblazer can also work if you prefer not to use Docker, in which case you will need to have a Postgres database running, and edit the `server.py` accordingly to match your HOST, PORT, TABLE_NAME, DB_USERNAME and DB_PASSWORD. 

To set up the database using Docker, follow the steps:

- Make sure Docker is installed on your device. You can find information from [official documentation](https://docs.docker.com/get-started/get-docker/).
- `cd` into `database` folder, run `docker compose up`. 
- Once completed, you should have a Postgres database running as a Docker container, and it can be accessed via `127.0.0.1:5432`. 

Note: if you prefer to use a different port other than 5432, please edit the `docker-compose.yml`, change line 11 to your desired port, such as `8888:5432`. If you do so, your database is accessible via `127.0.0.1:8888`. You will also need to edit the `DB_PORT` in `./trailblazer/constants.py` and `./server.py` to reflect this change. 

### Chrome plugin

To install the Chrome plugin, please follow the below steps:

- Open Chrome. 
- At the top-right corner, click the three-dots icon.
- From the drop-down menu, select `Extensions` - `Manage extensions`.
- Make sure you are in developer mode so that you can load unpacked plugins. At the top-right corner, toggle `developer mode`.
- At the top-left area of the same page (extensions), there should be a button `load uncompressed extension`. Click it and select the `./chrome_plugin/` folder.
- You should now have the plugin loaded. 

The plugin we provided in the `./chrome_plugin/` folder, is configured to only capture API traffic to IP addresses begin with either `192.168.` (represent a LAN setup) or `127.0.0` (localhost). This is to ensure only API traffic sends to locally deployed services will be captured and stored. Any API requests sending to `google.com`, `facebook.com` etc. which may include sensitive information (such as, your password) will NOT be stored. If you need to change this behaviour, please edit `./server.py` accordingly (e.g., comment out line 43-45).

### Trailblazer

The source code of Trailblazer is under `./trailblazer/`. We recommend using virtual environment to avoid any issues. 

- Create a virtual environment via `python3 -m venv .venv` (*nix, MacOS) or `python -m venv .venv` (Windows).
- Activate the vertual environment using `source .venv/bin/activate` (*nix, MacOS) or `.venv\Scripts\activate` (Windows).
- Install `Schemathesis` by `pip install schemathesis`.
- Install `psycopg2` by `pip install psycopg2`.
- Verify that Trailblazer can load all required dependencies by executing `tb.py` (`python3 tb.py`). It should display a banner and an error message saying "Invalid mode". 

### A web application under test

We deployed and evaluated Trailblazer on [Strapi](https://github.com /strapi/strapi), [Directus](https://github.com/directus/directus), [Ghost](https://github.com/TryGhost/Ghost) and [Cockpit](https://github.com/Cockpit-HQ/Cockpit). 

You can follow their instructions to deploy their web applications to be tested. 

## Usage

Run `./server.py` (`python3 server.py`), it runs an HTTP server at background, listens to port 8086. The Chrome plugin sends any API traffic to it, and it would store the API traffic into the database.

Open your web browser (with the traffic capturing plugin installed), visit the deployed web application (e.g. `127.0.0.1`). Log in to the web application's management interface and manually explore the back-end (e.g. create / edit / delete resources).

Once enough traffic is collected (say, after ten minutes exploration), run `./trailblazer s` and select a target to identify collected endpoints and infer request payloads (discussed in the paper, see section 3.2-3.4). It should produce `[target].json` (inferred OpenAPI specification), `[target]_endpoints.txt` (a list of identified endpoints) and `[target].pkl` (our internal representation of request payload structure, used in mutations). 

Run `./trailblazer f [target]` to start the fuzzing process. Use option `-n X` to set the maximum number of test cases generated by Schemathesis (default: 100), and `-m` to add mutations generated by Trailblazer (will produce and replace X/2 number of test cases). The option `-H YYY` to add custom header (for authentication), for example, `-H "Authorization: Bearer eYj9..."`. 


## License

![](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/).
