from sync_folders_greehill import SyncFolders
import os

testClass = SyncFolders(os.getcwd() + "\\sync_folders\\test\\test1\\test1source\\", 20)
print(testClass.getFile_information())
print("\n\n")
print(testClass.getFolder_information())


