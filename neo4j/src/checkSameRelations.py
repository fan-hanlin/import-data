import re

from neo4j import GraphDatabase

url = "bolt://10.70.9.83:30562"
user_name = "neo4j"
password = "111111"

# url = "neo4j://localhost:7687"
# user_name = "neo4j"
# password = "fan"

def checkExample(driver):
    with driver.session() as session:
        # 查找所有节点
        query = "match (n:`专利`) where not n.name =~'[A-Z][A-Z].*' return n"
        rows = session.run(query)
        for r in rows.value():
            print(r._properties["name"])

def checkTagIsNum(driver):
    # 查找tag为数字的边

    del_ids = []  # 需要删除的边，即tag为int类型的边的id
    exist_ids = []  # 不删除的边，即tag为str类型的边的id
    with driver.session() as session:
        # 查找所有节点
        query = "MATCH (n)-[r:`拥有专利`]->(m) with n,r,m match p=(n)-[q:`拥有专利`]->(m) where q <> r return q"
        rows = session.run(query)

        for r in rows.value():
            if isinstance(r._properties["tag"], int):
                del_ids.append(r.id)
            else:
                exist_ids.append(r.id)

        print(len(del_ids), del_ids)
        print(len(exist_ids), exist_ids)

    return del_ids

def checkSameRelationship(driver):
    '''
    检查图谱中相同边
    :return: 重复边（可直接删除）, 报告
    '''

    log = []
    del_ids = [] # 需要删除的边的id
    with driver.session() as session:
        # 查找所有节点
        query = "MATCH (n) RETURN id(n)"
        nids = session.run(query)
        for nid in nids.value():
            print("当前头结点：", nid)
            # 遍历所有结点
            query2 = f"MATCH (n)-[r]->(m) WHERE id(n) = {nid} RETURN r" # 查询以该结点出发的所有边
            relations = session.run(query2)
            relations = relations.value()
            rlist = []
            for r in relations:
                # 遍历以该节点出发的边
                mid = r.end_node.id  # 尾结点id
                rtype = r.type  # 边id
                rprops = r._properties  # 边属性

                rstring = str(mid)+rtype+str(rprops)  #把三者连成一个string，表示一条边

                if rstring in rlist:  # 重复边
                    log.append("重复边：<start node id: nid, end node id: mid, relationship id: r.id")
                    # print("del:", r.id, rstring)
                    del_ids.append(r.id)
                else:
                    # print("add:", rstring)
                    rlist.append(rstring)

    return del_ids, log

def checkIncorrectPID(driver):
    '''
    检测图谱中不正确的专利公告号
    :param driver:
    :return: log
    '''
    log = []
    query = "MATCH (n:`专利`) RETURN n.name"
    with driver.session() as session:
        pids = session.run(query)
        for pid in pids.value():
            # 国别号+分类号+流水号+标识代码
            isRight = True
            if pid[:1] == "CN":
                isRight = False

            pid_2 = pid[2]
            if re.match(r"[1-3]", pid_2) is None:
                isRight = False

            pid__1 = pid[-1]
            if re.match(r"[A-C]|[U-Y]|[S]", pid__1) is None:
                isRight = False

            if not isRight:
                print(f"专利公告号不正确 位置(id)：{pid}")
                log.append(f"专利公告号不正确 位置(id)：{pid}")


def checkIncorrectPtype(driver):
    '''
    检测图谱中不正确的专利类型
    :param driver:
    :return:log
    '''
    log = []
    query = "MATCH (n:`专利`) RETURN n"
    with driver.session() as session:
        patents = session.run(query)
        for patent in patents.value():
            pid = patent._properties["name"] # 国别号+分类号+流水号+标识代码
            ptype = patent._properties["专利类型"]
            if patent._properties.has_key("专利申请号"):
                print("不含")
            # papply = patent._properties["专利申请号"] # 年份+分类号+流水号（5位）+标识代码
            # p
            isRight = True

            pid_2 = pid[2]
            if pid_2 == 1 and ptype != "发明专利": # 发明专利申请
                log.append(f"专利类型不正确 位置(id)：{pid} 修改建议：'专利类型修改为：发明专利'")
                isRight = False

            elif pid_2 == 2 and ptype != "实用新型": # 实用新型专利申请
                log.append(f"专利类型不正确 位置(id)：{pid} 修改建议：'专利类型修改为：实用新型'")
                isRight = False

            elif pid_2 == 3 and ptype != "外观设计": # 外观设计专利申请
                log.append(f"专利类型不正确 位置(id)：{pid} 修改建议：'专利类型修改为：外观设计'")
                isRight = False

            # TODO：最后一个字母的含义

            # TODO：2003年10月1日以后的专利采用十二位编号；2003年10月1日以前的专利采用八位编号

            # TODO：专利申请号

def deleteRelationship(del_ids, driver):
    '''
    在图谱中删除边
    :param del_ids:
    :return: None
    '''
    # print("删除边：", del_ids)
    # 删除边

    for del_id in del_ids:
        query = f"MATCH (n)-[r]->(m) WHERE id(r) = {del_id} delete r"
        with driver.session() as session:
            result = session.run(query)  # 谨慎删除
            print(result)

def entityAlighment(driver):
    with driver.session() as session:
        # 查找所有节点
        query = "MATCH (n) RETURN n limit 5"  # TODO 要查的结点
        result = session.run(query)
        for row in result.value():
            props = row._properties
            print(len(props), props)

            name = row._properties["name"]

            statements = []
            for key in props.keys():
                statements.append(f"{key}是'props'")
            description = f"{name}"


driver = GraphDatabase.driver(url, auth=(user_name, password))
del_ids = checkTagIsNum(driver)
# del_ids, log = checkSameRelationship(driver)
print(len(del_ids), del_ids)
deleteRelationship(del_ids, driver)
# print(log)
# checkIncorrectPID(driver)
# checkIncorrectPtype(driver)
# checkExample(driver)

# entityAlighment(driver)
