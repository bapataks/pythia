import os
import sys
import subprocess

with open("/home/akshay/seqFiles/prefetchFiles/config.txt", "r") as f:
    configOption = f.read().rstrip().split('\n')
    prefetchType = configOption[0].split('-')

tmp = sys.argv[2]

queryDir = "/home/akshay/seqFiles/final_exp/queries/"+tmp+"/"
queries = os.listdir(queryDir)
queries.sort()

bID = sys.argv[1]

for query in queries:
    result = subprocess.run(['diff',queryDir+query,'/home/akshay/seqFiles/prefetchFiles/'+bID+'-query.txt'], stdout=subprocess.DEVNULL)
    ret_code = result.returncode

    if not ret_code:
        if "full" in prefetchType[0]:
            os.system('cp '+'/home/akshay/seqFiles/final_exp/predicted/'+tmp+'/with_nonleaf_idx/'+query+'_predSeq.txt /home/akshay/seqFiles/prefetchFiles/'+bID+'-prefetch.txt')
            break
        elif "no" in prefetchType[0]:
            os.system('cp '+'/home/akshay/seqFiles/empty.txt /home/akshay/seqFiles/prefetchFiles/'+bID+'-prefetch.txt')
            break
        elif "oracle" in prefetchType[0]:
            os.system('cp '+'/home/akshay/seqFiles/final_exp/oracle/'+tmp+'/'+query+'_Rshort /home/akshay/seqFiles/prefetchFiles/'+bID+'-prefetch.txt')
            break
        else:
            print("WRONG CONFIG")
            exit(1)
        '''
        elif "prefetch" in prefetchType[1]:
            os.system('cp '+'/home/akshay/seqFiles/final_exp/predicted/'+prefetchType[0]+'_'+tmp+'/with_nonleaf_idx/'+query+'_predSeq.txt /home/akshay/seqFiles/prefetchFiles/'+bID+'-prefetch.txt')
            break
        elif "subset" in prefetchType[1]:
            os.system('cp '+'/home/akshay/seqFiles/final_exp/predicted/subset_'+prefetchType[0]+'_'+tmp+'/'+query+'_predSeq.txt /home/akshay/seqFiles/prefetchFiles/'+bID+'-prefetch.txt')
            break
        '''
