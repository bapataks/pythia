This patch file should be applied over AIO repository https://github.com/anarazel/postgres/tree/aio

The above repository with AIO code will enable AIO for postgres.
The patch will make changes such that AIO can be done on a query basis based on a file that maintain pages to be prefetched.

1. Clone AIO repo into a folder.
2. Build and run postgres to test (refer to https://www.postgresql.org/docs/current/install-make.html)
3. Load the database to test.
4. Apply the patch file "enable_aio_postgres.patch".
5. Make changes to the code based on your database identifiers (these are set after creating a database and loading the data)
6. Build and run postgres to test.

Many paramaetrs are hard coded into the code for now. These need to be set properly for it to work as expected.
The code is not tested and thus might not be suitable for a production environment.
There are debug related logs added in code (they are commented out right now but can be enabled if needed).
Following chnages need to be done based on the created database after applyiung the patch file.
We have added [ADDME] in code to make it easier to find these locations.
1. In file ([path_to_postgres/src/backend/executor/execMain.c), add tablespace identifier (spcOid) for the database for which prefetching is to be enabled.
   scan->reln->rd_locator.spcOid = <ADDME>;
2. In file ([path_to_postgres/src/backend/executor/execMain.c), add database identifier (dbOid) for the database for which prefetching is to be enabled.
   scan->reln->rd_locator.dbOid = <ADDME>;
Both of these information can be found with the following query after your database is ready.
(select oid,dattablespace from pg_database where datname='[database_name]';)
(oid column is dbOid, dattablespace column is spcOid)
3. In file ([path_to_postgres/src/backend/executor/execMain.c), add full path to prefetchFiles folder
   char tmp_q[70] = "/<ADDME>/prefetchFiles/\0";
   char tmp_p[70] = "/<ADDME>/prefetchFiles/\0";
   char pyScriptCMD[150] = "python /<ADDME>/prefetchFiles/identifyTemplate_createPrefetch.py \0";

Following execution steps are performed in the normal setting after enabling prefetch:
1. Postgres backend will write a query text file. ([path_to_preftchFiles]/[backend-id]-query.txt)
2. It will then invoke a script that reads this query text file, writes a new file with a page prefetch list as predicted by the model ([path_to_preftchFiles]/[backend-id]-prefetch.txt)
   It searches for this script in "prefetchFiles".
3. Postgres reads this page prefetch list to prefetch pages during execution.

Added notes on the code changes:
1. In file ([path_to_postgres/src/backend/executor/execMain.c), under ExecutePlan function, the entire prefetch code can be enabled or disabled by setting a boolean value.
   This is particularly useful if only trracing is to be done to collect training data or postgres is to be run without prefetch from Pythia.
   bool includeNewCode = false;
2. Comment out the script call from postgres (that writes [path_to_preftchFiles]/[backend-id]-prefetch.txt file) if the prefetch file is being placed by another script (like genericRunTestQueries.py)
   The same can be achieved by exiting early from the script that postgres calls.
3. Using an empty file (empty.txt) as prefetch file will also disable prefetching.
4. To enable tracing, in file ([path_to_postgres/src/backend/storage/buffer/bufmgr.c), under ReadBufferExtended function
   1. Update the dbOid as used above
      if (reln->rd_locator.dbOid == <ADDME>)
   2. Update the relNumber for which tracing is to be enabled
      if (reln->rd_locator.relNumber > <ADDME>)
      This information can be found using the following SQL query
      (select oid,relname from pg_class where oid>dbOid;)
      We use dbOid here so that postgres internal tables, which are also in this table, do not clutter the result.
   3. Uncomment this codeblock to enable tracing.
      Trace includes ([fileIdentified_blockOffset) where the file identifier is the same as relation identifier (placed within a folder with database identifier name within the postgres data directory)
   4. Enable printing of trace messages by changing the "client_min_messages" parameter in "postgresql.conf" file.
5. To enable any debug traces (mostly in file [path_to_postgres/src/backend/storage/buffer/bufmgr.c) use similar steps as above.

Along with the database identifier, the individual relation identifiers will also need to be updated in "common/databaseConstants.py".
This makes the Pythia models to predict correct filenames and block offsets which are then used by postgres as page identifiers during prefetching.
