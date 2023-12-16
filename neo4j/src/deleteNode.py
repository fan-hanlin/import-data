from neo4j import GraphDatabase

url = "bolt://10.70.7.186:30562"
user_name = "neo4j"
password = "111111"

# url = "neo4j://localhost:7687"
# user_name = "neo4j"
# password = "fan"

def deleteNode(jsonData):
    driver = GraphDatabase.driver(url, auth=(user_name, password))
    for entity in jsonData["entities"]:
        query = "MATCH (n: "+ str(entity["type"]) +" {name: $name}) RETURN n"  # 把该实体添加到企业这张表
        with driver.session() as session:
            result = session.run(query, name=entity["name"], type=entity["type"])
            node_exists = result.single() is not None
        if node_exists:
            match_query = f"MATCH p = (n)-[]->() where n.name = \"{entity['name']}\" return count(p)"
            m = 0
            with driver.session() as session:
                try:
                    result = session.run(match_query)
                    m = result.value()[0]
                    print(entity["name"], m)
                except:
                    print(match_query)

            if m == 0:
                delete_query = f"MATCH (n:{entity['type']} {{name: $name}}) delete n"
                print(delete_query)
                with driver.session() as session:
                    try:
                        session.run(delete_query, name=entity["name"])
                        print("delete:", entity["name"])
                    except:
                        print(delete_query, name=entity["name"])