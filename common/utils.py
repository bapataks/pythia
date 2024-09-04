import os

fileIdent = {"idx": "_I_", "0": "_R_0"}
nameIdent = {"idx": "index", "0": "base table, part 0"}

#relationDict = {"tmp018": ["CUAD", "CUDE", "DT", "IT", "CU"]}
relationDict = {"tmp018": ["DT"]}

# Class for vocabulary object
# Dictionaries from word to index, index to word and word frequency
class Vocab:
  def __init__(self):
    # As long as we are training models for a single template
    # We do not need SOS and EOS tokens, since all queries will be of same length
    # We still need a PAD token for transformer attention mechanism
    self.word2index = {"PAD": 0}
    self.index2word = {0: "PAD"}
    self.word2count = {"PAD": 0}
    self.n_words = 1

  # This is an inefficient code as it reads the entire file, but okay for prototyping.
  # It takes a list of input_files to create vocabulary, present in train_folder
  # An input file has rows of comma separated input tokens, no headers
  # If folder is True, the input_files is a folder, all files in this folder will be used
  def load_from_file(self, train_folder, input_files, folder=False):
    if folder:
      files = [os.path.join(train_folder, input_files, f) for f in os.listdir(os.path.join(train_folder, input_files))]
    else:
      files = [os.path.join(train_folder, f) for f in input_files]

    for file in files:
      with open(file) as f:
        lines = [line.rstrip() for line in f]

      for line in lines:
        words = line.split(",")
        for word in words:
          if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
          else:
            self.word2count[word] += 1

      # Set to None for GC
      words = None
      lines = None 

  # Load the vocab object from a given input_file
  def read_vocab_from_file(self, input_file):
    with open(input_file, "r") as f_input:
      lines = [line.rstrip() for line in f_input]
      lines = lines[1:]
      for line in lines:
        item = line.split(",")
        self.word2index[",".join(item[0:len(item) - 2])] = item[len(item) - 2]
        self.word2count[",".join(item[0:len(item) - 2])] = item[len(item) - 1]
        self.index2word[int(item[len(item) - 2])] = ",".join(item[0:len(item) - 2])
        self.n_words += 1

  # This outputs a csv file with three entries: word, index, frequency
  # with header
  # At <train_folder>/encoded_input/<relation_name>_vocab_file_input.csv
  def write_vocab_to_file(self, train_folder, relation_name):
    f_output = open(os.path.join(train_folder, "encoded_input", relation_name+"_vocab_file_input.csv"), "w")
    f_output.write("word,index,frequency\n")
    for index in range(self.n_words):
      word = self.index2word[index]
      f_output.write(f"{word},{index},{self.word2count[word]}\n")
    f_output.close()

  # Get token for a given index
  def getToken(self, index):
    return self.index2word[index]

def getPageSeqFromVocabIndex(seq, vocab_obj):
    pageSeq = [vocab_obj.index2word[idx] for idx in seq]
    return pageSeq

def getIdxSeqFromPages(seq, vocab_obj):
    idxSeq = [int(vocab_obj.word2index[word]) for word in seq]
    return idxSeq
