"""
    A module to synchronize folders and their subfolders/files aswell.
    This module uses the os module and the multiprocessing module.
"""

# Mandatory parameters to use this module:
# source_path (string) : path of the source folder
# MAX_CHANGES (consant integer) : maximum number of changes (add/remove/modify) 

import os
import multiprocessing as mp
import time


class SyncFolders:
    
    def __init__(self, source_path, MAX_CHANGES):
        self.source_path = source_path
        self.MAX_CHANGES = MAX_CHANGES
        self.changes_made = 0
        
        
        #### ---------- ####
        self.buffer = mp.Queue(maxsize=self.MAX_CHANGES)
        # buffer that keeps track of changes, temporary stores the changes
        # the queue contains lists
        # the lists will contain the type of change (add/remove/modify)
                                # 1 = add
                                # 0 = remove
                                # -1 = modify,
        # name of folder / file,
        # whether it's a folder of it's a file
                                # 1 = folder
                                # 0 = file 
        #### ---------- ####                                     
        
        
        
        #### ---------- ####
        # keep track of folders / files
        
        # files
        # dictionary with:
        #       key -> filename (string)
        #       value -> path (string)
        self.file_information = {}
        
        # folders
        # dictionary with:
        #       key -> filename (string)
        #       value -> path (string)
        self.folder_information = {}
        #### ---------- ####
        
    
        #### ---------- ####
        
        # initalize folder and file information based on source path
        self.init_folder_file_information(self.source_path)
        
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
    
    
    def increase_changes_made(self):
        self.changes_made += 1
        
        
    def getBuffer(self):
        return self.buffer
    
    
    def appendToBuffer(self, l):
        if type(l) == list:
            self.buffer.put(l)
        else:
            quit("Error adding to Buffer!")
    
    
    def getFile_information(self):
        return self.file_information
    
    
    def setFile_information(self, file_information):
        self.file_information = file_information
    
    
    def getFolder_information(self):
        return self.folder_information
    
    
    def setFolder_information(self, folder_information):
        self.folder_information = folder_information
        
    
    def init_folder_file_information(self, source_path):
        # recursive method, maps the folders and files
        
        # iterate through the current directory provided by source_path
        for item in os.listdir(source_path):
            
            # if folder, add to self.folder_information and call the method with the folder's path
            if os.path.isdir(source_path + item):
                tempFolderInfo = self.getFolder_information()
                tempFolderInfo[item] = source_path
                self.setFolder_information(tempFolderInfo)
                
                # call recursive function with new path
                self.init_folder_file_information(source_path + item + "\\")
            else:
                # handle self.file_information
                tempFileInfo = self.getFile_information()
                tempFileInfo[item] = source_path
                self.setFile_information(tempFileInfo)
                
    
    
    def sync_folders(self):
        # Consumer process that reads the changes from the buffer
        while True:
            # quit if changes_made equals MAX_CHANGES
            if self.getChanges_made() >= self.MAX_CHANGES:
                quit(f"The program finished with {self.changes_made} changes.")
                
            # continue if nothing is in the buffer
            if not self.getBuffer().empty():
                continue
            
            
            # get and remove the last item from buffer
            change = self.getBuffer().get()
            
            # call the recursive method
            self.make_changes(change)
            
            # increase changes_made
            self.increase_changes_made()
                
    
    def make_changes(self, change):
        # change : list in the buffer
        # gets called by sync_folders method
        
        # todo: logic
        pass
    
            
    
    def check_for_changes(self):
        # Producer process that keeps checking for changes and adds them to the buffer
        
        # inner method for file and folder checking
        def check():
            # look for changes
            for itemName, path in self.getFolder_information().items():
               
                # check if folder exists
                if os.path.exists(path + itemName):
                    for item in os.listdir(path):
                        if not os.path.isdir(path + item):
                            # todo: check file
                            pass
                else:
                    # containing folder deleted or modified
                    
                    # get the number of items in parent directory by folder_information and os.listdir
                    # if the number of items are the same, then the directory been modified, otherwise added or error
                    same_path_counter = 0
                    parentFolder = "\\".join(path.split("\\")[:-2]) + "\\"
    
                    for path in list(self.getFolder_information().values()) + list(self.getFile_information().values()):
                        if path == parentFolder:
                            same_path_counter += 1
                    if len(os.listdir(parentFolder)) == same_path_counter:
                        # modified
                        # todo: get the old name of modified folder
                        self.appendToBuffer([-1, itemName, 1])
                        return
                    elif len(os.listdir(parentFolder)) == same_path_counter - 1:
                        # deleted
                        self.appendToBuffer(0, itemName, 1)
                        return
                    else:
                        # error, multiple operation at the same time
                        quit("Multiple operation at the same time!")
            # todo: check folder addition
            
        while True:
            # check for change if make_changes method is not executing
            if self.buffer.empty():
                # call the check method
                check()
            
       
    def main(self):
        # init the two processes
        producer = mp.Process(target=self.check_for_changes)
        consumer = mp.Process(target=self.sync_folders)
        
        # start them and join them
        producer.start()
        consumer.start()
        
        
        #consumer.join()
    
        #producer.join()
       
        
    
        


