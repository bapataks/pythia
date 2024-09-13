import os
import time
import pickle

# Modify the following for the script to work
path_to_result = "[ADDME]" # where the result files will be written
path_to_dataset = "[ADDME]" # dataset/benchmark folder
path_to_prefetchFiles = "[ADDME]" # path to prefetchFiles folder
path_to_postgres_data = "[ADDME]" # path to postgres data folder
path_to_prediction = "[ADDME]" # path to seqFiles/benchmark folder
database_name = "[ADDME]" # database name

# params: ["template", "prefetch type", "result subfolder", "result file name"]
# prefetch type is "predicted" or "" for no prefetch
# sample below
runParams = [["tmp018", "predicted", "tmp018_result", "full_prefetch"]]

for run in runParams:
    # reset prefetch file
    os.system('cp '+path_to_prefetchFiles+'/empty.txt '+path_to_prefetchFiles+'/3-prefetch.txt')

    # fetch test queries
    testQueries = list(filter(lambda x:x.startswith('t'), os.listdir(path_to_dataset+"/"+run[0]+"/queries/")))
    testQueries.sort()
    print(testQueries)

    # set run config
    timeDict = {}
    if run[1] == "":
        os.system('cp '+path_to_prefetchFiles+'/empty.txt '+path_to_prefetchFiles+'/3-prefetch.txt')
        prefetch = False
    else:
        prefetchFolder = run[2]
        prefetchType = run[1]
        prefetch = True
    resFile = path_to_result + "/" + run[3] + "/" + run[4] + ".pickle"

    print(testQueries)

    # run queries
    for file in testQueries:
        # reset prefetch file
        os.system('cp '+path_to_prefetchFiles+'/empty.txt '+path_to_prefetchFiles+'/3-prefetch.txt')

        print(run, file)
        if prefetch:
            if prefetchType == "predicted":
                os.system('cp '+path_to_prediction+'/'+run[0]+'/'+file + '_predSeq.txt '+path_to_prefetchFiles+'/3-prefetch.txt')
            else:
                print("WRONG OPTION PROVIDED")
                exit(1)
        os.system('free -h')
        os.system('sync')
        time.sleep(2)
        os.system('sudo sh -c \'echo 1 > /proc/sys/vm/drop_caches\'')
        os.system('free -h')
        os.system('pg_ctl -D '+path_to_postgres_data+' start')

        time.sleep(5)

        tic = time.perf_counter()
        os.system('psql -d '+database_name+' -f '+path_to_dataset+'/'+run[0]+'/queries/'+file+' > tmpresult 2> tmperror')
        toc = time.perf_counter()

        os.system('pg_ctl -D '+path_to_postgres_data+' stop')
        time.sleep(2)

        timeDict[file] = float(toc - tic)

    print(timeDict)
    with open(resFile, 'wb') as handle:
        pickle.dump(timeDict, handle, protocol=pickle.HIGHEST_PROTOCOL)

