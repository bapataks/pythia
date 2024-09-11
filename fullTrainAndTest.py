from common.utils import *
import os
import subprocess
import sys

if len(sys.argv) != 3:
  print("Usage: python trainAndTest.py <dataset> <template>")
  exit(1)

train_folder = os.path.join("dataset", sys.argv[1], sys.argv[2], "train_test_files")
if not os.path.exists(train_folder):
  print("Incorrect path for training files")
  exit(2)

print("Encoding input files...")
for rel in relationDict[sys.argv[2]]:
  subprocess.run(["python", "train_scripts/preprocess.py", sys.argv[1], sys.argv[2], rel])

print("Training models...")
for rel in relationDict[sys.argv[2]]:
  subprocess.run(["python", "train_scripts/train.py", sys.argv[1], sys.argv[2], rel])

print("Generating prediction sequence...")
subprocess.run(["python", "infer_scripts/genSeq.py", sys.argv[1], sys.argv[2]])

print("Predicton Accuracy...")
subprocess.run(["python", "infer_scripts/testAcc.py", sys.argv[1], sys.argv[2]])
