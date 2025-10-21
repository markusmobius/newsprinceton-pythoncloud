import os
from importlib.resources import as_file, files
import subprocess
import threading
import uuid
import zipfile

from RemoteBlobStore.Utils.tempOrganizer import tempOrganizer


class RemoteBlobServer:
    def __init__(self):
        #print("server init")
        self.tempOrg = tempOrganizer()
        self.BaseDirectory = self.tempOrg.createTempDir("remoteblobserver")
        self.workingDir = os.path.join(self.BaseDirectory, str(uuid.uuid4()))
        os.makedirs(self.workingDir)
        #print("start unzipping")
        with as_file(files('RemoteBlobStore.Remote').joinpath('RemoteBlobServer.zip')) as zip_file_path:
            with zipfile.ZipFile(zip_file_path, 'r') as archive:
                archive.extractall(self.workingDir)
        #print("done unzipping")
        self.isReady = threading.Condition()
        self.startServer()


    def startServer(self):
        #print("enter start server")
        self.server = subprocess.Popen(
            ["dotnet", f"{self.workingDir}/RemoteBlobServer.dll"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            cwd=self.workingDir,
            text=True,
            bufsize=1  # line-buffered
        )

        self.isReadyFlag = False

        def read_stdout():
            """Read stdout line by line. First line = port; others printed."""
            first_line = True
            for line in self.server.stdout:
                if first_line:
                    line = line.strip()
                    try:
                        self.port = int(line)
                        self.isReadyFlag = True
                        with self.isReady:
                            self.isReady.notify()
                    except Exception as e:
                        raise Exception("cannot start remote server") from e
                    first_line = False
                else:
                    # Print exactly as received — don't strip \r
                    print(line, end='', flush=True)

        def read_stderr():
            """Print stderr lines as they come."""
            for line in self.server.stderr:
                print(line.strip(), flush=True)

        threading.Thread(target=read_stdout, daemon=True).start()
        threading.Thread(target=read_stderr, daemon=True).start()

        # Wait for the port line
        with self.isReady:
            self.isReady.wait(timeout=30)
            if not self.isReadyFlag:
                raise Exception("cannot start remote server")


    def closeClient(self):
        try:
            self.server.kill()
            self.server.wait()
        except Exception as e:
            print("close client failed: " + e)

    def Dispose(self):
        print("server dispose")
        self.closeClient()