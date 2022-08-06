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
        self.buffer = mp.Queue(maxsize=self.MAX_CHANGES)
        # buffer that keeps track of changes, temporary stores the changes
        # the queue contains lists
        # the lists will contain the type of change (add/remove/modify),
                                # 1 = add
                                # 0 = remove
                                # -1 = modify
        # name of folder / file,
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
                tempFolderInfo[source_path + item] = item
                self.setFolder_information(tempFolderInfo)
                
                # call recursive function with new path
                self.init_folder_file_information(source_path + item + "\\")
            else:
                # handle self.file_information
                tempFileInfo = self.getFile_information()
                tempFileInfo[source_path + item] = item
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
        print(change)
        # todo: logic
        pass
    
            
    
    def check_for_changes(self):
        # Producer process that keeps checking for changes and adds them to the buffer
        
        # inner method for file and folder checking
        def check():
            # look for changes
            
            # look for modifcation and deletion
            for path, itemName in self.getFolder_information().items():
                parentFolder = "\\".join(path.split("\\")[:-1])
                if os.path.exists(parentFolder):
                    # check if folder exists
                    if os.path.exists(path):
                        # check for files
                        
                        # check if file was modified or removed
                        # loop through files by file_information
                        
                        for file_path, file_name in self.getFile_information().items():
                            # if file doesn't exists, then it was removed or modified
                            if not os.path.exists(file_path):
                                # get the number of files in directory by file_information and os.listdir
                                # if the two numbers equal, file has been modified, otherwise removed
                                file_information_files = []
                                for inner_file_path, inner_file_name in self.getFile_information().items():
                                    if "\\".join(file_path.split("\\")[:-2]) == "\\".join(inner_file_path.split("\\")[:-2]):
                                        file_information_files.append(inner_file_name)
                                os_files = []
                                for inner_os_file in os.listdir("\\".join(file_path.split("\\")[:-1])):
                                    # check if file
                                    if not os.path.isdir("\\".join(file_path.split("\\")[:-1]) + "\\" + inner_os_file):
                                        os_files.append(inner_os_file)
                                
                                # modification
                                if len(os_files) == len(file_information_files):
                                    # get unique files from the two list
                                    unique_files = list(set(file_information_files).symmetric_difference(set(os_files)))
                                    # remove the new file
                                    unique_files.remove(file_name)
                                    
                                    if len(unique_files) != 1:
                                        quit("More than one files changed at a time!")
                                    self.appendToBuffer([-1, file_name, unique_files[0], 0])
                                    return
                                # deletion
                                elif len(os_files) + 1 == len(file_information_files):
                                    self.appendToBuffer([0, file_name, 0])
                                    return
                                else:
                                    quit("More than one files changed at a time!")
                                
                    # check for folders
                    else:
                        # folder removed or modified
                        
                        # get the number of items in directory by folder_information and os.listdir
                        # if the number of items are the same, then the directory been modified, otherwise added or error
                        same_path_counter = 0
        
                        for inner_path in list(self.getFolder_information().keys()) + list(self.getFile_information().keys()):
                            if parentFolder == "\\".join(inner_path.split("\\")[:-1]):
                                same_path_counter += 1
                            
                        if len(os.listdir(parentFolder)) == same_path_counter:
                            # modified
                            oldFolders = []
                            for folder_path, oldfolder_name in self.getFolder_information().items():
                                if parentFolder == "\\".join(folder_path.split("\\")[:-1]):
                                    oldFolders.append(oldfolder_name)
                            newFolders = []
                            for newfolder_name in os.listdir(parentFolder):
                                if os.path.isdir(parentFolder + "\\" + newfolder_name):
                                    newFolders.append(newfolder_name)
                            # get unique items from the two lists
                            unique_folders = list(set(oldFolders).symmetric_difference(set(newFolders)))
                            
                            # remove the renamed folder, the only folder remaining is the old one
                            unique_folders.remove(itemName)
                            if len(unique_folders) != 1:
                                quit("More than one folders changed at a time!")
                            else:
                                # todo: get the old name of modified folder
                                self.appendToBuffer([-1, itemName, unique_folders[0], 1])
                                return
                        elif len(os.listdir(parentFolder)) == same_path_counter - 1:
                            # deleted
                            self.appendToBuffer([0, itemName, 1])
                            return
                        else:
                            # error, multiple operation at the same time
                            quit("More than one folders changed at a time!")
                
            
            # inner recursive method to check if every file in source_path has a pair
            # if not, then that file / folder was added
            def check_for_addition(source_path):
                # recursive method
                for item in os.listdir(source_path):
                    if os.path.isdir(source_path + item):
                        # folder
                        # check if folder exists in getFolder_information
                        if source_path + item not in self.getFolder_information().keys():
                            self.appendToBuffer([1, item, 1])
                            return
                        # call method for folder
                        check_for_addition(source_path + item + "\\")
                    else:
                        # file
                        # check if file exists in getFile_information
                        if source_path + item not in self.getFile_information().keys():
                            self.appendToBuffer([1, item, 0])
                            return
                        
            # look for addition
            check_for_addition(self.getSource_path())
                
            
            
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
    
        


