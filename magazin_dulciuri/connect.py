import cx_Oracle
from magazin_dulciuri.config import username, password, dsn, encoding

def connect_to_oracle():
    print('Connecting to Oracle...')
    connection = None
    try:
        connection = cx_Oracle.connect(
            username,
            password,
            dsn,
            encoding=encoding)
        print(f'Successfully connected to {username}! Oracle Database version: ', connection.version)
    except cx_Oracle.Error as error:
        print('Error: ', error)
    return connection

