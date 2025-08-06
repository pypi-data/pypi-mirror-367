# dbt-run-api

Once installed allows DBT commands to be sent via an api call. 

### Installation:

```bash
pip install dbt-run-api
```

NOTE: currently the package comes with `dbt-postgres`. If you need another adapter then it would have to be install separately

### Set up:

After installing the package ensure your DBT project is set up correctly with all needed profile variables either explicitly defined or available as ENV-variables. 


### Execution:

#### Run server while in the same directory as your `dbt_project.yml':

```bash
uvicorn dbt_run_api:app
```

#### Ensure you DBT project has access to the database you have defined in profile.yml

#### Send call to endpoint:

```bash
curl --header 'Content-Type: application/json' \
     --request POST \
     http://localhost:8000/dbt \
    --data \
    '{  "cmd": "run",  "vars": {"test_var": "1", "date": "20240423"},  "target": "dev",  "threads" : 8,  "project-dir": "wab",  "profiles-dir": "wab",  "full-refresh": true}'
```

```bash
curl --header 'Content-Type: application/json' \
     --request POST \
     http://localhost:8000/dbt \
    --data \
    '{  "cmd": "test"}'
```

**Notes:** 
- commands are passed without `dbt` at the start. All dbt commands should be valid e.g `run`, `test`, et cetera. 
