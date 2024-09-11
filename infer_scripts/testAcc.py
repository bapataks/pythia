import os
import sys
import torch

sys.path.append(os.getcwd())
from common.databaseConstants import *
from common.embedQuery import *
from common.inferHelpers import *
from common.model import TransformerEncoderModel
from common.utils import *

def getVal(rel, query, vocab, model, testInpFile, testOutFile):
  tp = 0
  fp = 0
  fn = 0

  input = torch.LongTensor(getIdxSeqFromPages(query, vocab)).to(device)
  input = input.unsqueeze(1)

  with torch.no_grad():
    output = model(input).sigmoid()

  output = output.squeeze(0)

  with open(testInpFile, "r") as f:
    lines = [line.lstrip().rstrip().split(',') for line in f]
  for targetIdx in range(len(lines)):
    if lines[targetIdx] == query:
      break

  with open(testOutFile, "r") as f:
    lines = [line.lstrip().rstrip().split(',') for line in f]
  target = lines[targetIdx]

  target_dict_page = {}
  output_dict_page = {}

  for idx in range(len(output)):
    if output[idx].item() > 0.5:
      output_dict_page[idx] = 1
    if target[idx] == "1":
      target_dict_page[idx] = 1

  for k in output_dict_page.keys():
    if k in target_dict_page:
      tp += 1
    else:
      fp += 1

  for k in target_dict_page.keys():
    if k not in output_dict_page:
      fn += 1

  return tp, fp, fn

def calculatePRF1(tp, fp, fn, relKeys):
  p = {}
  r = {}
  f1 = {}

  for k in relKeys:
    if tp[k] == -1:
      p[k] = -1
      r[k] = -1
      f1[k] = -1
      continue

    if tp[k] + fp[k] == 0:
      fp[k] += 1
    if tp[k] + fn[k] == 0:
      fn[k] += 1

    p[k] = float(tp[k])/(tp[k] + fp[k])
    r[k] = float(tp[k])/(tp[k] + fn[k])
    if (p[k] + r[k] == 0):
      f1[k] = 0.0
    else:
      f1[k] = (2*p[k]*r[k])/(p[k]+r[k])

  return p, r, f1

def tst_model(query, planSeq, vocab, mI, mR, relKeys, testInpDict, testOutDict):
  tpD = {"ALL": 0}
  fpD = {"ALL": 0}
  fnD = {"ALL": 0}

  for k in relKeys:
    tpD[k] = -1
    fpD[k] = -1
    fnD[k] = -1

  for node in planSeq:
    if "HJ" in node:
      continue

    for filenode in invFilenode:
      if filenode in node:
        rel = invFilenode[filenode]
        if rel not in vocab:
          print("Warning: One of the models not found - {}".format(rel))
        else:
          tp, fp, fn = getVal(rel, query, vocab[rel], mI[rel], testInpDict[rel], testOutDict[rel]["idx"])
          tpD[rel] += tp + 1
          fpD[rel] += fp + 1
          fnD[rel] += fn + 1
          tp, fp, fn = getVal(rel, query, vocab[rel], mR[rel], testInpDict[rel], testOutDict[rel]["0"])
          tpD[rel] += tp
          fpD[rel] += fp
          fnD[rel] += fn
        break

  for k in relKeys:
    if tpD[k] != -1:
      tpD["ALL"] += tpD[k]
      fpD["ALL"] += fpD[k]
      fnD["ALL"] += fnD[k]

  return calculatePRF1(tpD, fpD, fnD, relKeys+["ALL"])
 
if __name__ == "__main__":
  if len(sys.argv) != 3 and len(sys.argv) != 4:
    print("Usage: python infer_scripts/testAcc.py <dataset> <template> [<file>]")
    exit(1)

  # check if template workload exists
  tmp_folder = os.path.join("dataset", sys.argv[1], sys.argv[2])
  if not os.path.exists(tmp_folder):
    print("Incorrect path for template files")
    exit(2)

  if not os.path.exists(os.path.join(tmp_folder, "queries")):
    print("Incorrect path for query text")
    exit(3)

  if not os.path.exists(os.path.join(tmp_folder, "EAplans")):
    print("Incorrect path for query plans")
    exit(4)

  # gather all test files
  if len(sys.argv) == 4:
    if not os.path.exists(os.path.join(tmp_folder, "queries", sys.argv[3])):
      print("No such file")
      exit(5)

    if not sys.argv[3].startswith("t"):
      print("Not a test file")
      exit(6)

    testFiles = [sys.argv[3]]
  else:
    files = os.listdir(os.path.join(tmp_folder, "queries"))
    testFiles = filter(lambda x: x.startswith("t", files))

  # check if the models are present
  model_folder = os.path.join("models", sys.argv[1], sys.argv[2])
  if not os.path.exists(model_folder):
    print("Model folder not found")
    exit(7)

  vocabDict = loadVocab(os.path.join(tmp_folder, "train_test_files", "encoded_input"), relationDict[sys.argv[2]])

  # handle IMDB separately
  # We only have one model for the base table
  if sys.argv[1] == "imdb":
    modelIMDB = TransformerEncoderModel(
                  EMBEDDING_SIZE,
                  vocabDict[relationDict[sys.argv[2]]].n_words,
                  NHEAD,
                  HIDDEN_SIZE,
                  NUM_LAYERS,
                  DROPOUT,
                  sizeIMDB,
                  PAD_IDX,
                  device
                ).to(device)
    modelIMDB.load_state_dict(torch.load(os.path.join(modelFolder, sys.argv[3])))
    modelIMDB.eval()

    testInpFile = relationDict[sys.argv[2]]+"MLtest_input.csv"
    testOutFile = relationDict[sys.argv[2]]+"MLtest_output.csv"
    f1Dict = {}

    for file in testFiles:
      qEmbed = getEmbed(tmp_folder, file)

      tp, fp, fn = getVal(relationDict[sys.argv[2]], qEmbed, vocabDict[relationDict[sys.argv[2]]], modelIMDB, testInpFile, testOutFile)
      tpD = {"ALL": tp}
      fpD = {"ALL": fp}
      fnD = {"ALL": fn}
      p, r, f1 = calculatePRF1(tpD, fpD, fnD, ["ALL"])

      f1Dict[file] = f1["ALL"]

    print("F1 score for {}".format(tmp_folder))
    print(testFiles)
    print(f1Dict)

    exit(0)

  # Resume for DSB workloads
  modelIdxDict, modelMainDict = loadModels(model_folder, relationDict[sys.argv[2]], vocabDict)

  # initialize structures
  pAll = {"ALL": []}
  rAll = {"ALL": []}
  f1All = {"ALL": []}
  f1Dict = {}

  testInpDict = {}
  testOutDict = {}

  for rel in relationDict[sys.argv[2]]:
    pAll[rel] = []
    rAll[rel] = []
    f1All[rel] = []

    testInpDict[rel] = os.path.join(tmp_folder, "train_test_files", rel+"_MLtest_input.csv")
    testOutDict[rel] = {}
    for part in ["idx", "0"]:
      testOutDict[rel][part] = os.path.join(tmp_folder, "train_test_files", rel+fileIdent[part]+"MLtest_output.csv")

  for file in testFiles:
    qEmbed, tabSeq = getEmbed(tmp_folder, file)
    p, r, f1 = tst_model(qEmbed, tabSeq, vocabDict, modelIdxDict, modelMainDict, relationDict[sys.argv[2]], testInpDict, testOutDict)

    for k in relationDict[sys.argv[2]]:
      if p[k] != -1:
        pAll[k].append(p[k])
        rAll[k].append(r[k])
        f1All[k].append(f1[k])

    if p["ALL"] != -1:
      pAll["ALL"].append(p["ALL"])
      rAll["ALL"].append(r["ALL"])
      f1All["ALL"].append(f1["ALL"])
      f1Dict[file] = f1["ALL"]

  print("F1 score for {}".format(tmp_folder))
  print(testFiles)
  print(f1Dict)

