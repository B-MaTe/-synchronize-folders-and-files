"""
    A module to synchronize folders and their subfolders/files aswell.
    This module uses the os module and the multiprocessing module.
"""

# Mandatory parameters to use this module:
# source_path (string) : path of the source folder
# MAX_CHANGES (consant integer) : maximum number of changes (add/remove/modify) 

import os
import multiprocessing as mp


class SyncFolders:
    
    def __init__(self, source_path, MAX_CHANGES):
        self.source_path = source_path
        self.MAX_CHANGES = MAX_CHANGES
        self.changes_made = 0
        
        
        #### ---------- ####
        self.buffer = list()
        # buffer that keeps track of changes, temporary stores the changes
        # two dimensional list
        # the second dimension will contain the type of change (add/remove/modify)
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
        
        # start the main loop
        #self.main()
        
        
    def getSource_path(self):
        return self.source_path
    

    def getMAX_CHANGES(self):
        return self.MAX_CHANGES
    
    
    def getChanges_made(self):
        return self.changes_made
    
    
    def increase_changes_made(self):
        self.changes_made += 1
        
    
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
                tempFolderInfo[item] = source_path + "\\"
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
            if self.getChanges_made >= self.MAX_CHANGES:
                quit(f"The program finished with {self.changes_made} changes.")
                
            # continue if nothing is in the buffer
            if not self.buffer:
                continue
            # call the recursive method
            self.make_changes(self, self.buffer.pop())
            
            # increase changes_made
            self.increase_changes_made()
                
    
    def make_changes(self, change):
        # change : list in the buffer
        # gets called by sync_folders method
        # recursive method, which calles itself in every folder
        pass
            
    
    def check_for_changes(self):
        # Producer process that keeps checking for changes and adds them to the buffer
        while True:
            # check for change
            pass
        
    
    def main(self):
        # init the two processes
        producer = mp.Process(target=self.check_for_changes)
        consumer = mp.Process(target=self.sync_folders)
        
        # start them and join them
        producer.start()
        producer.join()
        
        consumer.start()
        consumer.join()
        
        
    
    
    
        


