This folder contains scripts to run queries on Postgres with prefetch from Pythia enabled.
1. concurrentRun.py can be used to run multiple queries with varying overlap of concurrency.
   The identify workload script in prefetchFiles will select appropriate prefetch file and so should NOT exit prematurely.
2. genericRunTestQueries.py can be used to run queries individually in isolation.
   The identify workload script in prefetchFiles is NOT needede and so should exit prematurely.

For these scripts to work, modify them to include full absolute paths of required folders in each script.\
They are marked with [ADDME] tag.
