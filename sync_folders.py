"""
    A module to synchronize folders and their subfolders/files aswell.
    This module uses the os, pathlib, shutil, time, sys, platform, disutils, warnings and the multiprocessing module.
"""

# Mandatory parameters to use this module:
# source_path (string) : path of the source folder
# MAX_CHANGES (consant integer) : maximum number of changes (add/remove/modify) 


import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import multiprocessing as mp
from pathlib import Path
import shutil
import time
from sys import argv
from platform import system
from distutils.dir_util import copy_tree


class SyncFolders:
    
    def __init__(self, source_path, MAX_CHANGES, seperator):
        
        #### ---------- ####
        self.source_path = source_path
        self.MAX_CHANGES = MAX_CHANGES
        self.changes_made = 0
        self.seperator = seperator
        self.modification_counter = 1
        self.overall_modifications = mp.Value('i', 0)
        #### ---------- ####
        
        
        
        #### ---------- ####
        self.buffer = mp.Queue()
        # buffer that keeps track of changes, temporary stores the changes
        # the queue contains lists
        # the lists will contain the type of change (add/remove/modify),
                                # 1 = add
                                # 0 = remove
                                # -1 = rename
                                # -2 = modify
        # name of folder / file,
        # if add and folder, then the path of the folder (to copy its content)
        # if modify, then the name of the old file,
        # whether it's a folder of it's a file
                                # 1 = folder
                                # 0 = file 
        #### ---------- ####                                     
        
        
        
        #### ---------- ####
        # keep track of folders / files
        
        # files
        # dictionary with:
        #       key -> path of file (string)
        #       value -> name of file (string)
        self.file_information = {}
        
        # folders
        # dictionary with:
        #       key -> path of folder (string)
        #       value -> name of folder (string)
        self.folder_information = {}
        
        # dictionary for files and their last modified value
        #       key -> path of file (string)
        #       value -> last time of modification (int)
        self.last_modified_files = {}
        #### ---------- ####
        
        
        #### ---------- ####
        # boolean for the two processes
        self.finished_changing = mp.Event()
        
        # set it to True
        self.finished_changing.set()
        
        # flag for exiting the process
        self.exit_process = mp.Event()
        #### ---------- ####
    
    
        #### ---------- ####
        # initalize folder and file information based on source path
        self.init_folder_file_information(self.source_path)
        #### ---------- ####
        
        
        #### ---------- ####
        # get the number of items in source_dir
        self.number_of_items = sum(1 for _ in Path(self.source_path).glob('**/*'))
        #### ---------- ####
        
        
        #### ---------- ####
        # start the main loop
        self.main()
        #### ---------- ####
        
    
    def getSource_path(self):
        return self.source_path
    

    def getMAX_CHANGES(self):
        return self.MAX_CHANGES
    
    
    def getChanges_made(self):
        return self.changes_made
    
    
    def getSeperator(self):
        return self.seperator
    
    
    def getModification_counter(self):
        return self.modification_counter
    
    
    def setModification_counter(self, number):
        self.modification_counter = number
        
        
    def getOverall_modifications(self):
        return self.overall_modifications.value
    
    
    def setOverall_modifications(self, number):
        self.overall_modifications.value = number
        
        
    def increase_changes_made(self):
        self.changes_made += 1
        
        
    def getBuffer(self):
        return self.buffer
    
    
    def appendToBuffer(self, l):
        if type(l) == list:
            self.buffer.put(l)
        else:
            self._exit_process()
    
    
    def getFile_information(self):
        return self.file_information
    
    
    def setFile_information(self, file_information):
        self.file_information = file_information
    
    
    def getFolder_information(self):
        return self.folder_information
    
    
    def setFolder_information(self, folder_information):
        self.folder_information = folder_information
        
        
    def clearFolderFileInformation(self):
        self.folder_information.clear()
        self.file_information.clear()
        self.last_modified_files.clear()
        
        
    def getLast_modified_files(self):
        return self.last_modified_files
    
    
    def addLast_modified_files(self, key, val):
        self.last_modified_files[key] = val
        
        
    def getAndRemoveFromBuffer(self):
        return self.buffer.get()
    
    
    def getFinished_changing(self):
        return self.finished_changing.is_set()
    
    
    def setFinished_changing(self, boolean):
        if boolean == True:
            self.finished_changing.set()
        else:
            self.finished_changing.clear()
        
    
    def getExit_process(self):
        return self.exit_process.is_set()
    
    
    def _exit_process(self):
        self.exit_process.set()
        
            
    def getNumber_of_items(self):
        return self.number_of_items
    
    
    def updateAndGetNumber_of_items(self):
        self.number_of_items = sum(1 for _ in Path(self.getSource_path()).glob('**/*'))
        return self.number_of_items
            
            
    # init the recursive methods for adding / modifying / deleting files / folders
    # file addition
    def add_file(self, source, file_path, filename):
        # recursively go through every folder and check if filename exists,
        # if not, copy the recently added file to the folder
        for item in os.listdir(source):
            path = os.path.join(source, item)
            if os.path.isdir(path):
                self.add_file(path + self.getSeperator(), file_path, filename)
        if not os.path.exists(os.path.join(source, filename)):
            try:
                shutil.copy2(file_path, source)
            except PermissionError:
                while True:
                    try:
                        # for some reason, copy2 sometimes throws PermissionError...
                        # In my opinion the problem is that the program tries to copy the file as soon as it is created, and maybe
                        # it copyes the file before its initalization...
                        # I managed to fix it with this loop
                        shutil.copy2(file_path, source)
                        break
                    except PermissionError:
                        pass
            
            
    def rename_file(self, source, new_file, old_file):
        # recursively go through every folder and check if old_file exists,
        # if yes, then rename it to new_file name
        for item in os.listdir(source):
            # get path
            path = os.path.join(source, item)
            if os.path.isdir(path):
                self.rename_file(path + self.getSeperator(), new_file, old_file)
        oldPath = os.path.join(source, old_file)
        if os.path.exists(oldPath):
            os.rename(oldPath, os.path.join(source, new_file))
            
            # increase the modification counter
            self.setModification_counter(self.getModification_counter() + 1)
            
            
    # file modification
    def modify_file(self, source, file_name, file_path):
        # recursively go through every folder and check if file_name exists,
        # if yes, then replace it with file_path file
        for item in os.listdir(source):
            # get path
            path = os.path.join(source, item)
            if os.path.isdir(source + item):
                self.modify_file(path + self.getSeperator(), file_name, file_path)
        oldPath = os.path.join(source, file_name)
        if os.path.exists(oldPath) and os.path.normcase(oldPath) != os.path.normcase(file_path):
            # remove the file and copy the modified file from file_path
            os.remove(oldPath)
            shutil.copy(file_path, source)
            
            # increase the modification counter
            self.setModification_counter(self.getModification_counter() + 1)
            
            
    # file deletion
    def delete_file(self, source, filename):
        # recursively go through every folder and check if filename exists,
        # if yes, remove it
        for item in os.listdir(source):
            path = os.path.join(source, item)
            if os.path.isdir(path):
                self.delete_file(path + self.getSeperator(), filename)
        path = os.path.join(source, filename)
        if os.path.exists(path):
            os.remove(path)
        
        
    # folder addition
    def add_folder(self, source, foldername, folder_path):
        # recursively go through every folder and check if foldername exists,
        # if not, create it
        for item in os.listdir(source):
            if os.path.normcase(source) == os.path.normcase(folder_path + self.getSeperator()):
                # causes infinite recursion
                return
            if os.path.isdir(source + item):
                self.add_folder(source + item + self.getSeperator(), foldername, folder_path)
        path = os.path.join(source, foldername)
        if not os.path.exists(path):
            # check if folder has content
            if len(os.listdir(folder_path)) > 0:
                # copy the contents of the added directory
                copy_tree(folder_path, path)
            else:
                # create directory
                if os.path.normcase(path) != os.path.normcase(os.path.join(folder_path, foldername)):
                    os.mkdir(path)
            
    # folder modification
    def modify_folder(self, source, new_folder, old_folder):
        # recursively go through every folder and check if old_folder exists,
        # if yes, rename it to new_folder name
        for item in os.listdir(source):
            if os.path.isdir(source + item):
                self.modify_folder(source + item + self.getSeperator(), new_folder, old_folder)
        if os.path.exists(os.path.join(source, old_folder)):
            os.rename(os.path.join(source, old_folder) + self.getSeperator(), os.path.join(source, new_folder) + self.getSeperator())
            
            # increase the modification counter
            self.setModification_counter(self.getModification_counter() + 1)
            
            
    # folder deletion
    def delete_folder(self, source, foldername):
        # recursively go through every folder and check if foldername exists,
        # if yes, remove it
        # if the folder is not empty, use shutil to remove the tree
        for item in os.listdir(source):
            if os.path.isdir(source + item):
                self.delete_folder(source + item + self.getSeperator(), foldername)
        path = os.path.join(source, foldername)
        if os.path.exists(path):
            # check if folder empty
            if len(os.listdir(path)) > 0:
                # use shutil to remove the directory and its belongings
                shutil.rmtree(path)
            else:
                os.rmdir(path)
                
            
    def init_folder_file_information(self, source_path):
        # recursive method, maps the folders and files
        
        # iterate through the current directory provided by source_path
        for item in os.listdir(source_path):
            # get the path
            path = os.path.join(source_path, item)
            # if folder, add to self.folder_information and call the method with the folder's path
            if os.path.isdir(path):
                tempFolderInfo = self.getFolder_information()
                tempFolderInfo[path] = item
                self.setFolder_information(tempFolderInfo)
                
                # call recursive function with new path
                self.init_folder_file_information(path + self.getSeperator())
            else:
                # handle last_modified_files
                self.addLast_modified_files(path, os.path.getmtime(path))
                
                # handle self.file_information
                tempFileInfo = self.getFile_information()
                tempFileInfo[path] = item
                self.setFile_information(tempFileInfo)
                
    
    def sync_folders(self):
        # Consumer process that reads the changes from the buffer
        while True:
            # quit if changes_made equals MAX_CHANGES
            if self.getChanges_made() >= self.MAX_CHANGES:
                self._exit_process()
                
            # continue if nothing is in the buffer
            if self.getBuffer().empty():
                continue
            
            # call the make_change method
            self.make_changes()
            
            # increase changes_made
            self.increase_changes_made()
                
    
    def make_changes(self):
        # change : list in the buffer
        # gets called by sync_folders method
        
        # get and remove the last item from the queue
        change = self.getAndRemoveFromBuffer()
        
        
        # reset modification_counter
        self.setModification_counter(1)
        # check the last item and call the corresponding recursive method
        
        if change[-1] == 1:
            # folders
            if change[0] == 1:
                # addition
                self.add_folder(self.getSource_path(), change[1], change[2])
                
                # get the old number of items and the updated one, update the modification_number by their absoulte subtraction
                self.setModification_counter(abs(self.getNumber_of_items() - self.updateAndGetNumber_of_items()))
                print(f"{self.getModification_counter()} item(s) added.")
                
            elif change[0] == 0:
                # deletion
                self.delete_folder(self.getSource_path(), change[1])
                
                # get the old number of items and the updated one, update the modification_number by their subtraction
                self.setModification_counter(self.getNumber_of_items() - self.updateAndGetNumber_of_items())
                print(f"{self.getModification_counter()} item(s) removed.")
                
            else:
                # rename
                self.modify_folder(self.getSource_path(), change[1], change[2])
                print(f"{self.getModification_counter()} folder(s) renamed.")
                
        else:
            # files
            if change[0] == 1:
                # addition
                self.add_file(self.getSource_path(), change[1], change[2])
                
                # get the old number of items and the updated one, update the modification_number by their absolute subtraction
                self.setModification_counter(abs(self.getNumber_of_items() - self.updateAndGetNumber_of_items())) 
                print(f"{self.getModification_counter()} file(s) added.")
                
            elif change[0] == 0:
                # deletion
                self.delete_file(self.getSource_path(), change[1])
                # get the old number of items and the updated one, update the modification_number by their subtraction
                self.setModification_counter(self.getNumber_of_items() - self.updateAndGetNumber_of_items()) 
                print(f"{self.getModification_counter()} file(s) removed.")
            elif change[0] == -1:
                # rename
                self.rename_file(self.getSource_path(), change[1], change[2])
                print(f"{self.getModification_counter()} file(s) renamed.")
            else:
                # modification
                self.modify_file(self.getSource_path(), change[1], change[2])
                print(f"{self.getModification_counter()} file(s) modified.")
        
        # increase overall_modifications
        self.setOverall_modifications(self.getOverall_modifications() + self.getModification_counter())
        
        # finished the change
        self.setFinished_changing(True)
        
    
    def check_for_changes(self):
        # Producer process that keeps checking for changes and adds them to the buffer
        
        
        # inner method for file and folder checking
        def check(source_path):
            
            # look for changes
            
            # try-except block is necessary, because changes can happen while the method runs,
            # and the program would throw FileNotFoundError
            try:
                # loop through the folders by os.listdir and compare the items with the ones in folder_information, file_information
                os_files = []
                os_folders = []
                if os.path.exists(source_path):
                    for os_item in os.listdir(source_path):
                        if os.path.isdir(os.path.join(source_path, os_item)):
                            # folder
                            os_folders.append(os_item)
                        else:
                            # file
                            os_files.append(os_item)
                            
                    # files
                    # loop through file_information
                    # get the files with the path source_path
                    information_files = []
                    for information_file_path, information_file in self.getFile_information().items():
                        information_file_path = Path(information_file_path)
                        if Path(source_path) == information_file_path.parent.absolute():
                            information_files.append(information_file)
                            
                    # folders
                    # loop through folder_information
                    # get the  folders with the path source_path
                    information_folders = []
                    for information_folder_path, information_folder in self.getFolder_information().items():
                        information_folder_path = Path(information_folder_path)
                        if Path(source_path) == information_folder_path.parent.absolute():
                            information_folders.append(information_folder)
                
                
                    # folder checking
                    info_folders_len = len(information_folders)
                    os_folders_len = len(os_folders)
                    # deleted or added folder if the length of the two lists are not the same
                    if info_folders_len != os_folders_len:
                        # get the unique elements from the two list
                        unique = list(set(information_folders).symmetric_difference(set(os_folders)))
                        if len(unique) != 1:
                            self._exit_process()
                        if info_folders_len > os_folders_len:
                            # deleted folder
                            self.appendToBuffer([0, unique[0], 1])
                            return True
                        else:
                            # added folder
                            self.appendToBuffer([1, unique[0], os.path.join(source_path, unique[0]) ,1])
                            return True
                            
                    # modification of folder
                    elif information_folders != os_folders:
                        # get the unique elements from the two list
                        unique = list(set(information_folders).symmetric_difference(set(os_folders)))
                        if len(unique) != 2:
                            self._exit_process()
                        if unique[0] in os_folders:
                            new_folder_name = unique[0]
                            old_folder_name = unique[1]
                        else:
                            new_folder_name = unique[1]
                            old_folder_name = unique[0]
                        self.appendToBuffer([-1, new_folder_name, old_folder_name, 1])
                        return True
                        
                    
                    # file checking
                    
                    info_files_len = len(information_files)
                    os_files_len = len(os_files)
                    # deleted or added file if the length of the two lists are not the same
                    if info_files_len != os_files_len:
                        # get the unique elements from the two list
                        unique = list(set(information_files).symmetric_difference(set(os_files)))
                        if len(unique) != 1:
                            self._exit_process()
                        if info_files_len > os_files_len:
                            # deleted file
                            self.appendToBuffer([0, unique[0], 0])
                            return True
                        else:
                            # added file
                            self.appendToBuffer([1, os.path.join(source_path, unique[0]), unique[0], 0])
                            return True
                            
                    # file renaming
                    elif information_files != os_files:
                        # get the unique elements from the two list
                        unique = list(set(information_files).symmetric_difference(set(os_files)))
                        if len(unique) != 2:
                            self._exit_process()
                        if unique[0] in os_files:
                            new_file_name = unique[0]
                            old_file_name = unique[1]
                        else:
                            new_file_name = unique[1]
                            old_file_name = unique[0]
                        self.appendToBuffer([-1, new_file_name, old_file_name, 0])
                        return True
                    
                    # file modifying
                    # loop through source_path, convert the files last modified value with last_modified_files
                    for filename in os.listdir(source_path):
                        path = os.path.join(source_path, filename)
                        if not os.path.isdir(path):
                            # file
                            if path in self.getLast_modified_files().keys():
                                if os.path.getmtime(path) > self.getLast_modified_files()[path]:
                                    self.appendToBuffer([-2, filename, path, 0])
                                    return True
                        
                    for folder in os_folders:
                        # call the method again with the found folders path
                            if check(os.path.join(source_path, folder)):
                                return True
            except:
                return False
                    
        while True:
            # check for change if make_changes method is not executing
            if self.getBuffer().empty() and self.getFinished_changing():
                # call the check method
                if check(self.getSource_path()):
                    self.setFinished_changing(False)
                    while not self.getFinished_changing():
                        # wait until the other process finished changing
                        time.sleep(1)
                    
                    # clear thefolder_inforamtion and file_information dictionaries
                    self.clearFolderFileInformation()
                    
                    # init the folder_inforamtion and file_information dictionaries again
                    self.init_folder_file_information(self.source_path)
                    
                    
    def main(self):
        # init the two processes
        producer = mp.Process(target=self.check_for_changes)
        consumer = mp.Process(target=self.sync_folders)
        
        # start them
        producer.start()
        consumer.start()
        
        
        while True:
            if self.getExit_process():
                # if exit triggers, stop the processes and exit from the program
                producer.kill()
                consumer.kill()
                quit(f"Program finished with {self.getOverall_modifications()} modifications.")
                
                  
if __name__ == '__main__':
    if len(argv) < 3:
        quit("Not enough arguments!")
    
    OS = system()
    if OS == "Windows":
        seperator = "\\"
    elif OS == "Linux" or OS == "Darwin":
        seperator = "/"
    else:
        quit("Not supported Operating System!")
    
    if argv[1][-1] != seperator:
        argv[1] += seperator
    
    SyncFolders(argv[1], int(argv[2]), seperator)