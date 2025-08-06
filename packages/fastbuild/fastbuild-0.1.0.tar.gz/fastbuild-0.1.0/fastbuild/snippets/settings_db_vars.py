# BEGIN AUTO-INJECT:DB_SETTINGS

# POSTGRES
self.db_user = os.getenv("DB_USER")
self.db_password = os.getenv("DB_PASSWORD")
self.db_host = os.getenv("DB_HOST")
self.db_port = os.getenv("DB_PORT", "5432")
self.db_name = os.getenv("DB_NAME")

# POSTGRES DEV
self.db_dev_user = os.getenv("DB_DEV_USER")
self.db_dev_password = os.getenv("DB_DEV_PASSWORD")
self.db_dev_host = os.getenv("DB_DEV_HOST")
self.db_dev_port = os.getenv("DB_DEV_PORT", "5432")
self.db_dev_name = os.getenv("DB_DEV_NAME")

# END AUTO-INJECT:DB_SETTINGS
