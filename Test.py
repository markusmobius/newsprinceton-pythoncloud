import os
import json

from RemoteBlobStore.Remote.Runners.CloudMachine import CloudMachine
from RemoteBlobStore.Remote.Runners.DownloadTask import DownloadTask, DirectorySet
from RemoteBlobStore.Remote.RemoteBlobServer import RemoteBlobServer
from RemoteBlobStore.Remote.Runners.UploadTask import TagRule, BlobFilter

def main():
    server = RemoteBlobServer()
    cloud = CloudMachine(port=server.port,clientHash=os.getenv("CLOUDPDS_CLIENT_HASH"),serverUrl="https://www.legopds.projectratio.net:6008")
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