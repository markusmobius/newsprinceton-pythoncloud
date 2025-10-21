import os
from RemoteBlobStore.DataVersionMachine import DataVersionMachine

def main():
    machine=DataVersionMachine(clientHash=os.getenv("legocloud_clienthash"),serverUrl="https://www.legocloud.projectratio.net:6002",cacheFolder="c:/temp")
    config={"key1":"this is a test","key2":"this is really a test","key2":"this is really a test - another one!"}
    tempFileName=machine.getTempFile(config)
    with open(tempFileName, "w") as f:
        f.write("This is a new file with some dummy content ...")
    machine.saveVersion(tempFileName=tempFileName,cloudPath="pds/test",config=config)

if __name__ == '__main__':
    main()