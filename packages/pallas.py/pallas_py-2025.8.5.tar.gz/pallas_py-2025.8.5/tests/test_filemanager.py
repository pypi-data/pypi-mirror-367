import pytest

import os

import zipfile

from pallas.utils.FileManager import FileManager

def test_unit_filemanager_create_zip_success():
    fm = FileManager()
    fm.create_new_zip(zip_filename="/tmp/filemanager_test.zip")
    assert 'filemanager_test.zip' in os.listdir('/tmp/')

def test_unit_filemanager_create_zip_fail():
    fm = FileManager()
    zip_filename = "/tmp/filemanager_^test.zip" #Fails because we can't use ^ in the filename
    try:
        fm.create_new_zip(zip_filename=zip_filename) #this should fail.. we'll see
    except Exception as ex:
        pass
    assert '/tmp/filemanager_test.zip' not in os.listdir('/tmp/')

def test_unit_filemanager_write_str_to_zipfile_success():
    dir = "/tmp"
    zip_filename = "zipfile.zip"
    zip_path = f"{dir}/{zip_filename}"
    dst_filename = "Test.txt"
    data = "abc123--RitoPlz"

    #Attempt to store data in zip
    try:
        fm = FileManager()
        fm.create_new_zip(zip_filename=zip_path)
        fm.write_str_to_zipfile(zip_filename=zip_path, dest_filename=dst_filename, data=data)
    except:
        assert False

    #Read data from ZIP
    assert zip_filename in os.listdir(dir)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        with zf.open(dst_filename, mode='r') as f:
            f_data = f.read()
    if type(f_data) == bytes:
        f_data = str(f_data)[2:-1]
    assert f_data == data

#TODO: Write Failing test for FileManager.str_to_zipfile
def test_unit_filemanager_write_str_to_zipfile_fail():
    pass

#TODO: Write success function for FileManager.write_str_to_yaml()
def test_unit_filemanager_write_str_to_yaml_success():
    pass

#TODO: Write Failing test for FileManager.write_str_to_yaml() (what can't you write to YAML?)
def test_unit_filemanager_write_str_to_yaml_fail():
    pass
