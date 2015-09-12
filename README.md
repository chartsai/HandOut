# HandOut
Welcome to <b>HandOut</b>!

# Pre-require pacakges
* MySQLite server
* python 2.7+

# Install Required Packages
## tornado
```
pip install -U tornado
```
## sqlalchemy
```
pip install -U sqlalchemy
```
## mysql-connector
```
pip install -U --allow-external mysql-connector-python mysql-connector-python
```

## unoconv
### Ubuntu
```
apt-get install unoconv
```
### OS X
```
brew install unoconv
```

### (Note: Required Package versions)
* unoconv 0.6
* python-tornado 4.2.1
* python-sqlalchemy 1.0.8
* python-mysql.connector 2.0.4

# Usege
TODO...

# Commands
* `python -m HandOut.app`  # start server
* `python -m HandOut.initDB` # Init Database.Create All Table.
* `python -m HandOut.DropDB` # Drop Database.Delete All Table.

# URL memo

* PREFIX/present # Query all presentation around 1 KM.
* PREFIX/present/[id] # preview a presentation.
* PREFIX/present/submit # Upload a new presentation
* PREFIX/present/submit/[id] # Edit a exist presentation

* Current download link: PREFIX/download/[uuid]/[real_file_name] # A URL for download.
