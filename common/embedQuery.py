import os

def getEmbed(tmp_folder, file):
  if "tmp018" in tmp_folder:
    return getEmbed_tmp018(tmp_folder, file)

  elif "tmp019" in tmp_folder:
    return getEmbed_tmp019(tmp_folder, file)

  elif "tmp091" in tmp_folder:
    return getEmbed_tmp091(tmp_folder, file)

  elif "imdb" in tmp_folder:
    return getEmbed_imdb(tmp_folder, file)

  else:
    print("Template not present")
    exit(1)

def getEmbed_tmp018(tmp_folder, file):
  qEmbed = []
  seq = ""

  with open(os.path.join(tmp_folder, "EAplans", file), "r") as f:
    lines = [line.rstrip().lstrip() for line in f]
  plan = list(filter(lambda x: "Nested Loop" in x or "Hash Join" in x or "Merge Join" in x or "Scan" in x, lines))

  with open(os.path.join(tmp_folder, "queries", file), "r") as f:
    lines = [line.rstrip().lstrip() for line in f]

  ss = "Seq Scan"
  ids = "Index Scan"
  for i in plan:
    if "Nested Loop" in i:
      seq += "N:"
    elif "Hash Join" in i:
      seq += "H:"
    elif "Merge Join" in i:
      seq += "M:"
    elif ids in i and "date_dim" in i:
      seq += "33357:"
    elif ss in i and "date_dim" in i:
      seq += "33356:"
    elif ids in i and "catalog_sales" in i:
      seq += "33346:"
    elif ss in i and "catalog_sales" in i:
      seq += "33345:"
    elif ss in i and "call_center" in i:
      seq += "33336:"
    elif ss in i and "ship_mode" in i:
      seq += "33377:"
    elif ss in i and "warehouse" in i:
      seq += "33398:"
    elif ids in i and "item" in i:
      seq += "33371:"
    elif ss in i and "item" in i:
      seq += "33369:"
    elif ids in i and "catalog_returns" in i:
      seq += "33344:"
    elif ss in i and "catalog_returns" in i:
      seq += "33343:"
    elif ids in i and "customer_demographics" in i:
      seq += "33355:"
    elif ss in i and "customer_demographics" in i:
      seq += "33354:"
    elif ids in i and "household_demographics" in i:
      seq += "33364:"
    elif ss in i and "household_demographics" in i:
      seq += "33363:"
    elif ids in i and "inventory" in i:
      seq += "33368:"
    elif ss in i and "inventory" in i:
      seq += "33367:"
    elif ss in i and "promotion" in i:
      seq += "33373:"
    elif ids in i and "customer_address" in i:
      seq += "33348:"
    elif ss in i and "customer_address" in i:
      seq += "33347:"
    elif ids in i and "customer" in i:
      seq += "33350:"
    elif ss in i and "store_sales" in i:
      seq += "33394:"
    elif ids in i and "store" in i:
      seq += "33381:"
    elif ss in i and "store" in i:
      seq += "33379:"
    elif "Bitmap Heap Scan" in i:
      seq += ""

  seq = seq.split(':')
  seq = seq[:len(seq)-1]
  tabSeq = ["", "", "", "", "", ""]
  firstIdx = 0
  lastIdx = len(tabSeq) - 1
  lastPlanIdx = len(seq) - 1
  planIdx = 0
  prevJO = ""

  while planIdx <= lastPlanIdx:
    if "N" in seq[planIdx]:
      tabSeq[lastIdx] = seq[lastPlanIdx] + ":NLJ"
      lastIdx -= 1
      lastPlanIdx -= 1
      prevJO = ":NLJ"
    elif "H" in seq[planIdx]:
      tabSeq[firstIdx] = seq[lastPlanIdx] + ":HJ"
      firstIdx += 1
      lastPlanIdx -= 1
      prevJO = ":HJ"
    else:
      tabSeq[firstIdx] = seq[lastPlanIdx] + prevJO

    planIdx += 1

  for node in plan:
    if "Nested Loop" in node:
      qEmbed.append("NLJ")

    elif "Hash Join" in node:
      qEmbed.append("HJ")

    elif "store_sales" in node:
      qEmbed += ["RELN_SEQ", "STSL", "PRED", "COST"]
      val = int(list(filter(lambda x: "ss_wholesale_cost" in x, lines))[0].split('BETWEEN ')[1].split(' AND')[0])
      qEmbed += list(map(str, list(range(val, val+21))))

    elif "store" in node:
      if "Index" in node:
        qEmbed += ["RELN_IDX", "ST"]
      else:
        qEmbed += ["RELN_SEQ", "ST"]

    elif "catalog_sales" in node:
      qEmbed += ["RELN_SEQ", "CTSL", "PRED", "COST"]
      val = int(list(filter(lambda x: "cs_wholesale_cost" in x, lines))[0].split('BETWEEN ')[1].split(' AND')[0])
      qEmbed += list(map(str, list(range(val, val+6))))

    elif "item" in node:
      if "Index" in node:
        qEmbed += ["RELN_IDX", "IT", "PRED", "CATEGORY"]
      else:
        qEmbed += ["RELN_SEQ", "IT", "PRED", "CATEGORY"]
      qEmbed.append(list(filter(lambda x: "i_category" in x, lines))[0].split('\'')[1])

    elif "customer_address" in node:
      if "Index" in node:
        qEmbed.append("RELN_IDX")
      else:
        qEmbed.append("RELN_SEQ")
      qEmbed += ["CUAD", "PRED", "STATE"]
      qEmbed.append(list(filter(lambda x: "ca_state" in x, lines))[1].split('\'')[1])
      qEmbed.append(list(filter(lambda x: "ca_state" in x, lines))[1].split('\'')[3])
      qEmbed.append(list(filter(lambda x: "ca_state" in x, lines))[1].split('\'')[5])

    elif "customer_demographics" in node:
      if "Index" in node:
        qEmbed.append("RELN_IDX")
      else:
        qEmbed.append("RELN_SEQ")
      qEmbed += ["CUDE", "PRED", "GENDER"]
      qEmbed.append(list(filter(lambda x: "cd_gender" in x, lines))[0].split('\'')[1])
      qEmbed += ["PRED", "ES"]
      qEmbed.append(list(filter(lambda x: "cd_education_status" in x, lines))[0].split('\'')[1])

    elif "customer" in node:
      qEmbed += ["RELN_IDX", "CU", "PRED", "MONTH"]
      qEmbed.append(list(filter(lambda x: "c_birth_month" in x, lines))[0].split('= ')[1].split(' and')[0])

    elif "date_dim" in node:
      if "Index" in node:
        qEmbed += ["RELN_IDX", "DT", "PRED", "YEAR"]
      else:
        qEmbed += ["RELN_SEQ", "DT", "PRED", "YEAR"]
      qEmbed.append(list(filter(lambda x: "d_year" in x, lines))[0].split('= ')[1].split(' and')[0])

  return qEmbed, tabSeq

def getEmbed_tmp019(tmp_folder, file):
  qEmbed = []
  seq = ""

  with open(os.path.join(tmp_folder, "EAplans", file), "r") as f:
    lines = [line.rstrip().lstrip() for line in f]
  plan = list(filter(lambda x: "Nested Loop" in x or "Hash Join" in x or "Merge Join" in x or "Scan" in x, lines))

  with open(os.path.join(tmp_folder, "queries", file), "r") as f:
    lines = [line.rstrip().lstrip() for line in f]

  ss = "Seq Scan"
  ids = "Index Scan"
  for i in plan:
    if "Nested Loop" in i:
      seq += "N:"
    elif "Hash Join" in i:
      seq += "H:"
    elif "Merge Join" in i:
      seq += "M:"
    elif ids in i and "date_dim" in i:
      seq += "33357:"
    elif ss in i and "date_dim" in i:
      seq += "33356:"
    elif ids in i and "catalog_sales" in i:
      seq += "33346:"
    elif ss in i and "catalog_sales" in i:
      seq += "33345:"
    elif ss in i and "call_center" in i:
      seq += "33336:"
    elif ss in i and "ship_mode" in i:
      seq += "33377:"
    elif ss in i and "warehouse" in i:
      seq += "33398:"
    elif ids in i and "item" in i:
      seq += "33371:"
    elif ss in i and "item" in i:
      seq += "33369:"
    elif ids in i and "catalog_returns" in i:
      seq += "33344:"
    elif ss in i and "catalog_returns" in i:
      seq += "33343:"
    elif ids in i and "customer_demographics" in i:
      seq += "33355:"
    elif ss in i and "customer_demographics" in i:
      seq += "33354:"
    elif ids in i and "household_demographics" in i:
      seq += "33364:"
    elif ss in i and "household_demographics" in i:
      seq += "33363:"
    elif ids in i and "inventory" in i:
      seq += "33368:"
    elif ss in i and "inventory" in i:
      seq += "33367:"
    elif ss in i and "promotion" in i:
      seq += "33373:"
    elif ids in i and "customer_address" in i:
      seq += "33348:"
    elif ss in i and "customer_address" in i:
      seq += "33347:"
    elif ids in i and "customer" in i:
      seq += "33350:"
    elif ss in i and "store_sales" in i:
      seq += "33394:"
    elif ids in i and "store" in i:
      seq += "33381:"
    elif ss in i and "store" in i:
      seq += "33379:"
    elif "Bitmap Heap Scan" in i:
      seq += ""

  seq = seq.split(':')
  seq = seq[:len(seq)-1]
  tabSeq = ["", "", "", "", "", ""]
  firstIdx = 0
  lastIdx = len(tabSeq) - 1
  lastPlanIdx = len(seq) - 1
  planIdx = 0
  prevJO = ""

  while planIdx <= lastPlanIdx:
    if "N" in seq[planIdx]:
      tabSeq[lastIdx] = seq[lastPlanIdx] + ":NLJ"
      lastIdx -= 1
      lastPlanIdx -= 1
      prevJO = ":NLJ"
    elif "H" in seq[planIdx]:
      tabSeq[firstIdx] = seq[lastPlanIdx] + ":HJ"
      firstIdx += 1
      lastPlanIdx -= 1
      prevJO = ":HJ"
    else:
      tabSeq[firstIdx] = seq[lastPlanIdx] + prevJO

    planIdx += 1

  for node in plan:
    if "Nested Loop" in node:
      qEmbed.append("NLJ")

    elif "Hash Join" in node:
      qEmbed.append("HJ")

    elif "store_sales" in node:
      qEmbed += ["RELN_SEQ", "STSL", "PRED", "COST"]
      val = int(list(filter(lambda x: "ss_wholesale_cost" in x, lines))[0].split('BETWEEN ')[1].split(' AND')[0])
      qEmbed += list(map(str, list(range(val, val+21))))

    elif "store" in node:
      if "Index" in node:
        qEmbed += ["RELN_IDX", "ST"]
      else:
        qEmbed += ["RELN_SEQ", "ST"]

    elif "item" in node:
      if "Index" in node:
        qEmbed += ["RELN_IDX", "IT", "PRED", "CATEGORY"]
      else:
        qEmbed += ["RELN_SEQ", "IT", "PRED", "CATEGORY"]
      qEmbed.append(list(filter(lambda x: "i_category" in x, lines))[0].split('\'')[1])

    elif "customer_address" in node:
      qEmbed += ["RELN_IDX", "CUAD", "PRED", "STATE"]
      qEmbed.append(list(filter(lambda x: "ca_state" in x, lines))[0].split('\'')[1])

    elif "customer" in node:
      qEmbed += ["RELN_IDX", "CU", "PRED", "MONTH"]
      qEmbed.append(list(filter(lambda x: "c_birth_month" in x, lines))[0].split('= ')[1])

    elif "date_dim" in node:
      if "Index" in node:
        qEmbed += ["RELN_IDX", "DT", "PRED", "YEAR"]
      else:
        qEmbed += ["RELN_SEQ", "DT", "PRED", "YEAR"]
      qEmbed.append(list(filter(lambda x: "d_year" in x, lines))[0].split('=')[1])
      qEmbed += ["PRED", "MONTH"]
      qEmbed.append(list(filter(lambda x: "d_moy" in x, lines))[0].split('= ')[1])

  return qEmbed, tabSeq

def getEmbed_tmp091(tmp_folder, file):
  qEmbed = []
  seq = ""

  with open(os.path.join(tmp_folder, "EAplans", file), "r") as f:
    lines = [line.rstrip().lstrip() for line in f]
  plan = list(filter(lambda x: "Nested Loop" in x or "Hash Join" in x or "Merge Join" in x or "Scan" in x, lines))

  with open(os.path.join(tmp_folder, "queries", file), "r") as f:
    lines = [line.rstrip().lstrip() for line in f]

  ss = "Seq Scan"
  ids = "Index Scan"
  for i in plan:
    if "Nested Loop" in i:
      seq += "N:"
    elif "Hash Join" in i:
      seq += "H:"
    elif "Merge Join" in i:
      seq += "M:"
    elif ids in i and "date_dim" in i:
      seq += "33357:"
    elif ss in i and "date_dim" in i:
      seq += "33356:"
    elif ids in i and "catalog_sales" in i:
      seq += "33346:"
    elif ss in i and "catalog_sales" in i:
      seq += "33345:"
    elif ss in i and "call_center" in i:
      seq += "33336:"
    elif ids in i and "call_center" in i:
      seq += "33338:"
    elif ss in i and "ship_mode" in i:
      seq += "33377:"
    elif ss in i and "warehouse" in i:
      seq += "33398:"
    elif ids in i and "item" in i:
      seq += "33371:"
    elif ss in i and "item" in i:
      seq += "33369:"
    elif ids in i and "catalog_returns" in i:
      seq += "33344:"
    elif ss in i and "catalog_returns" in i:
      seq += "33343:"
    elif ids in i and "customer_demographics" in i:
      seq += "33355:"
    elif ss in i and "customer_demographics" in i:
      seq += "33354:"
    elif ids in i and "household_demographics" in i:
      seq += "33364:"
    elif ss in i and "household_demographics" in i:
      seq += "33363:"
    elif ids in i and "inventory" in i:
      seq += "33368:"
    elif ss in i and "inventory" in i:
      seq += "33367:"
    elif ss in i and "promotion" in i:
      seq += "33373:"
    elif ids in i and "customer_address" in i:
      seq += "33348:"
    elif ss in i and "customer_address" in i:
      seq += "33347:"
    elif ids in i and "customer" in i:
      seq += "33350:"
    elif ss in i and "store_sales" in i:
      seq += "33394:"
    elif ids in i and "store" in i:
      seq += "33381:"
    elif ss in i and "store" in i:
      seq += "33379:"
    elif "Bitmap Heap Scan" in i:
      seq += ""

  seq = seq.split(':')
  seq = seq[:len(seq)-1]
  tabSeq = ["", "", "", "", "", "", ""]
  firstIdx = 0
  lastIdx = len(tabSeq) - 1
  lastPlanIdx = len(seq) - 1
  planIdx = 0
  prevJO = ""

  while planIdx <= lastPlanIdx:
    if "N" in seq[planIdx]:
      tabSeq[lastIdx] = seq[lastPlanIdx] + ":NLJ"
      lastIdx -= 1
      lastPlanIdx -= 1
      prevJO = ":NLJ"
    elif "H" in seq[planIdx]:
      tabSeq[firstIdx] = seq[lastPlanIdx] + ":HJ"
      firstIdx += 1
      lastPlanIdx -= 1
      prevJO = ":HJ"
    else:
      tabSeq[firstIdx] = seq[lastPlanIdx] + prevJO

    planIdx += 1

  for node in plan:
    if "Nested Loop" in node:
      qEmbed.append("NLJ")

    elif "Hash Join" in node:
      qEmbed.append("HJ")

    elif "store_sales" in node:
      qEmbed += ["RELN_SEQ", "STSL"]

    elif "store" in node:
      if "Index" in node:
        qEmbed += ["RELN_IDX", "ST"]
      else:
        qEmbed += ["RELN_SEQ", "ST"]

    elif "catalog_sales" in node:
      qEmbed += ["RELN_SEQ", "CTSL", "PRED", "COST"]
      val = int(list(filter(lambda x: "cs_wholesale_cost" in x, lines))[0].split('BETWEEN ')[1].split(' AND')[0])
      qEmbed += list(map(str, list(range(val, val+6))))

    elif "item" in node:
      if "Index" in node:
        qEmbed += ["RELN_IDX", "IT", "PRED", "CATEGORY"]
        idxItem = True
      else:
        qEmbed += ["RELN_SEQ", "IT", "PRED", "CATEGORY"]
      qEmbed.append(list(filter(lambda x: "i_category" in x, lines))[0].split('\'')[1])

    elif "customer_address" in node:
      if "Index" in node:
        qEmbed.append("RELN_IDX")
      else:
        qEmbed.append("RELN_SEQ")
      qEmbed += ["CUAD", "PRED", "GMT_OFFSET"]
      qEmbed.append(list(filter(lambda x: "ca_gmt_offset" in x, lines))[0].split('= ')[1])

    elif "customer_demographics" in node:
      qEmbed += ["RELN_IDX", "CUDE"]

    elif "household_demographics" in node:
      qEmbed += ["RELN_IDX", "HDE", "PRED", "BUY_POT"]
      qEmbed.append(list(filter(lambda x: "hd_buy_potential" in x, lines))[0].split('\'')[1])

    elif "customer" in node:
      qEmbed += ["RELN_IDX", "CU"]

    elif "date_dim" in node:
      if "Index" in node:
        qEmbed += ["RELN_IDX", "DT"]
      else:
        qEmbed += ["RELN_SEQ", "DT", "PRED", "YEAR"]
      qEmbed.append(list(filter(lambda x: "d_year" in x, lines))[0].split('= ')[1])
      qEmbed += ["PRED", "MONTH"]
      qEmbed.append(list(filter(lambda x: "d_moy" in x, lines))[0].split('= ')[1])

    elif "catalog_returns" in node:
      qEmbed += ["RELN_SEQ", "CTRT"]

    elif "call_center" in node:
      if "Index" in node:
        qEmbed.append("RELN_IDX")
      else:
        qEmbed.append("RELN_SEQ")
      qEmbed.append("CC")

  return qEmbed, tabSeq

def getEmbed_imdb(tmp_folder, file):
  qEmbed = []

  with open(os.path.join(tmp_folder, "EAplans", file), "r") as f:
    lines = [line.rstrip().lstrip() for line in f]
  plan = list(filter(lambda x: "Nested Loop" in x or "Hash Join" in x or "Merge Join" in x or "Scan" in x, lines))

  prevText = ""
  for i in range(len(plan)):
    plan[i] += prevText
    prevText = ""

    if "Bitmap Heap Scan" in plan[i]:
      if "mi1" in plan[i]:
        prevText = "mi1"
      else:
        prevText = "mi2"
  plan = list(filter(lambda x: "Bitmap Heap Scan" not in x, plan))

  with open(os.path.join(tmp_folder, "queries", file), "r") as f:
    lines = [line.rstrip().lstrip() for line in f]

  for node in plan:
    if "Nested Loop" in node:
      qEmbed.append("NLJ")

    elif "Hash Join" in node:
      qEmbed.append("HJ")

    elif "Merge Join" in node:
      qEmbed.append("MJ")

    elif "title" in node:
      if "title_pkey" in node:
        qEmbed += ["RELN_IDX", "TTL_PK"]
      elif "kind_id_title" in node:
        qEmbed += ["RELN_IDX", "TTL_KI"]
      else:
        qEmbed += ["RELN_SEQ", "TTL"]
      qEmbed += ["PRED", "YEAR"]
      qEmbed.append(list(filter(lambda x: "production_year" in x, lines))[0].split("<= ")[1])
      qEmbed.append(list(filter(lambda x: "production_year" in x, lines))[1].split(" <")[0].split("AND ")[1])

    elif "kind_type" in node:
      if "kind_type_pkey" in node:
        qEmbed += ["RELN_IDX", "KT"]
      else:
        qEmbed += ["RELN_SEQ", "KT"]
      qEmbed += list(filter(lambda x: "kind" in x, lines))[2].split('(')[1].split(')')[0].split(',')

    elif "mi1" in node:
      if "movie_id_movie_info" in node:
        qEmbed += ["RELN_IDX", "MI_MI"]
      else:
        qEmbed += ["RELN_IDX", "MI_IT"]
      qEmbed += list(filter(lambda x: "mi1.info" in x, lines))[1].split('(')[1].split(')')[0].split(',')

    elif "mi2" in node:
      if "movie_id_movie_info" in node:
        qEmbed += ["RELN_IDX", "MI_MI"]
      else:
        qEmbed += ["RELN_IDX", "MI_IT"]
      qEmbed += list(filter(lambda x: "mi2.info" in x, lines))[1].split('(')[1].split(')')[0].split(',')

    elif "it1" in node or "it2" in node:
      qEmbed += ["RELN_SEQ", "IT"]

    elif "cast_info" in node:
      if "movie_id_cast_info" in node:
        qEmbed += ["RELN_IDX", "CI_MI"]
      else:
        qEmbed += ["RELN_IDX", "CI_RI"]

    elif "role_type" in node:
      qEmbed += ["RELN_SEQ", "RT"]
      qEmbed += list(filter(lambda x: "rt.role" in x, lines))[0].split('(')[1].split(')')[0].split(',')

    elif "name" in node:
      qEmbed += ["RELN_IDX", "NM"]
      qEmbed += list(filter(lambda x: "n.gender" in x, lines))[0].split('(')[1].split(')')[0].split(',')

  return qEmbed
