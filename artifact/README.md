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

## Folder Structure

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

## Initial Setup

To complete a full run of experiment, there are four components need to be set up.

### Local Database

The local database stores the captured API traffic. We provide a `Dockerfile` to simplify the process to set it up. Trailblazer can also work if you prefer not to use Docker, in which case you will need to have a Postgres database running, and edit the `server.py` accordingly to match your HOST, PORT, TABLE_NAME, DB_USERNAME and DB_PASSWORD. 

To set up the database using Docker, follow the steps:

- Make sure Docker is installed on your device. You can find information from [official documentation](https://docs.docker.com/get-started/get-docker/).
- `cd` into `database` folder, run `docker compose up`. 
- Once completed, you should have a Postgres database running as a Docker container, and it can be accessed via `127.0.0.1:5432`. 

Note: if you prefer to use a different port other than 5432, please edit the `docker-compose.yml`, change line 11 to your desired port, such as `8888:5432`. If you do so, your database is accessible via `127.0.0.1:8888`. You will also need to edit the `DB_PORT` in `./trailblazer/constants.py` and `./server.py` to reflect this change. 

### Chrome Plugin

To install the Chrome plugin, please follow the below steps:

- Open Chrome. 
- At the top-right corner, click the three-dots icon.
- From the drop-down menu, select `Extensions` - `Manage extensions`.
- Make sure you are in developer mode so that you can load unpacked plugins. At the top-right corner, toggle `developer mode`.
- At the top-left area of the same page (extensions), there should be a button `load unpacked`. Click it and select the `./chrome_plugin/` folder.
- You should now have the plugin loaded. 

The plugin we provided in the `./chrome_plugin/` folder, is configured to only capture API traffic to IP addresses begin with either `192.168.` (represent a LAN setup) or `127.0.0` (localhost). This is to ensure only API traffic sends to locally deployed services will be captured and stored. Any API requests sending to `google.com`, `facebook.com` etc. which may include sensitive information (such as, your password) will NOT be stored. If you need to change this behaviour, please edit `./server.py` accordingly (e.g., comment out line 43-45).

### Trailblazer

The source code of Trailblazer is under `./trailblazer/`. We recommend using virtual environment to avoid any issues. 

- Create a virtual environment via `python3 -m venv .venv` (*nix, MacOS) or `python -m venv .venv` (Windows).
- Activate the vertual environment using `source .venv/bin/activate` (*nix, MacOS) or `.venv\Scripts\activate` (Windows).
- Install `Schemathesis` by `pip install schemathesis`.
- Install `psycopg2` by `pip install psycopg2`.
  - If encountering the error `pg_config executable not found`, fix by `sudo apt install libpq-dev python3-dev build-essential`
- Verify that Trailblazer can load all required dependencies by executing `tb.py` (`python3 tb.py`). It should display a banner and an error message saying "Invalid mode". 

### A Web Application Under Test

We deployed and evaluated Trailblazer on [Strapi](https://github.com/strapi/strapi), [Directus](https://github.com/directus/directus), [Ghost](https://github.com/TryGhost/Ghost) and [Cockpit](https://github.com/Cockpit-HQ/Cockpit). 

Instructions to deploy each web application can be found on the respective website. Further setup instructions for the development of Trailblazer are also provided below. 

## Development

To measure Trailblazer's code coverage and performance on the above applications, [C8](https://github.com/bcoe/c8) is installed on top of the web applications. Full setup instructions (windows) are provided below for Strapi, Ghost.

Installation and runtime instructions are provided for each application below.

### Strapi Install

Strapi's official [installation guide](https://github.com/strapi/strapi)

- Ensure [`Node.js`](https://nodejs.org/en) version >=20.0.0 and <=24.x.x is installed.
- `cd` into the location for Strapi to be installed.
- Install Strapi application by `npx create-strapi@latest` (Windows). Default config options are provided below (customisable):
  - What is the name of your project?: strapi
  - Please log in or sign up: Skip
  - Do you want to use the default database (sqlite) ?: Y
  - Start with an example structure & data?: Y
  - Start with Typescript?: Y
  - Install dependencies with npm?: Y
  - Initialize a git repository?: N
  - Participate in anonymouse A/B testing (to improve Strapi)?: N
- `cd` into installation folder `strapi` and run Strapi with `npm run develop` to verify installation. It should be accessible at `127.0.0.1:1337`
  - Enter validation credentials to create a (local) admin account for Strapi. Use a dummy username and password as this will be used to log in during testing.   
- Exit Strapi with `Ctrl + C`.
- `cd` into installation folder `strapi` and install c8 using `npm install --save-dev c8`
- Open `strapi/package.json` and add the script `"coverage": "c8 --all --reporter=text-summary --reporter=html strapi develop"`
- Open `strapi/src/index.ts` and paste:
```typescript
export default {
  async bootstrap({strapi}) {
    const SHUTDOWN_DELAY = 20000; // time in ms before shutting down Strapi

    setTimeout(async () => {
      await strapi.destroy();
      process.exit(0);
    }, SHUTDOWN_DELAY);
  },
};
```
- Run Strapi using `npm run coverage`. Upon reaching `SHUTDOWN_DELAY` Strapi will shutdown. A text summary of code covered will be printed and coverage report will be generated in `strapi/coverage`.

### Ghost Install

Ghost's official [installation guide](https://docs.ghost.org/install/local)

- Ensure [`Node.js`](https://nodejs.org/en) version 22.22.0 is installed.
- Install Ghost CLI with `npm install ghost-cli@latest -g`.
- `cd` into empty directory and install Ghost with `ghost install local`.
  - Upon successful installation, Ghost will attempt to start. Exit with `ghost stop`.
  - If encountering the error `Cannot find module 'sqlite3'`, fix by `npm install sqlite3`.
- Open `ghost/config.development.json` and replace `url: "http://localhost:2368/"` with `url: "http://127.0.0.1:2368"`
- Start Ghost with `ghost start`. Navigate to `127.0.0.1:2368/ghost` to set up admin credentials.
  - Enter site name, your name, email and password as desired. Use a dummy username and password as this will be used to log in during testing.  
- Install c8 using `npm install --save-dev c8`
- Open `ghost/versions/6.24/package.json` and paste `"coverage": "c8 --all --reporter=text-summary --reporter=html node index.js"` into scripts. 
- `cd` into `ghost/versions/6.24` and run `npm run coverage` to start Ghost.
- After tests are performed, exit Ghost with `Ctrl + C`. A coverage summary will be displayed and a coverage report will be generated in `ghost/coverage/`

## Usage

### Server
Start the docker database instance through the Docker desktop application. Alternatively, `cd` into `artifact/database` folder again and run `docker compose up`. 

In a terminal window, intialise the virtual environment. Then, `cd` into `artifact` and run `python3 server.py`. It runs an HTTP server at background, listening to port 8086. The Chrome plugin sends any captured API traffic to it and stores the API traffic in the database.

### Test Application
In a separate terminal window, start the preferred application to test. Open Google Chrome (with the traffic capturing plugin installed) and visit the deployed web application at `127.0.0.1:xxxx`. Log in to the web application's management interface using admin username and password (created during application setup) and manually explore the back-end (e.g. create / edit / delete resources). Any traffic on pages within `127.0.0.1:xxxx` will be captured. 

### Trailblazer - API Specification Inferral 
Once enough API traffic is collected (say, after ten minutes exploration), in a separate terminal window, initialise the virtual environment. `cd` into `artifact/trailblazer` and run `python3 tb.py s` to identify collected endpoints and infer request payloads. It should produce `[target].json` (inferred OpenAPI specification), `[target]_endpoints.txt` (a list of identified endpoints) and `[target].pkl` (our internal representation of request payload structure, used in mutations). 

### Trailblazer - Fuzzing and Code Coverage
To allow for the measurement of code coverage within the test application using C8, the test application must automatically shutdown after a set delay. As such, Trailblazer must complete its testing cycle within this delay. To adjust this delay, update the variable `SHUTDOWN_DELAY` in `[target]/index.ts` within the web application's config to allow adequate time to complete Trailblazer tests.

With the target application running, `cd` into `artifact/trailblazer` and run `python3 tb.py f [target]` (e.g. `python3 tb.py f 127.0.0.1`) to start the fuzzing process. Select the test application's corresponding port using `1, 2, 3 etc.` If the target application shuts down before Trailblazer tests are complete, increase `SHUTDOWN_DELAY`, restart the target application and try again.

When running `python3 tb.py f [target]`, use option `-n X` to set the maximum number of test cases generated by Schemathesis (default: 100), and `-m` to add mutations generated by Trailblazer (will produce and replace X/2 number of test cases). The option `-H YYY` adds a custom header (for authentication), for example, `-H "Authorization: Bearer eYj9..."`. The option `-r` generates payloads based on traffic captured from host (bypassing Schemathesis), and `-g` replays the exact traffic captured from host.

After `SHUTDOWN_DELAY` has passed, the system under test will shutdown and a coverage report will be generated by c8 in `[system]/coverage/index.html`.



## License

![](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/).
