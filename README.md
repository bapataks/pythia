# Pythia

Following is included in this repo:
1. Patch file to enable query level AIO with postgres
2. Datasets on which we tested it out (3 DSB templates and 1 IMDB template)
  The training and testing files are included and the queries thta were part of the workload for every template. There is a train and test set for every index and base table file for every template. The input file for index and base table files is shared between them. Along with that, also included are postgres query plans for all the queries.
  The input files for train and test sets will have to be converted to a suitable dictionary encoding. The output files are directly ready to be ingested by the model when training. 
3. Model used for the prediction of accessed pages.

To use these datasets:
1. Select a template.
2. Select a particular base table or index model to train.
3. Convert input files into dictionary encoded files.
4. Train a model using the given model and the corresponding input and output training files.
5. Use test files to test model performance.
6. Use test files to generate a page prefetch sequence files.
7. Use these files during query execution to test postgres performance.

Some files have been compressed to save space.
IMDB dataset only has 1 table data as just that one is big enough to fill the buffer by itself.
