import os
import time
import pickle
import random
import subprocess
import numpy as np

## revision experiment
## inject delays for queries
## use multiple workloads

def getInterArrivalTime(fractionOverlap):
  expRT = 619 # expected runtime of tmp-18 queries
  return expRT * ((1 - fractionOverlap)/(1 + fractionOverlap))

saveOutput = False
runs = 10
useOldTestQueries = True

resultDIR = "resultFiles/concurrentRevision/"

totalQueries = 5
# second delay from start
#delayMax = 0

fractionOverlap = 0.25
delayMax = getInterArrivalTime(fractionOverlap) # based on inter arrival time


#templates = ["tmp018", "leaftmp019", "tmp091"]
templates = ["tmp018"]
configs = ["no-prefetch", "full-prefetch"]

allQueries = []
# gather all queries
for tmp in templates:
  queries = os.listdir("final_exp/queries/"+tmp+"/")
  for q in queries:
    allQueries.append("final_exp/queries/"+tmp+"/"+q)
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
    with open("prefetchFiles/config.txt", "w") as f:
      f.write(cfg + "\n")

    # start server
    os.system('free -h')
    os.system('sync')
    time.sleep(2)
    os.system('sudo sh -c \'echo 1 > /proc/sys/vm/drop_caches\'')
    os.system('free -h')
    os.system('pg_ctl -D ~/research/aio_postgres/pgsql/data start')
    time.sleep(5)

    count = 0
    curIndex = 0

    if delayMax > 0:
      startTime = time.perf_counter()

      while len(completedDict) < len(testQueries):
        if curIndex < totalQueries and testQueries[curIndex][1] < float(time.perf_counter() - startTime):
          processDict[testQueries[curIndex][0]] = subprocess.Popen(["psql", "-d", "dsb100", "-f", testQueries[curIndex][0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        processDict[query[0]] = subprocess.Popen(["psql", "-d", "dsb100", "-f", query[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

    os.system('pg_ctl -D ~/research/aio_postgres/pgsql/data stop')
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
    with open(resultDIR+str(totalQueries)+"-execTimeDict-t18-"+str(fractionOverlap)+".pickle", "wb") as handle:
      pickle.dump(execTimeDict, handle, protocol=pickle.HIGHEST_PROTOCOL)

exit(0)

# code after this not used

for numQueries in [2,3,4,5]:
    if not useOldTestQueries:
        testListDict = {}
        while len(testListDict) < runs:
            testList = []
            while len(testList) < numQueries:
                testList.append(queries[random.randint(0,len(queries)-1)])
                testList.sort()

            if ":".join(testList) not in testListDict:
                testListDict[":".join(testList)] = 1
    else:
        with open("resultFiles/multiQuery/"+template+"/"+str(numQueries)+"-full-prefetch-execTimeDict.pickle", "rb") as handle:
            testListDict = pickle.load(handle)

    #workList = [("full", "prefetch"), ("20k", "subset"), ("40k", "subset"), ("60k", "subset"), ("no", "prefetch")]
    workList = [("5k", "subset")] #[("5k", "subset")]

    for cfg in workList:
        subsetSize = cfg[0]
        prefetchType = cfg[1]

        with open("prefetchFiles/config.txt", "w") as f:
            f.write(template + "\n")
            f.write(str(numQueries) + "\n")
            f.write(subsetSize + "-" + prefetchType + "\n")

        if "full" in subsetSize:
            prefetchDIR = "final_exp/predicted/"+template+"/with_nonleaf_idx/"
        elif "prefetch" in prefetchType:
            prefetchDIR = "final_exp/predicted/"+subsetSize+"_"+template+"/with_nonleaf_idx/"
        else:
            prefetchDIR = "final_exp/predicted/subset_"+subsetSize+"_"+template+"/"

        prefetchUnionDict = {}
        fullUnionDict = {}
        scoreDict = {}
        execTimeDict = {}

        for test in testListDict:
            print(numQueries, subsetSize, prefetchType, test)
            #with open("prefetchFiles/config.txt", "a") as f:
            #    f.write(test+"\n")
            testList = test.split(":")

            os.system('cp '+'/home/akshay/seqFiles/empty.txt /home/akshay/seqFiles/prefetchFiles/lockFile.lck')
            for bid in ["3", "4", "5", "6", "7"]:
                os.system('cp '+'/home/akshay/seqFiles/empty.txt /home/akshay/seqFiles/prefetchFiles/'+bid+'-prefetch.txt')

            os.system('free -h')
            os.system('sync')
            time.sleep(2)
            os.system('sudo sh -c \'echo 1 > /proc/sys/vm/drop_caches\'')
            os.system('free -h')
            os.system('pg_ctl -D ~/research/aio_postgres/pgsql/data start')
            time.sleep(5)

            #fill prefetchUnionDict
            if "no" not in subsetSize:
                punion = {}
                for query in testList:
                    with open(prefetchDIR+query+"_predSeq.txt", "r") as f:
                        pages = [line.rstrip().lstrip() for line in f]

                    for page in pages:
                        if page not in punion:
                            punion[page] = 1
                        else:
                            punion[page] += 1

                prefetchUnionDict[":".join(testList)] = punion

            #fill fullUnionDict
            if "no" not in subsetSize:
                funion = {}
                for query in testList:
                    with open(fullDIR+query+"_Rshort", "r") as f:
                        pages = [line.rstrip().lstrip() for line in f]

                    for page in pages:
                        if page not in funion:
                            funion[page] = 1
                        else:
                            funion[page] += 1

                fullUnionDict[":".join(testList)] = funion

            #calc scoreDict
            if "no" in subsetSize:
                scoreDict[":".join(testList)] = 0.0
            else:
                score = 0
                for k in punion.keys():
                    if k in funion:
                        score += 1

                scoreDict[":".join(testList)] = score/len(funion)

            # start run
            processList = []
            if saveOutput:
                outFiles = {}
                for query in testList:
                    outFiles[query] = open(query+"-outfile.txt", "w")

            tic = time.perf_counter()

            if saveOutput:
                for query in testList:
                    processList.append(subprocess.Popen(["psql", "-d", "dsb100", "-f", queryDIR+query], stdout=outFiles[query], stderr=subprocess.DEVNULL))
            else:
                for query in testList:
                    processList.append(subprocess.Popen(["psql", "-d", "dsb100", "-f", queryDIR+query], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

            for child in processList:
                child.wait()

            toc = time.perf_counter()
            execTimeDict[":".join(testList)] = float(toc - tic)

            if saveOutput:
                for query in testList:
                    outFiles[query].close()

            os.system('pg_ctl -D ~/research/aio_postgres/pgsql/data stop')
            time.sleep(2)

        if saveOutput:
            os.system('mv *outfile* '+str(numQueries)+'-query-outputs/'+subsetSize+'-'+prefetchType+'/')

        with open(resultDIR+str(numQueries)+"-"+subsetSize+"-"+prefetchType+"-execTimeDict.pickle", "wb") as handle:
            pickle.dump(execTimeDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(resultDIR+str(numQueries)+"-"+subsetSize+"-"+prefetchType+"-scoreDict.pickle", "wb") as handle:
            pickle.dump(scoreDict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        print(sum(list(execTimeDict.values()))/runs)
        print(sum(list(scoreDict.values()))/runs)
