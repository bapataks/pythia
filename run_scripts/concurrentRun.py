import os
import time
import pickle
import random
import subprocess
import numpy as np

## script to
## inject delays for queries
## using multiple workloads

# Modify the following for the script to work
path_to_result = "[ADDME]" # where the result files will be written
path_to_dataset = "[ADDME]" # dataset/benchmark folder
path_to_prefetchFiles = "[ADDME]" # path to prefetchFiles folder
path_to_postgres_data = "[ADDME]" # path to postgres data folder
database_name = "[ADDME]" # database name

def getInterArrivalTime(fractionOverlap):
  expRT = 619 # expected runtime of tmp-18 queries, change for other template
  return expRT * ((1 - fractionOverlap)/(1 + fractionOverlap))

saveOutput = False
runs = 10

totalQueries = 5
# second delay from start
#delayMax = 0

fractionOverlap = 0.25
delayMax = getInterArrivalTime(fractionOverlap) # based on inter arrival time

# add the templates here where the query can be scheduled from
# single template will make all queries be from the same template
templates = ["tmp018", "tmp019", "tmp091"]
#templates = ["tmp018"]
configs = ["no-prefetch", "full-prefetch"]

allQueries = []
# gather all queries
for tmp in templates:
  queries = os.listdir(path_to_dataset+"/"+tmp+"/queries")
  for q in queries:
    if q.startswith('t'):
      allQueries.append(path_to_dataset+"/"+tmp+"/queries/"+q)
allQueries.sort()

execTimeDict = {}
for cfg in configs:
  execTimeDict[cfg] = {}

for run in range(runs):
  print("Run number: " + str(run))
  # quereis on which we will test
  # sampled uniformly from allQueries without replacement
  # its a list of [query, arrivalTime] form
  # this list will be sorted by arrival time
  # for easier processing
  # smallest entry will be made 0, others adjusted accordingly
  testQueries = []
  testQueriesDict = {}

  # create test queries
  while len(testQueriesDict) < totalQueries:
    someIndex = random.randint(0,len(allQueries)-1)
    if allQueries[someIndex] not in testQueriesDict:
      #testQueries.append([allQueries[someIndex], random.randint(0, delayMax)])
      # using poisson distribution inter arrival time
      testQueries.append([allQueries[someIndex], np.random.exponential(delayMax, 1).item()])
      testQueriesDict[allQueries[someIndex]] = 1

  # sort them with arrival time
  if delayMax > 0:
    testQueries.sort(key=lambda x:x[1])
    print(testQueries)
    offset = testQueries[0][1]
    for i in range(len(testQueries)):
      testQueries[i][1] -= offset
    print(testQueries)

  for cfg in configs:
    print("Config: " + cfg)
    completedDict = {}
    startDict = {}
    processDict = {}

    # write config
    with open(path_to_prefetchFiles+"/config.txt", "w") as f:
      f.write(cfg + "\n")

    # start server
    os.system('free -h')
    os.system('sync')
    time.sleep(2)
    os.system('sudo sh -c \'echo 1 > /proc/sys/vm/drop_caches\'')
    os.system('free -h')
    os.system('pg_ctl -D '+path_to_postgres_data+' start')
    time.sleep(5)

    count = 0
    curIndex = 0

    if delayMax > 0:
      startTime = time.perf_counter()

      while len(completedDict) < len(testQueries):
        if curIndex < totalQueries and testQueries[curIndex][1] < float(time.perf_counter() - startTime):
          processDict[testQueries[curIndex][0]] = subprocess.Popen(["psql", "-d", database_name, "-f", testQueries[curIndex][0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
          startDict[testQueries[curIndex][0]] = time.perf_counter()
          curIndex += 1

        for child in list(processDict.keys()):
          if processDict[child].poll() is not None:
            completedDict[child] = time.perf_counter()
            del processDict[child]

        time.sleep(1)
        count += 1

    else:
      startTime = time.perf_counter()
      for query in testQueries:
        processDict[query[0]] = subprocess.Popen(["psql", "-d", database_name, "-f", query[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        startDict[query[0]] = time.perf_counter()        

      while len(completedDict) < len(testQueries):
        for child in list(processDict.keys()):
          if processDict[child].poll() is not None:
            completedDict[child] = time.perf_counter()
            del processDict[child]

        time.sleep(1)

      endTime = 0.0
      for et in list(completedDict.values()):
        if et > endTime:
          endTime = et

    print(startDict)
    print(completedDict)

    os.system('pg_ctl -D '+path_to_postgres_data+' stop')
    time.sleep(2)

    # calculate runtime
    rt = 0.0
    key = ""
    for i in range(totalQueries):
      rt += float(completedDict[testQueries[i][0]] - startDict[testQueries[i][0]])
      key += testQueries[i][0] + ":"
    execTimeDict[cfg][key] = [rt]

    if delayMax == 0:
      execTimeDict[cfg][key].append(float(endTime - startTime))

    print(execTimeDict)
    with open(path_to_result+"/"+str(totalQueries)+"-execTimeDict-"+"-".join(templates)+"-"+str(fractionOverlap)+".pickle", "wb") as handle:
      pickle.dump(execTimeDict, handle, protocol=pickle.HIGHEST_PROTOCOL)

