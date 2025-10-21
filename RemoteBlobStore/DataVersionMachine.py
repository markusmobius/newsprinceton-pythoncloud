from RemoteBlobStore.Remote.Runners.CloudMachine import CloudMachine
from RemoteBlobStore.Remote.Runners.DownloadTask import DownloadTask, DirectorySet, FilterPattern
from RemoteBlobStore.Remote.RemoteBlobServer import RemoteBlobServer
from RemoteBlobStore.Remote.Runners.UploadTask import TagRule, BlobFilter
import json
import hashlib
import os
from pathlib import Path
import uuid
import shutil
import atexit

class DataVersionMachine:
    def __init__(self, clientHash: str, serverUrl: str, cacheFolder: str):
        self.server = RemoteBlobServer()
        self.cloud = CloudMachine(port=self.server.port,clientHash=clientHash,serverUrl=serverUrl)
        self.cacheFolder=cacheFolder
        self.tempFolder=os.path.join(cacheFolder,"__temp")
        # Create the directory and any necessary parent directories if they don't exist
        temp_path = Path(self.tempFolder)
        temp_path.mkdir(parents=True, exist_ok=True)
        # Register cleanup handler at process exit
        atexit.register(self._cleanup)

    def _cleanup(self):
        """Runs automatically on interpreter exit to clean up resources."""
        try:
            # Gracefully close the server
            self.server.closeClient()
        except Exception as e:
            print(f"Warning: error closing RemoteBlobServer: {e}")

            
    def getTempFile(self, config: any):
        hash = self.getHash(config)
        return os.path.join(self.tempFolder,hash)
    
    def getEphemeralFile(self):
        guid=str(uuid.uuid4())
        return os.path.join(self.tempFolder,guid)

    def getConfigJson(self,config : any):
        json_str = json.dumps(config, default=lambda x: x.__dict__, sort_keys=True)
        return json_str

    def getHash(self, config :any):
        json_str=self.getConfigJson(config)
        hash_object = hashlib.sha256(json_str.encode('utf-8'))
        return hash_object.hexdigest()

    #cloudPath is a path to the directory where the versions will be stored
    def loadVersion(self, cloudPath: str, config: any, debug:bool = False):
        hash = self.getHash(config)
        localPath=os.path.join(self.cacheFolder,cloudPath,hash)
        if os.path.exists(localPath):
            return localPath
        if debug:
            return None
        dirStatus = self.cloud.Directory(cloudDirectory=cloudPath)
        if hash in dirStatus.files:
            task=DownloadTask(localRootDirectory=self.cacheFolder,downloads=DirectorySet(paths=[cloudPath+"/{{PATTERN}}|"],filters={"PATTERN": FilterPattern(patterns=["*"+hash+"*"])}))
            self.cloud.Download(downloads=task)
            return localPath
        else:
            return None

    def saveVersion(self, tempFileName, cloudPath: str, config: any, debug:bool = False):
        hash = self.getHash(config)        
        if hash!=os.path.basename(tempFileName):
            raise Exception("temp filename does not match config")
        localPath=os.path.join(self.cacheFolder,cloudPath,hash)
        parent_path = Path(os.path.join(self.cacheFolder,cloudPath))
        parent_path.mkdir(parents=True, exist_ok=True)        
        shutil.move(tempFileName,localPath)
        if debug:
            return
        #create a temporary subfolder for the temp file
        guid=str(uuid.uuid4())
        tempSubdir=Path(os.path.join(self.tempFolder,guid))
        tempSubdir.mkdir(parents=True, exist_ok=True)
        shutil.copy(localPath,os.path.join(self.tempFolder,guid,hash))
        tagRules=[]
        tagRules.append(TagRule(key="config",value=self.getConfigJson(config),kvFilter=BlobFilter(ftype="pattern",filterDefinition="*")))
        self.cloud.Upload(localDirectory=os.path.join(self.tempFolder,guid),cloudDirectory=cloudPath,tagRules=tagRules,publicRules=[],recursiveUpload=False)
        #delete the temporary subfolder
        shutil.rmtree(os.path.join(self.tempFolder,guid))
    
    def Dispose(self):
        self.server.closeClient()

