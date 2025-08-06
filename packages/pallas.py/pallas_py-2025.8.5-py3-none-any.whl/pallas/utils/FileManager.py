import os
import zipfile

class FileManager:
    def create_new_zip(self, zip_filename:str="zipfile.zip"):
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        with zipfile.ZipFile(zip_filename, 'w') as zip_f:
            zip_f.writestr("UAFAssets/start.txt", "\n")

    def write_str_to_zipfile(self, zip_filename:str="zipfile.zip", dest_filename:str="Test.txt", data:str="\n"):
        with zipfile.ZipFile(zip_filename, 'a') as zip_f:
            zip_f.writestr(dest_filename, data)
    
    def write_str_to_yaml(self, filepath:str="payload.yml", data:str="\n"):
        with open(filepath, 'w') as f:
            f.write(data)
