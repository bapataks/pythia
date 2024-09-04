import torch
from torch.utils.data import Dataset

def pad_tensor(vec, pad, dim):
  """
  args:
    vec - tensor to pad
    pad - the size to pad to
    dim - dimension to pad

  return:
    a new tensor padded to 'pad' in dimension 'dim'
  """
  pad_size = list(vec.shape)
  pad_size[dim] = pad - vec.size(dim)
  return torch.cat([vec, torch.zeros(*pad_size).long()], dim=dim)

# Class to add padding to training batches
# We do not need one as all training queries are from the same template
# So they have the same number of input tokens
class PadCollate:
  """
  a variant of callate_fn that pads according to the longest sequence in
  a batch of sequences
  """

  def __init__(self, dim=0):
    """
    args:
      dim - the dimension to be padded (dimension of time in sequences)
    """
    self.dim = dim

  def pad_collate(self, batch):
    """
    args:
      batch - list of (tensor, label)

    return:
      xs - a tensor of all examples in 'batch' after padding
      ys - a LongTensor of all labels in batch
    """
    # find longest sequence
    max_len_x = max(map(lambda x: x[0].shape[self.dim], batch))
    max_len_y = max(map(lambda x: x[1].shape[self.dim], batch))
    # pad according to max_len
    batch = list(map(lambda x:
              (pad_tensor(x[0], pad=max_len_x, dim=self.dim), pad_tensor(x[1], pad=max_len_y, dim=self.dim)), batch))
    # stack all
    xs = torch.stack(list(map(lambda x: x[0], batch)), dim=0)
    ys = torch.stack(list(map(lambda x: x[1], batch)), dim=0)
    return torch.LongTensor(xs), torch.LongTensor(ys)

  def __call__(self, batch):
    return self.pad_collate(batch)

# Custom dataset class to load all training data
class CustomDataset(Dataset):
  def __init__(self, context_file_name, prediction_file_name):
    self.context_data, self.prediction_data = [], []
    with open(context_file_name) as f:
      self.context_data = [[int(index) for index in line.strip().split(",")] for line in f ]
    with open(prediction_file_name) as f:
      self.prediction_data = [[int(index) for index in line.strip().split(",")] for line in f ]

  def __len__(self):
    return len(self.context_data)

  def __getitem__(self, index):
    return torch.LongTensor(self.context_data[index]), torch.LongTensor(self.prediction_data[index])
