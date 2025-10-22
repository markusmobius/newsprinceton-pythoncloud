import os
from RemoteBlobStore.DataVersionMachine import DataVersionMachine

def main():
    machine=DataVersionMachine(clientHash=os.getenv("legopds_clienthash"),serverUrl="https://www.legopds.projectratio.net:6008",cacheFolder="c:/temp")
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