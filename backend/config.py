# Configuration for SSH and PostgreSQL connection
DATABASE_CONFIG = {
    "ssh_host": "172.20.224.175",  # SSH server IP
    "ssh_user": "devuser",  # SSH username
    "ssh_password": "dev@cmb123",  # SSH password
    "pg_host": "172.20.224.149",  # PostgreSQL host IP
    "port": 5444,  # PostgreSQL port
    "user": "mubasher_oms",  # PostgreSQL user
    "database": "edb",  # PostgreSQL database name
    "pg_password": "password"  # PostgreSQL password
}

PATH_CONFIG = {
    "base_path" : "/u01/edb/as15/data/pg_wal",
    "base_path_archive" : "/u01/edb/as15/archivedir"
}