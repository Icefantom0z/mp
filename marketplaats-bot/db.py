import sqlite3
import pathlib
import traceback
import os
from dotenv import load_dotenv


load_dotenv()


class DB:
    """
    Main database repository
    """

    def __init__(self, db_name: str, db_path: pathlib.Path = None):
        """
        Creates a database connection object
        """
        self.db_name = db_name
        self.db_path = db_path
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row

    def init(self):
        """
        Run an init script to create tables and indices. Caller should make sure if database file exists or not in a certain path.
        init() should only be called if file does not already exist
        """
        path = (
            "/code/marketplaats-bot/migrations/init.sql"
            if os.environ.get("DB_PATH")
            else "./migrations/init.sql"
        )
        with open(path, "r") as file:
            data = file.read()

            try:
                cursor = self.conn.cursor()
                cursor.executescript(data)
                print("ran init")
            except Exception as e:
                print(f"Error occured while running init query: {e}")

    def insert_listing(self, data) -> bool:
        """
        insert a Listing object into the database. Returns True if the passed data was inserted. Else False
        """
        cur = self.conn.cursor()
        try:
            # check if the key already exists
            res = cur.execute(
                "select * from Listings where listing_id = ?", (data.get("listing_id"),)
            )
            row = res.fetchone()

            if row is None:
                cur.execute(
                    "INSERT INTO Listings VALUES (:listing_id,:listing_title,:listing_vip_url,:listing_keyword,:tstep);",
                    data,
                )
                self.conn.commit()
                print(f"Inserted into Listings {data.values()}\n")
                return True

            else:
                print(
                    f"Item with key {data.get("listing_id")} already present, skipping"
                )
                return False

        except Exception as e:
            print(f"error occured while inserting into Listing: {e}")
            print(traceback.print_exc())

    def fetch_all_listings(self, query):
        """
        fetch all the objects from the Listings table for a particular keyword
        """
        cur = self.conn.cursor()
        try:
            res = cur.execute(
                "select * from Listings where listing_keyword= ?", (query,)
            )
            return res.fetchall()
        except Exception as e:
            print(f"error in fetch_all: {e}")
            return []

    def insert_keyword(self, keyword: str) -> bool:
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO Keywords VALUES (:keyword_id, :keyword);",
                {"keyword_id": None, "keyword": keyword},
            )
            self.conn.commit()
            print(f"Inserted into keywords {keyword}\n")

            return True

        except Exception as e:
            print(f"error occured while inserting into keywords: {e}")
            print(traceback.print_exc())

            return False

    def fetch_keywords(self) -> list:
        """
        fetch all keywords from Keywords table
        """
        cur = self.conn.cursor()
        try:
            res = cur.execute("select * from keywords")
            return res.fetchall()
        except Exception as e:
            print(f"error occured while fetching all keywords: {e}")
            print(traceback.print_exc())
            return None

    def delete_keyword(self, keyword: str) -> bool:
        """
        Delete a given keyword from the keyword table
        """
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM Keywords where keyword = ?", (keyword,))
            self.conn.commit()

            return True

        except Exception as e:
            print(f"error occured while deleting from keywords: {e}")
            print(traceback.print_exc())

            return False
