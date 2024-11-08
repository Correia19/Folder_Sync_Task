import os
import shutil
import pytest
import logging
import time
from folder_sync import sync_folders, loggingConfig

def loggingConfig(log_file):
    log_format = "%(asctime)s - %(message)s"
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(level=logging.INFO, format=log_format)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(file_handler)
    
    # Returns file_handler so we are able to terminate it at the end
    return file_handler

@pytest.fixture
def setup_folders():
    source = "test_source"
    replica = "test_replica"
    log_file = "test_log.log"
    
    #For creating the test source and test replica folders
    #Note: Not creating replica folder because it will be tested
    os.makedirs(source, exist_ok=True)
    
    #Logging config
    file_handler = loggingConfig(log_file)
    
    #Passing the variables to the tests
    yield source, replica, log_file
    
    #Close handler
    logging.getLogger().removeHandler(file_handler)
    file_handler.close()
    
    #Cleanup after each test, delets the folders and the test log file
    shutil.rmtree(source)
    shutil.rmtree(replica)
    if os.path.exists(log_file):
        os.remove(log_file)
    
#Test for:
#           Creating and syncing the folders, 
#           Updating and syncing the folders,
#           Deleting and syncing the folders
def test_sync_process(setup_folders):
    source, replica, log_file = setup_folders
    source_file_path = os.path.join(source, "test_file.txt")
    replica_file_path = os.path.join(replica, "test_file.txt")
    
    #Creates a txt file and writes on it
    with open(source_file_path, "w") as f:
        f.write("Testing creation and sync")
    
    #Starts 1st sync process    
    sync_folders(source, replica, log_file)

    #Confirms the content in the log file
    with open(log_file, "r") as f:
        logs = f.read()
        
    time.sleep(10)
    #Confirms the replica folder was created
    assert "Replica folder created" in logs
    
    #Confirms the file was created in the replicated folder
    assert(os.path.exists(replica_file_path))
    
    #Update the text file
    with open(source_file_path, "w") as f:
        f.write("Updated Content")
    
    #Starts 2nd sync process    
    sync_folders(source, replica, log_file)
    
    #Verifiying the updated content on the replica folder
    with open (replica_file_path, "r") as fr:
        text = fr.read()
        
    #Confirms the content was updated in the replicated folder
    assert text == "Updated Content"
    
    #Removes the text file
    os.remove(source_file_path)
    
    #Starts 3rd sync process    
    sync_folders(source, replica, log_file)
    
    #Confirms the file was deleted in the replicated folder
    assert not os.path.exists(replica_file_path)
        
