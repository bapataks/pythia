import os
import time
import pickle

# params: ["input query", "prefetch type", "input prefetch", "result subfolder", "result file name"]

resDir = "resultFiles"

for run in runParams:
    # reset prefetch file
    os.system('cp empty.txt <path_to_prefetchFiles>/3-prefetch.txt')

    # fetch test queries
    inpFolder = run[0]
    testQueries = os.listdir('<path_to_queries>/'+inpFolder+'/')
    testQueries.sort()
    print(testQueries)

    # set run config
    timeDict = {}
    if run[1] == "":
        os.system('cp empty.txt prefetchFiles/3-prefetch.txt')
        prefetch = False
    else:
        prefetchFolder = run[2]
        prefetchType = run[1]
        prefetch = True
    resFile = resDir + "/" + run[3] + "/" + run[4] + ".pickle"

    print(testQueries)

    # run queries
    for file in testQueries:
        # reset prefetch file
        os.system('cp empty.txt prefetchFiles/3-prefetch.txt')

        print(run, file)
        if prefetch:
            if prefetchType == "predicted":
                os.system('cp final_exp/predicted/'+prefetchFolder+'/' + file + '_predSeq.txt prefetchFiles/3-prefetch.txt')
            else:
                print("WRONG OPTION PROVIDED")
                exit(1)
        os.system('free -h')
        os.system('sync')
        time.sleep(2)
        os.system('sudo sh -c \'echo 1 > /proc/sys/vm/drop_caches\'')
        os.system('free -h')
        os.system('pg_ctl -D ~/research/aio_postgres/pgsql/data start')

        time.sleep(5)

        tic = time.perf_counter()
        os.system('psql -d dsb100 -f final_exp/queries/'+inpFolder+'/' + file + ' > tmpresult 2> tmperror')
        toc = time.perf_counter()

        os.system('pg_ctl -D ~/research/aio_postgres/pgsql/data stop')
        time.sleep(2)

        timeDict[file] = float(toc - tic)

    print(timeDict)
    with open(resFile, 'wb') as handle:
        pickle.dump(timeDict, handle, protocol=pickle.HIGHEST_PROTOCOL)

