import mysql.connector
# from mysql.connector import errorcode
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)

class DbHandler:
    def __init__(self, config, persistence=False, log_level: int=color.DEBUG):
        self.config = config
        self.persistence = persistence
        logging.setLevel(log_level)

    def __enter__(self):
        logging.debug("[DB] Connecting to database...")
        if self.persistence:
            try:
                self.mydb = mysql.connector.connect(
                    host=self.config["host"],
                    port=self.config["db_port"],
                    user=self.config["username"],
                    password=self.config["password"],
                    database="pds",
                    # auth_plugin = self.config["root_password"],
                )
                self.mycursor = self.mydb.cursor()
                return self
            except:
                # raise Exception("[DB] Unable to connect.")
                logging.error(f"[DB] Unable to connect.")
        else:
            try:
                self.mydb = mysql.connector.connect(
                    host=self.config["host"],
                    port=self.config["db_port"],
                    user=self.config["username"],
                    password=self.config["password"],
                    # auth_plugin = self.config["root_password"],
                )
                self.mycursor = self.mydb.cursor()
                return self
            except Exception as e:
                logging.error(f"[DB] Unable to connect. #{e}")

    def createDatabase(self):
        self.mycursor.execute("CREATE DATABASE IF NOT EXISTS pds")

    def createTable(self):
        if not self.persistence:
            try:
                self.mycursor.execute("USE pds")
                self.mycursor.execute("DROP TABLE IF EXISTS devices")
                self.mycursor.execute("CREATE TABLE devices ("
                                      "HASH VARCHAR(256),"
                                      "MAC VARCHAR(256), "
                                      "TID INTEGER(200), "
                                      "ROOMID VARCHAR(16),"
                                      "X DECIMAL(7, 4), "
                                      "Y DECIMAL(7 ,4),"
                                      "SN INTEGER(200),"
                                      "HTCI VARCHAR(50),"
                                      "primary key (TID, HASH)"
                                      ")")
            except Exception as e:
                logging.fatal(e)
                exit(1)
        logging.info("table created/reset with success")


    def insert (self, value):
        mycursor = self.mydb.cursor()
        # sql_formula = "INSERT INTO devices (HASH, MAC, TID, ROOMID, X, Y, SN, HTCI) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        # https://stackoverflow.com/questions/27787472/how-to-avoid-duplicate-entries-in-a-mysql-database-without-throwing-an-error
        sql_formula = "INSERT IGNORE INTO devices (HASH, MAC, TID, ROOMID, X, Y, SN, HTCI) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            mycursor.execute("USE pds")
            logging.debug(f"Trying to insert this: {len(value)=}")
            mycursor.executemany(sql_formula, value)
            self.mydb.commit()
        except Exception as e:
            logging.error('Something went wrong', exc_info=e)
            self.mydb.rollback()
            # logging.error(color.bg_blue('Try not doing "self.mydb.rollback()"'))
        mycursor.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mydb.close()

