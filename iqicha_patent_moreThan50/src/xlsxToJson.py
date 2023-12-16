import json
import pandas as pd

# 读取xlsx文件
file_path = '../潍柴5000专利.xlsx'
df = pd.read_excel(file_path)

# 获取第一行数据作为key，其余数据作为value
keys = df.iloc[0]
values = df.iloc[0:]

entities = [] # {"type":"","name":"","props":{}}
relations = [] # {"head":"","tail":"", "type":""}
for index, row in values.iterrows():
   props = {"专利名称":row[1], "公布/公告号": row[2], "专利类型": row[3], "公布/公告日期": str(row[4])}
   entity = {"type":"专利", "name":row[2], "props":props}
   entities.append(entity)
   relations.append({"head":"潍柴动力股份有限公司", "tail":row[2], "type":"拥有专利"})

r = {"entities": entities, "relations": relations}
with open("../data/潍柴5000专利.json", "w", encoding="utf-8") as json_file:
   json.dump(r, json_file, ensure_ascii=False)
# print(r)

# from insertToGraph import initJson2Neo4j
#
# initJson2Neo4j(r)