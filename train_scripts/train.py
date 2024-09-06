from common.model import TransformerEncoderModel
from common.modelConstants import *
from common.trainHelpers import *
from common.utils import *
import numpy as np
import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim

def train_model(inpFile, outFile, posFile, nTokens, modelFile):
  posW = torch.FloatTensor(np.load(posFile)).to(device)
  # prefer precision of model
  # over recall
  # make models more pessimistic in their prediction
  posW = posW / 2
  num_classes = posW.shape[0]

  # define our model
  model = TransformerEncoderModel(
            EMBEDDING_SIZE,
            nTokens,
            NHEAD,
            HIDDEN_SIZE,
            NUM_LAYERS,
            DROPOUT,
            num_classes,
            PAD_IDX,
            device
          ).to(device)

  # use default LR and betas
  optimizer = optim.Adam(model.parameters())
  criterion = nn.BCEWithLogitsLoss(pos_weight=posW)

  dataset = CustomDataset(inpFile, outFile)
  data_loader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=PadCollate(dim=0))

  prev_loss = 99999.9
  epoch_step = 1

  epoch = 0
  count = 0
  while True:
    epoch_loss = []
    tic = time.perf_counter()
    if epoch % epoch_step == 0:
      print(f"Epoch: {epoch}")

    for batch_index, (context, prediction) in enumerate(data_loader):
      input = torch.t(context).to(device)
      target = prediction.type(torch.FloatTensor).to(device)

      optimizer.zero_grad()
      output = model(input)

      loss = criterion(output, target)
      epoch_loss.append(loss.item())

      loss.backward()
      torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1)

      optimizer.step()

    toc = time.perf_counter()
    print(f"Time taken for epoch {epoch}: {toc - tic:0.4f} seconds")

    # check for stopping condition
    if float(prev_loss - np.mean(epoch_loss)) < STOP_LOSS_DELTA:
      count += 1
      if count >= STOP_LOSS_COUNT:
        break
    else:
      count = 0

    if float(np.mean(epoch_loss)) < prev_loss:
      prev_loss = float(np.mean(epoch_loss))

    if epoch % epoch_step == 0:
      print("Epoch_Loss - {}".format(float(np.mean(epoch_loss))))

    epoch += 1
    if epoch >= MAX_EPOCH:
      break

  print("Stopped after {} epochs".format(epoch))
  torch.save(model.state_dict(), modelFile)

if __name__ == "__main__":
  if len(sys.argv) != 4:
    print("Usage: python train_scripts/train.py <dataset> <template> <relation>")
    exit(1)

  train_folder = os.path.join("dataset", sys.argv[1], sys.argv[2], "train_test_files")
  print("Training model : {} - {}".format(train_folder, sys.argv[3]))

  # check if template workload exists
  if not os.path.exists(train_folder):
    print("Incorrect path for training files")
    exit(2)

  # handle IMDB separately
  if sys.argv[1] == "imdb":
    input_file = sys.argv[3]+"MLtrain_input.csv"
    output_file = sys.argv[3]+"MLtrain_output.csv"
    posFile = "posW_"+sys.argv[3]+".npy"

    vocab_obj = Vocab()
    vocab_obj.read_vocab_from_file(os.path.join(train_folder, "encoded_input", sys.argv[3]+"_vocab_file_input.csv"))

    train_model(os.path.join(train_folder, "encoded_input", input_file), os.path.join(train_folder, output_file), os.path.join(train_folder, posFile), vocab_obj.n_words, os.path.join(model_folder, sys.argv[3]))

    exit(0)

  parts = ["idx", "0"]
  input_file = sys.argv[3]+"_MLtrain_input.csv"
  output_files = {}
  posW_files = {}
  for p in parts:
    output_files[p] = sys.argv[3]+fileIdent[p]+"MLtrain_output.csv"
    posW_files[p] = "posW"+fileIdent[p]+sys.argv[3]+".npy"

  # check if training files exist
  if not os.path.exists(os.path.join(train_folder, "encoded_input", input_file)):
    print("Train input file does not exist")
    exit(3)

  for outFile in output_files.values():
    if not os.path.exists(os.path.join(train_folder, outFile)):
      print("Train output file does not exist: {}".format(outFile))
      exit(4)

  for posWFile in posW_files.values():
    if not os.path.exists(os.path.join(train_folder, posWFile)):
      print("Train posW file does not exist: {}".format(posWFile))
      exit(5)

  # check if output folder exists
  model_folder = os.path.join("models", sys.argv[1], sys.argv[2])
  if not os.path.exists(model_folder):
    print("Model folder not present")
    exit(6)

  vocab_obj = Vocab()
  vocab_obj.read_vocab_from_file(os.path.join(train_folder, "encoded_input", sys.argv[3]+"_vocab_file_input.csv"))

  tic = time.perf_counter()
  for p in parts:
    print("Training model for {}".format(nameIdent[p]))
    train_model(os.path.join(train_folder, "encoded_input", input_file), os.path.join(train_folder, output_files[p]), os.path.join(train_folder, posW_files[p]), vocab_obj.n_words, os.path.join(model_folder, sys.argv[3]+"_"+p))

  toc = time.perf_counter()

  print("Training complete for both models in {} seconds".format(float(toc - tic)))
  print("Models stored in {}".format(os.path.join(model_folder)))
