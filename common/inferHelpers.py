from common.databaseConstants import *
from common.model import TransformerEncoderModel
from common.modelConstants import *
from common.utils import Vocab
import os
import torch

def loadVocab(vocabFolder, relations):
  vocabDict = {}
  for rel in relations:
    vocabDict[rel] = Vocab()
    vocabDict[rel].read_vocab_from_file(os.path.join(vocabFolder,rel+"_vocab_file_input.csv"))

  return vocabDict

def loadModels(modelFolder, relations, vocabDict):
  modelIdxDict = {}
  modelMainDict = {}
  for rel in relations:
    modelIdxDict[rel] = TransformerEncoderModel(
                          EMBEDDING_SIZE,
                          vocabDict[rel].n_words,
                          NHEAD,
                          HIDDEN_SIZE,
                          NUM_LAYERS,
                          DROPOUT,
                          ISizeDict[rel],
                          PAD_IDX,
                          device
                        ).to(device)
    modelIdxDict[rel].load_state_dict(torch.load(os.path.join(modelFolder, rel+"_idx")))

    modelMainDict[rel] = TransformerEncoderModel(
                          EMBEDDING_SIZE,
                          vocabDict[rel].n_words,
                          NHEAD,
                          HIDDEN_SIZE,
                          NUM_LAYERS,
                          DROPOUT,
                          RSizeDict[rel],
                          PAD_IDX,
                          device
                        ).to(device)
    modelMainDict[rel].load_state_dict(torch.load(os.path.join(modelFolder, rel+"_0")))

  return modelIdxDict, modelMainDict

