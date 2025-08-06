# BEGIN AUTO-INJECT:DB_METHODS

def connect_to_postgresql(self):
    db_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    logging.info(f"BANCO DE DADOS >>> PRODUÇÃO -> : {db_url}")
    return db_url

def connect_to_postgresql_dev(self):
    db_url = f"postgresql://{self.db_dev_user}:{self.db_dev_password}@{self.db_dev_host}:{self.db_dev_port}/{self.db_dev_name}"
    logging.info(f"BANCO DE DADOS >>> DEV -> : {db_url}")
    return db_url

# END AUTO-INJECT:DB_METHODS
