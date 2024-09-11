import os
import sys
import time
import torch

sys.path.append(os.getcwd())
from common.databaseConstants import *
from common.embedQuery import *
from common.inferHelpers import *
from common.model import TransformerEncoderModel
from common.utils import *

def writePages(file, rel, part, query, vocab, model):
  input = torch.LongTensor(getIdxSeqFromPages(query, vocab)).to(device)
  input = input.unsqueeze(1)

  with torch.no_grad():
    output = model(input).sigmoid()

  output = output.squeeze(0)

  for page in range(len(output)):
    if part == "idx":
      actualPage = idxT[rel] + str(page)
    else:
      actualPage = baseT[rel] + str(page + (int(part) * 500000))

    if output[page].item() > 0.5:
      file.write(actualPage + "\n") 

def writeIndexPages(planSeq, seqOut, query, vocab, mI):
  for node in planSeq:
    if "HJ" in node:
      continue

    for filenode in invFilenode:
      if filenode in node:
        rel = invFilenode[filenode]
        if rel not in vocab:
          print("Warning: One of the models not found - {}".format(rel))
        else:
          writePages(seqOut, rel, "idx", query, vocab[rel], mI[rel])
        break

def writeBasePages(planSeq, seqOut, query, vocab, mR):
  for node in planSeq:
    if "HJ" in node:
      continue

    for filenode in invFilenode:
      if filenode in node:
        rel = invFilenode[filenode]
        if rel not in vocab:
          print("Warning: One of the models not found - {}".format(rel))
        else:
          writePages(seqOut, rel, "0", query, vocab[rel], mR[rel])
        break

def generateSequenceFile(seqFile, planSeq, query, vocab, mI, mR):
  seqOut = open(seqFile, "w")

  writeIndexPages(planSeq, seqOut, query, vocab, mI)
  writeBasePages(planSeq, seqOut, query, vocab, mR)

  seqOut.close()

if __name__ == "__main__":
  if len(sys.argv) != 3 and len(sys.argv) != 4:
    print("Usage: python infer_scripts/genSeq.py <dataset> <template> [<file>]")
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
    testFiles = filter(lambda x: x.startswith("t"), files)

  # check if the models are present
  model_folder = os.path.join("models", sys.argv[1], sys.argv[2])
  if not os.path.exists(model_folder):
    print("Model folder not found")
    exit(7)

  # check if the output folder exists
  seq_folder = os.path.join("seqFiles", sys.argv[1], sys.argv[2])
  if not os.path.exists(seq_folder):
    print("Sequence predictin folder not found")
    exit(8)

  print("Generating prediction sequence for {}".format(tmp_folder))
  print(testFiles)

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

    for file in testFiles:
      qEmbed = getEmbed(tmp_folder, file)
      seqFile = os.path.join(seq_folder, file+"_predSeq.txt")
      seqOut = open(seqFile, "w")

      writePages(seqOut, relationDict[sys.argv[2]], "0", qEmbed, vocabDict[relationDict[sys.argv[2]]], modelIMDB)

      seqOut.close()
    exit(0)

  # Resume for DSB workloads
  modelIdxDict, modelMainDict = loadModels(model_folder, relationDict[sys.argv[2]], vocabDict)

  tic = time.perf_counter()
  for file in testFiles:
    qEmbed, tabSeq = getEmbed(tmp_folder, file)
    generateSequenceFile(os.path.join(seq_folder, file+"_predSeq.txt"), tabSeq, qEmbed, vocabDict, modelIdxDict, modelMainDict)

  toc = time.perf_counter()
  print(f"Time taken to generate prediction sequences - {toc - tic:0.4f} seconds")

  print("Prediction sequence written to {}".format(seq_folder))
