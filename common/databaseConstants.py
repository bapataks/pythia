import os

# Relation Filenode of Postgres
baseT = {}
baseT["CU"] = "33349_"
baseT["CUAD"] = "33347_"
baseT["DT"] = "33356_"
baseT["IT"] = "33369_"
baseT["ST"] = "33379_"
baseT["CUDE"] = "33354_"
idxT = {}
idxT["CU"] = "33350_"
idxT["CUAD"] = "33348_"
idxT["DT"] = "33357_"
idxT["IT"] = "33371_"
idxT["ST"] = "33381_"
idxT["CUDE"] = "33355_"

# Inverse Filenode dictionary
invFilenode = {}
invFilenode["33350"] = "CU"
invFilenode["33348"] = "CUAD"
invFilenode["33357"] = "DT"
invFilenode["33371"] = "IT"
invFilenode["33381"] = "ST"
invFilenode["33355"] = "CUDE"

# Number of index pages
ISizeDict = {}
ISizeDict["CU"] = 5486
ISizeDict["CUAD"] = 2745
ISizeDict["DT"] = 202
ISizeDict["IT"] = 562
ISizeDict["ST"] = 2
ISizeDict["CUDE"] = 5268

# Number of base table pages
RSizeDict = {}
RSizeDict["CU"] = 55448
RSizeDict["CUAD"] = 22538
RSizeDict["DT"] = 1474
RSizeDict["IT"] = 14356
RSizeDict["ST"] = 18
RSizeDict["CUDE"] = 22413

# IMDB
sizeIMDB = 252885
baseT["182054"] = "182054_"
