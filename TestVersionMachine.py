import os
from RemoteBlobStore.DataVersionMachine import DataVersionMachine, Stage

def main():
    machine=DataVersionMachine(clientHash=os.getenv("legopds_clienthash"),serverUrl="https://www.legopds.projectratio.net:6008",cacheFolder="c:/temp")
    stages=[Stage(code_version="1.0",config={"key1":"this is a test","key2":"this is really a test","key2":"this is really a test - another one!","key3":"This is the third key."})]
    print(f"Trying to locate data file for stage configuration {machine.getConfigJson(stages)}")
    localFileName=machine.loadVersion(cloudPath="pds/test",stages=stages)
    if localFileName==None:
        print("File has not been saved before")
        print("Creating temporary file")
        tempFileName=machine.getTempFile(stages)
        print("Writing data to temporary file")
        with open(tempFileName, "w") as f:
            f.write("This is a new file with some dummy content ...")
        print("Saving temporary data to cloud storage")
        machine.saveVersion(tempFileName=tempFileName,cloudPath="pds/test",stages=stages,logs=["this is a test log"])
    else:
        print("File exists!")
    
    print("Note: if you specify debug=True for loadVersion and saveVersion method it will not store to the cloud but only to local storage")

if __name__ == '__main__':
    main()