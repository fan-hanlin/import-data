import json
import re
import pandas as pd

# 输入规范
# --csv类型：
#     BOM  注意的地方：分类号（12-16不要识别为12月16日，专利申请号不要识别为科学计数法）
# --列名依次为：
#              0   "专利名称": name,
#              1   "公布/公告号": publication_number,
#              2   "专利类型": patent_type,
#              3   "公布/公告日期": publication_date,
#
#              4   "专利申请号": application_number,
#              5   "申请日": application_date,
#              6   "主分类号": main_IPC_number,
#              7   "分案原申请号": original_application_number,#
#              8   "分类号": IPC_number,
#              9   "优先权": priority, #
#              10   "申请(专利权)人": applicant,
#              11   "地址": address,
#              12   "发明人": inventor,
#              13   "国际申请": international_application, #
#              14   "国际公布": international_publication, #
#              15   "进入国家阶段日期": state_stage_date, #
#              16   "专利代理机构": agency,
#              17   "代理人": agent,
#              18   "摘要": abstract,

df = pd.read_csv("./全部ANSI.csv", sep=",")
json_path = "./全部ANSI.json"
# json_path = "../data/全部2BOM.json"
df.rename(columns={'申请(专利权)人':'申请人或专利权人'}, inplace=True)
# print(df)
title = df.columns.values.tolist()
print(title)
entities = []
relations = []


for index, row in df.iterrows():
    if index > -1:
        # 公布号
        pid = row[1]
        # pid = row[7]

        # 申请人
        # if row[16] != "-":
        if row[10] != "-":
            # applicants = re.sub(r"【中文】|【EN】.*", "", row[16])  # 申请人可能为英文
            applicants = re.sub(r"【中文】|【EN】.*", "", row[10])  # 申请人可能为英文
            applicants = applicants.split(";")  # 申请人可能多个
            for applicant in applicants:
                entity = {"type": "企业", "name": applicant, "props": {}}
                entities.append(entity)
                relation = {"head": applicant, "tail": pid, "type": "拥有专利", "props": {}}
                relations.append(relation)
        # 专利代理机构和代理人
        # if row[0] != "-":
        if row[16] != "-":
            iname_icode = re.sub(r"【中文】|【EN】.*", "", row[16])  # 代理机构可能为英文
            # iname_icode = re.sub(r"【中文】|【EN】.*", "", row[0])  # 代理机构可能为英文
            pattern = r".*[0-9]{5}"
            if re.match(pattern, iname_icode) is not None:
                icode = iname_icode[-5:] # 得到机构代码
                iname = iname_icode[:-6] # 机构名称
                entity = {"type": "企业", "name": iname, "props": {"专利机构代码": icode}}
                entities.append(entity)
            else:
                iname = iname_icode  # 机构名称
                entity = {"type": "企业", "name": iname, "props": {"专利机构代码": "-"}}
                entities.append(entity)
            if row[17] != "-":
            # if row[5] != "-":
            #     agent_names = re.sub(r"【中文】|【EN】.*", "", row[5])  # 申请人可能为英文
                agent_names = re.sub(r"【中文】|【EN】.*", "", row[17])  # 申请人可能为英文
                agent_names = agent_names.split(";")  # 申请人可能多个
                for agent_name in agent_names:
                    entity = {"type": "人", "name": agent_name, "props": {}}
                    entities.append(entity)
                    relation = {"head": agent_name, "tail": iname, "type": "任职", "props": {}}
                    relations.append(relation)
                    relation = {"head": agent_name, "tail": pid, "type": "专利代理人", "props": {"代理机构": iname}}
                    relations.append(relation)
            relation = {"head": iname, "tail": pid, "type": "专利代理机构", "props": {"代理人": agent_name}}
            relations.append(relation)


        # 专利发明人
        if row[12] != "-":
        # if row[11] != "-":
            inventors = re.sub(r"【中文】|【EN】.*", "", row[12])  # 发明人可能为英文
            # inventors = re.sub(r"【中文】|【EN】.*", "", row[11])  # 发明人可能为英文
            inventors = inventors.split(";")  # 发明人可能多个
            for inventor in inventors:
                entity = {"type": "人", "name": inventor, "props": {}}
                entities.append(entity)
                relation = {"head": inventor, "tail": pid, "type": "专利发明人", "props": {}}
                relations.append(relation)
                if len(applicants) == 1:  # 只有一个申请公司，推测发明人就职于该公司
                    relation = {"head": inventor, "tail": applicants[0], "type": "任职", "props": {}}
                    relations.append(relation)

        props = dict()
        for i in range(19):
            chinese_only = re.sub(r"【中文】|【EN】.*", "", row[i])
            props.update({title[i]:chinese_only})
        entity = {"type": "专利", "name": pid, "props": props}
        entities.append(entity)
    elif index > 100000:
        break

r = {"entities": entities, "relations": relations}

with open(json_path, "w", encoding="utf-8") as json_file:
    json.dump(r, json_file, ensure_ascii=False)
print(r)
