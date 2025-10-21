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

2. Install ```setuptools```
   ```
   pip install setuptools
   ```
   ```setuptools``` is necessary for managing Python packages and dependencies. It simplifies the process of distributing, installing, and managing Python packages.

3. Install ```RemoteBlobStore``` from this GitHub repository:
   ```
   pip install git+https://github.com/markusmobius/newsprinceton-pythoncloud
   ```
   
## Usage: Simple Store

```Tests/Test.py``` is used in this section to demonstrate an example usage of ```RemoteBlobStore``` in opening a single store.

1. Importing necessary Python classes from ```RemoteDataStore```:

   These general classes are required to set up and use ```RemoteDataStore```.
   ```
   from RemoteDataStore import RemoteDataServer, LoadAsyncMachine, MemReadBuffer, ChunkReader, ChunkReaderCore
   from RemoteDataStore.dataStore import idtype
   ```
   
   In this example, we aim to access CUV data. This data is currently stored in binary format, making it inaccessible for researchers to retrieve useful information.  ```RemoteDataStore``` helps by converting this binary data into a Python class (represented here as ```userData``` imported below). Researchers can then access its instance variables to retrieve the desired information.
   ```
   from RemoteDataStore.Implementations.CUV import userData
   ```
    
   

2. Setting up ```RemoteDataStore```:

    A ```RemoteDataServer``` must be initiated at the beginning of your analysis and disposed at the end of your program. All of your code must be placed within these two lines:
   
   ```
    server = RemoteDataServer()
    ...
    server.Dispose()
    ```
    
    Next, initiate a ```LoadAsyncMachine``` instance, called ```loader```, with the port of the recently created server as a parameter. This will serve as the data loader, containing methods that the researchers can use to open or load data for a specific ID, to name a few. We also have to specify the key type which in the case of CUV data is a string (user ID).
    
    ```
    loader = LoadAsyncMachine(server.port,idtype.str)
    ```

3. Access the data:

    First, load a particular dataset by using the method ```Open()``` with the data file path as a parameter. For example,
    
    ```
    dir_path = "//nerds21/CUV/2024_04_10_00_00_00/cuv.dat"
    loader.Open(dir_path)
    ```
    
    The CUV data store is essentially a huge dictionary that maps instance IDs to associated data. Retrieving data for all IDs simultaneously is highly time-consuming. ```RemoteDataStore``` offers efficient methods to load data for individual IDs as requested by researchers. More specifically, the data store divides the IDs into groups. This way, with a particular ID requested by the researcher, ```RemoteDataStore``` only needs to load the data for the group which contains that ID. 
    
    To familiarize yourself with the concept of group and IDs, look at this example:
     
    ```
    ids = loader.GetGroupedIdsCount()
    count = 0
    for subcount in ids:
        count = count + subcount
    print(f"Data store has {count} ids.")
    ```
    
    The method ```GetGroupedIdsCount()``` retrieves the list containing the size of each group, where each group comprises a list of ```userData``` IDs. The ```for``` loop above calculates the total number of ```userData``` IDs in the dataset by iterating through each group and adding its size (```subcount```) to the total count of ```userData``` IDs (```count```).
    
    Next, we will show you how to load a particular ```userData``` ID. The first crucial step is to initiate a worker:
    ```
    workerGUID = loader.GetWorker()
    ```
    The following example will show you how to load the data of the first 10 ```userData``` IDs that belong to the *first* group. The code chunk may appear lengthy and daunting, but we will break it down step-by-step below.
    ```
    loopcount = 0
    for i in range(0, ids[0]):
        loopcount = loopcount + 1
        if loopcount >= 10:
            break
        userID = loader.GetIdByGroup(0, i)
        set = loader.LoadChunk(workerGUID, userID)
        reader = ChunkReader()
        reader.core = ChunkReaderCore(MemReadBuffer(set))
        user = userData(True)
        user.readBinary(reader)
    ```
    The ```for``` loop has at most ```ids[0]``` iterations, which is the size of the first group. Since we are only interested in the first 10 ```userData``` IDs in this group, we use the counter ```loopcount``` which breaks the loop whenever it reaches 10.
    
    The method ```GetIdByGroup()``` helps you retrieve the ```userData``` ID at a particular position in any given group. The first parameter of the method is the index of the group, while the second parameter is the index of the ```userData``` ID of interest within that group. 
    
    The method ```LoadChunk()``` is used to request the ```RemoteDataServer``` to return the binary data for a particular ```userData``` ID (represented as ```userID```). Note that what ```LoadChunk()``` returns (i.e. ```set```) is binary data, which is not ready for analysis. Therefore, this part of the code,
    ```
    reader = ChunkReader()
    reader.core = ChunkReaderCore(MemReadBuffer(set))
    user = userData(True)
    user.readBinary(reader)
    ```
    aims to convert the binary data into an instance of the Python class ```userData``` (i.e. ```user```), which is accessible to the researchers. It is unnecessary to understand the underlying mechanism of ```ChunkReader```, ```ChunkReaderCore```, or ```MemReadBuffer```. Every information that the researcher wants to access is stored in various instance variables of ```user``` (e.g, ```user.source``` or ```user.sessions```).
    
## Usage: Parallel Store

```Tests/TestCUVparallel.py``` is used in this section to demonstrate an example usage of ```RemoteDataStore``` in opening several stores in parallel.

1. Importing necessary Python classes from ```RemoteDataStore```:

   These general classes are required to set up and use ```RemoteDataStore```.
   ```
   from RemoteDataStore import RemoteDataServer
   from RemoteDataStore.Remote.Runners.ParallelLoadAsyncMachine import ParallelLoadAsyncMachine
   from RemoteDataStore.Remote.Runners.ParallelLoadSelector import ParallelLoadSelector
   from RemoteDataStore.dataStore import idtype
   ```
   
   In this example we open two CUV stores simultaneously. Our goal is to process data for all users who were active on both days. We again add the CUV class to be able to read CUV data.
   ```
   from RemoteDataStore.Implementations.CUV import userData
   ```
    
   

2. Setting up ```RemoteDataStore```:

    A ```RemoteDataServer``` must be initiated at the beginning of your analysis and disposed at the end of your program. All of your code must be placed within these two lines:
   
   ```
    server = RemoteDataServer()
    ...
    server.Dispose()
    ```
    
    Next, initiate a ```ParallelLoadAsyncMachine``` instance, called ```loader```, with the port of the recently created server as a parameter. This will serve as the parallel data loader.
    
    ```
    loader = ParallelLoadAsyncMachine(server.port,idtype.str)
    ```

3. Add the data:

    We add the CUV data for two days:
        
    ```
    files=["//nerds21/CUV/2024_04_10_00_00_00/cuv.dat","//nerds21/CUV/2024_04_11_00_00_00/cuv.dat"]
    loader.AddDataStore(files[0])
    loader.AddDataStore(files[1])
    ```
    
    Once all the data files have been added we seal the store. This is a necessary step:
    ```
    selector=ParallelLoadSelector()
    selector.MinStores=2
    loader.SealStores(selector)        
    ```
    The selector allows us to include a set of IDs (by default the union of IDs across all added stores are included), exclude a set of IDs (by default none are excluded) and to focus on on IDs which appear in a minimum number of added stores (by default this is 1). In the above example, we focus on users who appear on both days.

    We can get a breakdown of the number of included and excluded IDs by using the ```GetStats()``` method:
    ```
    loader.GetStats().print()
    ```

    We can now retrieve the included IDs one-by-one:
    ```
    guid=loader.GetWorker()
    for i in range(10):
        nextID=loader.GetNextID(guid)
        if nextID==None:
            break
        print("-------------")
        print(f"ID: {nextID.id}")
        for storeID in nextID.sets:
            print(f"*** {files[storeID]}")
            #create reader
            reader = ChunkReader()
            reader.core = ChunkReaderCore(MemReadBuffer(nextID.sets[storeID]))
            #now convert to user
            user=userData(True)
            user.readBinary(reader)
            print(f"source: {user.source}")
            print(f"number of sessions: {len(user.sessions)}")
            if len(user.places)>0:
                print(f"country: {user.places[0].countryName}")
    ```

    We first call ```GetWorker``` to create a reader GUID. Different threads can call ```GetNextID``` method with different GUID in parallel (in our example we only use one). ```nextID``` is ```None``` if all IDs have been exhausted. Otherwise, a class is returned with an ID available at ```nextID.id``` and a dictionary of byte arrays with the key being the storeID (equal to the order in which the files were added) and the value being a byte array with the user data.



## Tips and tricks

1. It is recommended to install this Python package into a separate Python environment (as demonstrated in Step 1 under "Installation" section) to prevent package conflicts. It is also easier to locate the downloaded package if you decide to modify or remove it later.

2. Returning to the example in the "Usage" section above where we loaded the first 10 ```userData``` IDs in the first group, it is important to note that when the data store loads a given ID, it first loads the group that contains that ID, then the ID itself. Consequently, if a researcher requests to load another ID from the same group, the data store doesn't need to reload the group, resulting in significant time savings. This implies that researchers aiming to sample IDs should focus on sampling within the same group, as it is faster than sampling across different groups.

3. You must not open the same ```userData``` ID twice, which will throw an error.

