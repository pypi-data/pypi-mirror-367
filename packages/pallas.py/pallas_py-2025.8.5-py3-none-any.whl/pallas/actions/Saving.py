import os
import sqlite3 as sqlite
from datetime import datetime

from pallas.asset import Asset

class Saving:
    def __init__(self, file_name:str):
        self.file_name = file_name

    def append_asset_to_sqlite(self, file_name:str="", asset:Asset=Asset({})):
        if self.file_name and len(file_name) == 0:
            file_name = self.file_name
        if len(file_name) == 0 and not self.file_name:
            raise RuntimeError("Cannot append to file. No file_name passed to Saving.append_asset_to_sqlite(str,Asset)")
        specifier = asset.asset_specifier
        version = asset.asset_version
        base_url = asset._BaseURL
        relative_path = asset._RelativePath
        posting_date = datetime.now().strftime("%Y-%m-%d")
        decryption_key = asset.decryption_key
        dec_key_file = asset.decryption_key_file
        compatibilities = asset._OSVersionCompatibilities
        command = f"INSERT INTO assets(specifier, version, baseURL, relativePath, posting_date, decryptionKey, decriptionKeyFile, os_compatibilties) VALUES ('{specifier}', '{version}', '{base_url}', '{relative_path}', '{posting_date}', '{decryption_key}', '{dec_key_file}', '{compatibilities}')"
        #TODO: Write SQL command to append an Asset to the table
    
    def configure_sqlite(self, file_name:str=""):
        if len(file_name) == 0 and not self.file_name:
            raise RuntimeError("Cannot configure file. No file_name passed to Saving.configure_sqlite(str)")
        elif len(file_name) == 0:
            file_name = self.file_name

        sql_commands = [
            "CREATE TABLE assets(id int primary key autoincrement, specifier text, version text, baseURL text, relativePath text, posting_date datetime, decryptionKey text, decryptionKeyFile text, os_compatibilities int)",
            "CREATE TABLE os_compatibilities(id integer primary key autoincrement, deviceName text, minOSVersion text, maxOSVersion text)"
        ]
        cnx = sqlite.connect(file_name)
        cur = cnx.cursor()
        for cmd in sql_commands:
            cur.execute(cmd)
        cnx.commit()

    def sqlite_exists(self, file_name:str="") -> bool:
        if len(file_name) == 0 and not self.file_name:
            raise RuntimeError("Cannot configure file. No file_name passed to Saving.sqlite_exists(str)")
        elif len(file_name) == 0:
            file_name = self.file_name
        return file_name in os.listdir('')