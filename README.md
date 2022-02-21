# musOK-chart-server
Server for uploading and downloading charts.

Needs a PostgreSQL database.

## Installation

### Ubuntu

Install requirements:
```
pip install -r requirements.txt
```

Install psycopg2
```
sudo apt-get install python-psycopg2
```

Install uvicorn:
```
sudo apt-get install uvicorn
```

Create and cnfigure `.env` file:
```
DB_USER=<db user>
DB_PASSWORD=<password>
DB_LOCATION=<db ip>
DB_NAME=<db name>
```

Finally, run:
```
uvicorn main:app --host <db ip>
```
