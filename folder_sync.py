import os
import time
import shutil
import argparse
import logging

# Command to run the script:
# 'python.exe .\folder_sync.py .\original\ .\replica\ 30 .\logs\log_file.log'
# Arguments:
# 1st - Path to the source/original folder
# 2nd - Path to the replica folder that will mirror the source folder
# 3rd - Time interval (in seconds) between each synchronization
# 4th - Path to the log file where operations are recorded

# A separate file is available with code to test this script.

def loggingConfig(log_file):
    log_format = "%(asctime)s - %(message)s"
    
    logging.basicConfig(level=logging.INFO, format=log_format)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(file_handler)


def sync_folders(source, replica, log_file):
    #Code to create or update files on replica by comparing to original
    if not os.path.exists(source):
        logging.error("Source folder doesn't exist")
        return

    if not os.path.exists(replica):
        os.mkdir(replica)
        logging.info(f"Replica folder created: {replica}")

    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        replica_path = os.path.join(replica, item)

        if os.path.isdir(source_path):
            if not os.path.exists (replica_path):
                shutil.copytree(source_path, replica_path)
                logging.info(f"Backup directory created: {replica_path}")
            else:
                sync_folders(source_path,replica_path,log_file) #Recursive call in case of subdirectories

        elif os.path.isfile(source_path):
            if not os.path.exists (replica_path) or (os.path.getmtime(source_path) > os.path.getmtime(replica_path)):
                shutil.copy2(source_path, replica_path)
                logging.info(f"File copied/updated: {source_path} -> {replica_path}")

    #Code to remove extra files from the replica folder by comparing to original
    for item in os.listdir(replica):
        replica_path = os.path.join(replica, item)
        source_path = os.path.join(source, item)

        if not os.path.exists(source_path):
            if os.path.isdir(replica_path):
                shutil.rmtree(replica_path)
                logging.info(f"Backup directory removed: {replica_path}")
            else:
                os.remove(replica_path)
                logging.info(f"File.removed: {replica_path}")

def main ():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Folder Synchronization Tool")
    parser.add_argument("source", help="Source folder path")
    parser.add_argument("replica", help="Replica folder path")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Log file path")

    args = parser.parse_args()

    loggingConfig(args.log_file)
    while True:
        sync_folders(args.source, args.replica, args.log_file)
        time.sleep (args.interval)


if __name__ == "__main__":
    main()