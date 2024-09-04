import os
import time
import pickle

# params: ["input query", "prefetch type", "input prefetch", "result subfolder", "result file name"]
#runParams = [["tmp091", "POsubset_1k_tmp091", "1k_tmp091", "pageonly_subset_selected"]]
#runParams = [["tmp018", "subset_1k_tmp018", "tmp018", "1k_subset"], ["tmp018", "subset_5k_tmp018", "tmp018", "5k_subset"], ["tmp018", "subset_10k_tmp018", "tmp018", "10k_subset"], ["tmp018", "subset_20k_tmp018", "tmp018", "20k_subset"], ["tmp018", "subset_40k_tmp018", "tmp018", "40k_subset"], ["tmp018", "subset_60k_tmp018", "tmp018", "60k_subset"]]
#runParams = [["tmp018", "subset_20k_tmp018", "tmp018", "20k_subset"], ["tmp018", "subset_40k_tmp018", "tmp018", "40k_subset"], ["tmp018", "subset_60k_tmp018", "tmp018", "60k_subset"]]

#runParams = [["tmp091", "oracle", "tmp091", "tmp091", "tempFile"], ["tmp091", "predicted", "tmp091/with_nonleaf_idx", "tmp091", "tmpFile2"]]

#runParams = [["imdb", "oracle", "subset_100k_imdb_1a", "imdb", "oracle_subset_100k_0-10"], ["imdb", "predicted", "subset_100k_imdb_1a_50", "imdb", "predicted_subset_100k_0-10_50"], ["imdb", "", "", "imdb", "normal_0-10"]]
#runParams = [["imdb", "oracle", "subset_100k_imdb_1a", "imdb", "oracle_subset_100k_90-110"]]

#runParams = [["imdb", "oracle", "tmp/t1795_182054", "t1795", "182054"]] #, ["imdb", "oracle", "tmp/t1795_182119", "t1795", "182119"], ["imdb", "oracle", "tmp/t1795_182143", "t1795", "182143"], ["imdb", "oracle", "tmp/t1795_182148", "t1795", "182148"], ["imdb", "oracle", "tmp/t1795_182162", "t1795", "182162"], ["imdb", "oracle", "tmp/t1795_182167", "t1795", "182167"], ["imdb", "oracle", "tmp/t1795_182171", "t1795", "182171"], ["imdb", "oracle", "tmp/t1795_182181", "t1795", "182181"]]

#runParams = [["imdb", "predicted", "subset_100k_imdb_1a_25", "imdb", "predicted_subset_100k_90-110_25"], ["imdb", "predicted", "subset_100k_imdb_1a_50", "imdb", "predicted_subset_100k_90-110_50"], ["imdb", "predicted", "subset_100k_imdb_1a_75", "imdb", "predicted_subset_100k_90-110_75"], ["imdb", "predicted", "subset_100k_imdb_1a_90", "imdb", "predicted_subset_100k_90-110_90"]]

#runParams = [["imdb", "oracle", "NN_subset_100k_imdb_1a", "imdb", "NN_subset_100k_0-10_110-130"]]
#runParams = [["imdb", "", "", "imdb", "tmp_90-110"]]
#runParams = [["imdb", "predicted", "subset_100k_imdb_1a_50", "imdb", "tmp_90-110"]]

#runParams = [["imdb_0-30", "", "", "macAks", "imdb_128_0-30"]]

# for buffer size
#runParams = [["tmp018", "oracle", "tmp018", "bufferSize", "tmp018_128_oracle"]]
#runParams = [["tmp018", "predicted", "tmp018/with_nonleaf_idx", "bufferSize", "tmp018_1024_predicted"]]
#runParams = [["tmp018", "", "", "bufferSize", "tmp018_4096_normal_small"]]

# hot cache
runParams = [["tmp018", "", "", "bufferReplace", "tmp018_lru_normal"], ["tmp018", "predicted", "tmp018/with_nonleaf_idx", "bufferPolicy", "tmp018_lru_predicted"]]

resDir = "resultFiles"
#resDir = "resultReadaheadDIR"

for run in runParams:
    # reset prefetch file
    os.system('cp empty.txt prefetchFiles/3-prefetch.txt')

    # fetch test queries
    inpFolder = run[0]
    testQueries = os.listdir('final_exp/queries/'+inpFolder+'/')
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

    #testQueries = testQueries[0:10] + testQueries[110:130]
    #testQueries = testQueries[:20]
    print(testQueries)
    #testQueries = ["t1884", "t2042"]
    #testQueries = [testQueries[93]]

    # run queries
    for file in testQueries:
        # reset prefetch file
        os.system('cp empty.txt prefetchFiles/3-prefetch.txt')

        print(run, file)
        if prefetch:
            if prefetchType == "predicted":
                os.system('cp final_exp/predicted/'+prefetchFolder+'/' + file + '_predSeq.txt prefetchFiles/3-prefetch.txt')
            elif prefetchType == "oracle":
                #os.system('cp final_exp/oracle/'+prefetchFolder+' prefetchFiles/3-prefetch.txt')
                os.system('cp final_exp/oracle/'+prefetchFolder+'/' + file + '_Rshort prefetchFiles/3-prefetch.txt')
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

