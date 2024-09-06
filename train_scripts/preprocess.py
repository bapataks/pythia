import os
import sys
from common.utils import Vocab

# This function takes a Vocab class object
# And encodes given input_files using this vocabulary
# input_files is a list of files that are to be encoded, present in train_folder
# An input file has rows of comma separated input tokens, no headers
# If folder is True, the input_files is a folder, all files in this folder will be encoded
# The output files are placed in <train_folder>/encoded_input/
# with the same file name as input_files
def convert_words_to_index(vocab_obj, train_folder, input_files, folder=False):
  if folder:
    rw_files = [(os.path.join(train_folder, input_files, f), os.path.join(train_folder, "encoded_input", f)) for f in os.listdir(os.path.join(train_folder, input_files))]
  else:
    rw_files = [(os.path.join(train_folder, f), os.path.join(train_folder, "encoded_input", f)) for f in input_files]

  for (inp_file, out_file) in rw_files:
    f_input = open(inp_file, "r")
    f_output = open(out_file, "w")

    for line in f_input:
      # we split each line using comma, convert the word to index, 
      # and since we are outputting to a file convert to string
      # and then join it using string.join
      words = line.strip().split(",")
      output = []
      for word in words:
        output.append(str(vocab_obj.word2index[word]))

      f_output.write(",".join(output) + "\n")

    f_input.close()
    f_output.close()

if __name__ == "__main__":
  if len(sys.argv) != 4:
    print("Usage: python train_scripts/preprocess.py <dataset> <template> <relation>")
    exit(1)

  train_folder = os.path.join("dataset", sys.argv[1], sys.argv[2], "train_test_files")
  print("Creating vocab for input to model: {} - {}".format(train_folder, sys.argv[3]))

  # check if template workload exists
  if not os.path.exists(train_folder):
    print("Incorrect path for training files")
    exit(2)

  # handle IMDB dataset separately
  if sys.argv[1] == "imdb":
    input_files = [sys.argv[3]+"MLtrain_input.csv", sys.argv[3]+"MLtest_input.csv"]
  else:
    input_files = [sys.argv[3]+"_MLtrain_input.csv", sys.argv[3]+"_MLtest_input.csv"]

  # check if the files to be encoded exist
  for inpFile in input_files:
    if not os.path.exists(os.path.join(train_folder, inpFile)):
      print("Train/Test file does not exist")
      exit(3)

  # check if the output directory exists
  if not os.path.exists(os.path.join(train_folder, "encoded_input")):
    print("\"encoded_input\" directory not present")
    exit(4)

  print("Creating Vocab...")

  # Create vocabulary file
  vocab_obj = Vocab()
  vocab_obj.load_from_file(train_folder, input_files)
  vocab_obj.write_vocab_to_file(train_folder, sys.argv[3])

  print("Encoding input files...")

  # Encode input files
  convert_words_to_index(vocab_obj, train_folder, input_files)

