# Pythia

Following is included in this repo:
1. Patch file to enable query level AIO with postgres
2. Datasets on which we tested it out (3 DSB templates and 1 IMDB template)
  The training and testing files are included and the queries that were part of the workload for every template. There is a train and test set for every index and base table file for every template. The input file for index and base table files is shared between them. Along with that, also included are postgres query plans for all the queries.
  The input files for train and test sets will have to be converted to a suitable dictionary encoding before they can be injested by the model. The output files are directly ready to be ingested by the model when training. Some files, which were larger than the github limit, are compressed to save space. Please unzip them before starting to use any of the given scripts, otherwise they would fail with a "File not found" error. IMDB dataset only has 1 table data as just that one is big enough to fill the buffer by itself.
3. Model used for the prediction of accessed pages.
4. Sample scripts to train the model for any given template and a relation. The script to preprocess serailized query plan into a suitable one-hot encoding such that they can be injested by any ML model is also present.
5. Sample scripts to infer from any trained model. There are 2 scripts one each for generating a prediction sequence and for calculating F1-score of the prediction.
6. Sample scripts to run queries on Postgres with an option to either enable or disable prefetching. There are 2 scripts one each for simulating cold cache (individual query), and hot cache (multiple queries, including concurrent) behaviour.
7. Sample scripts used by Postgres to identify if a scheduled query belongs to a workload (for DSB templates 18, 19 and 91 only) and ready the prefetch sequence (already inferred) for Postgres to start prefetching.
8. Postgres sample configuration file.
9. Requirements.txt for dependencies.


Train and Test
--------------
If you want to use the given datasets,
From the root folder, run the following command:

1. python setup.py
   This command prepares the directory structure for the other scripts to run.
   It also unzips the compressed files so that they can be used.
3. python fullTrainAndTest.py <benchmark> <template>
   This command trains models for a particular template workload and
   subsequently prints F1-score for all test queries.
   
Sample: python fullTrainAndTest.py dsb tmp018
  The above command internally does the following steps for template 18 of DSB which can be run separately if needed.
  1. Encode serialized input file to create a vocabulary object for a relation. ("train\_scripts/preprocess.py")
  2. Train models for a relation. ("train\_scripts/train.py")
  3. Generate prediction sequence for all test files. ("infer\_scripts/genSeq.py")
  4. Calculate F1-score for all test file predictions. ("infer\_scripts/testAcc.py")

Load Database
-------------
We have not provided the database with this repository.
To create one yourself:
  1. Get DSB (https://github.com/microsoft/dsb) benchmark
  2. Follow steps to generate data (script in DSB).
  3. Load into postgres (scripts provided in DSB).
  4. Apply the patchFile in "aio\_postgres" to enable prefetching. Visit README in that folder for more details.
  5. Every new database will have its own database and relation identifiers.
  6. These will have to be updated accordingly to enable proper prefetching and tracing. More details in README in "aio\_postgres"

Run and Prefetch
----------------
The scripts to run queries on Postgres are in "run\_scripts".
The following is how Pythia is integrated into Postgres and behaves when a query is run.

  1. Postgres looks for scripts inside "prefetchFiles".
  2. The "idenitfyTemplate\_createPrefetch.py" should "exit(0)" right away if run with "genericRunTestQueries.py".
     This is because this script copies prefetch file directly.
  3. If using "concurrentRun.py", Postgres will use "idenitfyTemplate\_createPrefetch.py" to identify the template and copy the prefetch sequnce from "seqFiles" to "prefetchFiles" by itself.
  4. To disable prefetch, replace "3-prefetch.txt" with "empty.txt". Empty file will basically tell Postgres to not prefetch.

To use run scripts:
  1. First, use README in "aio\_postgres" to setup Postgres.
  2. Set run parameters in the script file, detailed comments are in the script.
  3. Use "genericRunTestQueries.py" for cold cache setting and "concurrentRun.py" for hot cache or concurrent execution.

