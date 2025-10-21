# RemoteDataStore

This project provides a simple Python interface for researchers to save and store data in cloud storage. 

## Installation

In general, you ```pip install``` this Python package from this GitHub repository. It is assumed that you are using Windows PowerShell during the installation process. Follow these steps:

1. Create a Python environment:
   ```
   python -m venv myenv
   myenv\Scripts\Activate.ps1
   ```
   You can replace ```myenv``` with the name you want to give to your environment. This command will create a new directory named ```myenv``` in your current directory, containing a clean Python environment. If the command line displays the environment name within parentheses upon activation, e.g. ```(myenv)```, the activation is successful.

2. Install ```RemoteBlobStore``` from this GitHub repository:
   ```
   pip install git+https://github.com/markusmobius/newsprinceton-pythoncloud
   ```
   
## Usage: Version Machine (high-level API)

```TestVersionMachine.py``` is used in this section to demonstrate the version machine that allows saving and loading of data files that are versioned by config JSON files.

```
import os
from RemoteBlobStore.DataVersionMachine import DataVersionMachine

def main():
    machine=DataVersionMachine(clientHash=os.getenv("legocloud_clienthash"),serverUrl="https://www.legocloud.projectratio.net:6002",cacheFolder="c:/temp")
    config={"key1":"this is a test","key2":"this is really a test","key2":"this is really a test - another one!"}
    print(f"Trying to locate data file for config {machine.getConfigJson(config)}")
    localFileName=machine.loadVersion(cloudPath="pds/test",config=config)
    if localFileName==None:
        print("File has not been saved before")
        print("Creating temporary file")
        tempFileName=machine.getTempFile(config)
        print("Writing data to temporary file")
        with open(tempFileName, "w") as f:
            f.write("This is a new file with some dummy content ...")
        print("Saving temporary data to cloud storage")
        machine.saveVersion(tempFileName=tempFileName,cloudPath="pds/test",config=config)
    else:
        print("File exists!")
    
    print("Note: if you specify debug=True for loadVersion and saveVersion method it will not store to the cloud but only to local storage")

if __name__ == '__main__':
    main()
```

We create a ```DataVersionMachine``` class by providing clienthash and server URL for the data store as well as a cache folder for the data. All the data files will be stored in that cache folder.

Given a config file we check whether the data exists already in the cache or the on the server using ```loadVersion```. If it exists we download the data if necessary and return the local path. Otherwise, we create a temporary file name with a unique hash of the config file as the filename. Typically, this will be a new data store that we are constructing. 
We then use ```saveVersion``` to move the data into the permanent cache and upload this data to cloud storage (unless ```debug=True``` is set in which case we don't upload).

There is also a ```getEphemeralFile``` method which creates a temporary file that has a unique id (unconnected to any config file) and that lives during the duration of the current program. 

To summarize, ```DataVersionMachine``` provides the following 4 methods:

```
getTempFile(config)
getEphemeralFile()
loadVersion(cloudPath="pds/test",config=config)
saveVersion(tempFileName=tempFileName,cloudPath="pds/test",config=config)
```


## Usage: CloudMachine (low-level API)

Sometimes, it can be useful to have full control when storing cloud data. ```Test.py``` demonstrates how to use this API.


```
import os
import json

from RemoteBlobStore.Remote.Runners.CloudMachine import CloudMachine
from RemoteBlobStore.Remote.Runners.DownloadTask import DownloadTask, DirectorySet
from RemoteBlobStore.Remote.RemoteBlobServer import RemoteBlobServer
from RemoteBlobStore.Remote.Runners.UploadTask import TagRule, BlobFilter

def main():
    server = RemoteBlobServer()
    cloud = CloudMachine(port=server.port,clientHash=os.getenv("legocloud_clienthash"),serverUrl="https://www.legocloud.projectratio.net:6002")
    print(f"Remote blob server is on port {server.port}")
    #time.sleep(100)

    try:
        task=DownloadTask("C:/temp",DirectorySet(paths=["Resources/"]))
        log=cloud.Download(downloads=task)
        print("download ok!")

    except Exception as e:
        print("\n\n====== EXCEPTION:", e)

    try:  
        tagRules=[]
        tagRules.append(TagRule(key="resource",value="test",kvFilter=BlobFilter(ftype="pattern",filterDefinition="*")))
        log=cloud.Upload(localDirectory="C:/temp/lego",cloudDirectory="lego",tagRules=tagRules,publicRules=[],recursiveUpload=True)
        print("upload ok!")

    except Exception as e:
        print("\n\n====== EXCEPTION:", e)

    try:  
        status=cloud.Directory(cloudDirectory="lego/pageserver")
        if status==None:
            print("Directory does not exist")
        else:
            print(json.dumps(status,default=lambda x: x.__dict__))
        print("directory retrieval ok!")

    except Exception as e:
        print("\n\n====== EXCEPTION:", e)


    server.Dispose()


if __name__ == '__main__':
    main()
```