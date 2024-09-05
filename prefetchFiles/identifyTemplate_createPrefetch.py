import os
import sys

# exit for now as prefetch is set in another script
exit(0)

bid = sys.argv[1]

# modify these paths to include full path to prefetchFiles folder

with open("<path_to_prefetchFiles>/"+bid+"-query.txt", "r") as f:
  lines = [line.strip() for line in f]

if "min(i_item_id)" in lines[1]:
  os.system("python <path_to_prefetchFiles>/createPrefetchFile_tmp.py " + bid + " tmp018")
elif "min(cc_call_center_id)" in lines[2]:
  os.system("python <path_to_prefetchFiles>/createPrefetchFile_tmp.py " + bid + " tmp091")
elif "min(i_brand_id), min(i_manufact_id)" in lines[1]:
  os.system("python <path_to_prefetchFiles>/createPrefetchFile_tmp.py " + bid + " tmp019")
else:
  print("WRONG TEMPLATE")
  exit(1)
