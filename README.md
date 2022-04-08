# musOK-chart-server
Server for uploading and downloading charts.

Needs a PostgreSQL database.

## Usage

### Ubuntu

Install dependency requirements:
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

Create and configure `.env` file:
```
# Database configuration
DB_USER=<db user>
DB_PASSWORD=<password>
DB_LOCATION=<db ip>
DB_NAME=<db name>

# Store configuration
STORE_NAME="Your store name"
STORE_DESCRIPTION="Your store description"

# Security
SECRET_KEY = <you can generate your key with 'openssl rand -hex 32'>
ALGORITHM = <encoding algorithm for jwt, for example "HS256">
ACCESS_TOKEN_EXPIRE_MINUTES = <how long should any auth token be valid in minutes>
```

Finally, run:
```
uvicorn main:app --host <db ip>
```
