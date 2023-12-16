from neo4j import GraphDatabase

# url = "bolt://192.168.1.104:32041"
url = "bolt://10.70.31.123:32041"
user_name = "neo4j"
password = "111111"

# url = "neo4j://localhost:7687"
# user_name = "neo4j"
# password = "fan"

def initJson2Neo4j(jsonData):
    driver = GraphDatabase.driver(url, auth=(user_name, password))
    for entity in jsonData["entities"]:
        query = "MATCH (n: "+ str(entity["type"]) +" {name: $name}) RETURN n"  # 把该实体添加到企业这张表
        with driver.session() as session:
            print("查询是否存在")

            result = session.run(query, name=entity["name"], type=entity["type"])
            print("查询结束")
            node_exists = result.single() is not None
        if node_exists:
            if "props" in entity.keys() and len(entity["props"])>0:
                # 构建属性更新的Cypher语句
                set_clauses = []
                for key, value in entity["props"].items():
                    s = str(value)
                    if s != '-' and len(s) != 0:  # 为空的话，不覆盖
                        key_without_splash = str(key).replace('/', "或")
                        set_clauses.append(f"n.{key_without_splash} = \"{s}\"")
                    # s = str(value).replace('\'', '')
                    # set_clauses.append(f"n.{str(key)} = '{s}'".replace('/', "或"))
                set_statement = ", ".join(set_clauses)
                # 执行属性更新
                update_query = f"MATCH (n:{entity['type']} {{name: $name}}) SET {set_statement} RETURN n"
                with driver.session() as session:
                    try:
                        print("开始")
                        session.run(update_query, name=entity["name"])
                        print(entity["name"], "更新")
                    except:
                        print(update_query, name=entity["name"])
        else:
            with driver.session() as session:
                query = f"CREATE (n:{entity['type']} $properties)"
                merged_dict = {**{"name":entity["name"]}, **entity["props"], **{"tag":"20231007"}}
                str_dict = {key: str(value) for key, value in merged_dict.items()}
                try:
                    result = session.run(query, properties=str_dict)
                    print(entity["name"], "创造")
                except:
                    print(query, properties=merged_dict)

    for relation in jsonData["relations"]:
        with driver.session() as session:
            set_clauses = []
            if "props" in relation.keys():
                relation["props"]["tag"] = "20231007"
                for key, value in relation["props"].items():
                    set_clauses.append(f"{str(key)} : '{value}'")
                    # print(f"{str(key)} : '{value}'")
                set_statement = ", ".join(set_clauses)
                # print(set_statement)
            else:
                set_statement = "tag:'20231007'"   # TODO: 改，不然会把20231007看成数字
            try:
                s = str(relation["type"]).replace('/', "或").replace('&', "或").replace('（','或').replace('）','')
                if s == '-' or s == '':
                    s = "未知"
                result = session.run(
                    "MATCH (head), (tail) "
                    "WHERE head.name = $head_name AND tail.name = $tail_name "
                    "MERGE (head)-[r:"+s+" {"+set_statement+"}]->(tail) "  # 改：create改为merge，避免重复创建关系
                    "RETURN r",
                    head_name=relation["head"],
                    tail_name=relation["tail"]
                )
                print(relation["head"], relation["tail"], "创造边")
            except:
                print(
                    "MATCH (head), (tail) "
                    "WHERE head.name = $head_name AND tail.name = $tail_name "
                    "CREATE (head)-[r:"+str(relation["type"])+" {"+set_statement+"}]->(tail) "
                    "RETURN r",
                    head_name=relation["head"],
                    tail_name=relation["tail"]
                )