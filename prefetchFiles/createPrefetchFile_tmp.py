import os
import sys
import subprocess

# modify these paths to include full absolute path
path_to_dataset = "{ADDME]" # dataset/benchmark folder
path_to_prefetchFiles = "[ADDME]" # prefetchFiles folder
path_to_prediction = "[ADDME]" # seqFiles/benchmark folder

# path to config file, this is written by run script to enable or disable prefetch
with open(path_to_prefetchFiles+"/config.txt", "r") as f:
    configOption = f.read().rstrip().split('\n')
    prefetchType = configOption[0].split('-')

# template
tmp = sys.argv[2]

# path to queries
queryDir = path_to_query+"/"+tmp+"/queries/"
queries = os.listdir(queryDir)
queries.sort()

bID = sys.argv[1]

for query in queries:
    result = subprocess.run(['diff',queryDir+query,path_to_prefetchFiles+'/'+bID+'-query.txt'], stdout=subprocess.DEVNULL)
    ret_code = result.returncode

    if not ret_code:
        if "full" in prefetchType[0]:
            os.system('cp '+path_to_prediction+'/'+tmp+'/'+query+'_predSeq.txt '+path_to_prefetchFiles+'/'+bID+'-prefetch.txt')
            break
        elif "no" in prefetchType[0]:
            os.system('cp '+path_to_prefetchFiles+'/empty.txt '+path_to_prefetchFiles'/'+bID+'-prefetch.txt')
            break
        else:
            print("WRONG CONFIG")
            exit(1)

