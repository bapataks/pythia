import os
import subprocess

folderDict = {}
benchmark = os.listdir("dataset")
for b in benchmark:
  folderDict[b] = os.listdir(os.path.join("dataset", b))

for rootFolder in ["models", "seqFiles"]:
  for benchmark in folderDict:
    for template in folderDict[benchmark]:
      os.makedirs(os.path.join(rootFolder, benchmark, template), exist_ok=True)

ttf = "train_test_files"

for benchmark in folderDict:
  for template in folderDict[benchmark]:
    if not os.path.exists(os.path.join("dataset", benchmark, template, ttf, "encoded_input")):
      os.mkdir(os.path.join("dataset", benchmark, template, ttf, "encoded_input"))

    files = os.listdir(os.path.join("dataset", benchmark, template, "train_test_files"))
    for file in files:
      if "tar.gz" in file:
        subprocess.run(["tar", "-xzf", os.path.join("dataset", benchmark, template, ttf, file), "-C", os.path.join("dataset", benchmark, template, ttf)])
        subprocess.run(["rm", os.path.join("dataset", benchmark, template, ttf, file)])
