import torch

# Hard coding model hyperparameters
EMBEDDING_SIZE = 100
NUM_LAYERS = 2
HIDDEN_SIZE = 800
DROPOUT = 0.0 #No dropout
NHEAD = 10
PAD_IDX = 0

BATCH_SIZE = 200

STOP_LOSS_DELTA = 0.005
STOP_LOSS_COUNT = 3
MAX_EPOCH = 35

#device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
device = torch.device('cpu' if torch.cuda.is_available() else 'cpu')
