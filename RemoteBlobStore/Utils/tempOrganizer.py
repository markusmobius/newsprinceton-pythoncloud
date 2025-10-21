import os
import shutil
import sys
import time


class tempOrganizer:
    def __init__(self):
        value = os.environ.get("TEMP_NETCORE")
        if value is not None:
            self.baseTempDir = value
        else:
            self.baseTempDir = os.path.join(os.getcwd(), "temp_netcore")

    def getTempDir(self, tempPath):
        tempDir = "temp"
        try:
            fn = os.path.basename(sys.executable).split('.')[0]
            dir = os.path.dirname(os.path.abspath(__file__))
            hs = self.GetStableHashCode(dir)
            if hs < 0:
                hs = -hs
            tempDir = os.path.join(self.baseTempDir, f"{fn}_{tempPath}_{hs}")
        except Exception as e:
            tempDir = os.path.join(tempDir, tempPath)
            print("tempOrganizer error:", e)
        return tempDir

    def createTempDir(self, tempPath, deleteTempDir=True):
        dir = self.getTempDir(tempPath)
        if deleteTempDir:
            self.robustDirectoryDelete(dir)
        if not os.path.exists(dir):
            while True:
                try:
                    os.makedirs(dir)
                    if os.path.exists(dir):
                        break
                except Exception:
                    pass
                time.sleep(0.1)
        return dir
    
    def deleteTempDir(self, tempPath):
        self.robustDirectoryDelete(self.getTempDir(tempPath))
    
    def robustDirectoryDelete(self, dirname):
        if os.path.exists(dirname):
            try:
                shutil.rmtree(dirname,ignore_errors=True)
            except Exception as e:
                print(e)
                return

    def GetStableHashCode(self, string):
        hash1 = 5381
        hash2 = hash1
        for i in range(0, len(string), 2):
            hash1 = ((hash1 << 5) + hash1) ^ ord(string[i])
            if i == len(string) - 1 or string[i + 1] == '\0':
                break
            hash2 = ((hash2 << 5) + hash2) ^ ord(string[i + 1])
        return hash1 + (hash2 * 1566083941)