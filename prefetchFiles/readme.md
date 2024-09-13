This folder holds the files that Postgres will use to perform the following tasks:
1. Identify if the current query belongs to a particular workload (template)\
   We are only doing this for DSB benchmark currently (templates 18,19 and 91)
2. Find prediction sequence (already generated in seqFiles) of the query and write prefetch file for Postgres to use.

For these scripts to work, modify them to include full absolute paths of required folders in each script.\
They are marked with [ADDME] tag.
