from insertToGraph import initJson2Neo4j
from deleteNode import deleteNode
import json
import os

'''
    预处理：
    在json下放置要导入的json文件
'''

for filename in os.listdir("../json"):

    with open(f'../json/{filename}', 'r', encoding='utf-8') as file:
        data = json.load(file)

    print(filename)
    initJson2Neo4j(data)