import os
from lxml import etree


def Wangli_HtmlToJson(html):
    '''
    处理王力车详情页
    :param html: , etree.HTMLParser()类型
    '''
    props = dict()
    table_dict = dict()
    entities = []
    relations = []

    h1 = html.xpath("//h1/text()")[0]

    tables = html.xpath("//div[@class='cbox']//table")
    theads = html.xpath("//div[@class='cbox-t']//text()")
    theads2 = html.xpath("//div[@class='cbox-t margin']//text()")
    theads.extend(theads2)
    for i, table in enumerate(tables):
        if i < len(theads):
            thead = theads[i]
        else:
            thead = "else"
        trs = table.xpath(".//tr")
        if thead == "发动机参数":
            props["发动机型号"] = trs[1].xpath(".//td//text()")[0]
            props["发动机生产企业"] = trs[1].xpath(".//td//text()")[1]
            props["发动机排量"] = trs[1].xpath(".//td//text()")[2]
            props["发动机功率"] = trs[1].xpath(".//td//text()")[3]
        elif thead == "主要技术参数" or thead == "车辆燃料参数":
            for tr in trs:
                tds = tr.xpath(".//td")
                if len(tds) == 4:
                    t1 = tds[0].xpath(".//text()")
                    t1 = t1[0].replace("/", "或").replace("：", "")
                    t2 = tds[1].xpath(".//text()")
                    t3 = tds[2].xpath(".//text()")
                    t3 = t3[0].replace("/", "或").replace("：", "")
                    t4 = tds[3].xpath(".//text()")
                    # print(t1, t2, t3, t4)
                    if t2:
                        props[t1] = t2[0]
                    if t4:
                        props[t3] = t4[0]

                elif len(tds) == 2:
                    t1 = tds[0].xpath(".//text()")
                    t1 = t1[0].replace("/", "或").replace("：", "")
                    t2 = tds[1].xpath(".//text()")
                    # print(t1, t2)
                    if t2:
                        props[t1] = t2[0]
        else:
            for tr in trs:
                tds = tr.xpath(".//td")
                if len(tds) == 4:
                    t1 = tds[0].xpath(".//text()")
                    t2 = tds[1].xpath(".//text()")
                    t3 = tds[2].xpath(".//text()")
                    t4 = tds[3].xpath(".//text()")
                    # print(t1, t2, t3, t4)
                    table_dict[t1[0]] = "-" if len(t2) == 0 else t2[0]
                    table_dict[t3[0]] = "-" if len(t4) == 0 else t4[0]

                elif len(tds) == 2:
                    t1 = tds[0].xpath(".//text()")
                    t2 = tds[1].xpath(".//text()")
                    # print(t1, t2)
                    table_dict[t1[0]] = "-" if len(t2) == 0 else t2[0]

                elif len(tds) == 1 and thead == "其他":
                    t1 = tds[0].xpath(".//text()")
                    # print(t1)
                    props["其他说明"] = "-" if len(t2) == 0 else t1[0]

                elif len(tds) == 3 and thead == "else":
                    t1 = tds[0].xpath(".//text()")
                    t2 = tds[1].xpath(".//text()")
                    t3 = tds[2].xpath(".//text()")

                    if t1[0] == "产品型号":
                        continue
                    else:
                        print("需要处理")

                elif len(tds) == 5:
                    t1 = tds[0].xpath(".//text()")
                    t2 = tds[1].xpath(".//text()")
                    t3 = tds[2].xpath(".//text()")
                    t4 = tds[3].xpath(".//text()")
                    t5 = tds[4].xpath(".//@onclick")
                    # print(t1, t2, t3, t4, t5)
                    if t1[0] == "产品型号":
                        continue
                    else:
                        t5 = t5[0].replace("windows.open('", "").replace("window.open('", "")
                        t5 = t5[:-2]
                        props["燃油达标公告"] = t5

                elif len(tds) == 6:
                    t1 = tds[0].xpath(".//text()")
                    t2 = tds[1].xpath(".//text()")
                    t3 = tds[2].xpath("./text()")
                    t4 = tds[3].xpath(".//text()")
                    t5 = tds[4].xpath(".//text()")
                    t6 = tds[5].xpath(".//@onclick")
                    # print(t1, t2, t3, t4, t5, t6)
                    if t1[0] == "信息公开编号":
                        continue
                    else:
                        env_report_props = dict()
                        env_report_props["信息公开编号"] = t1[0]
                        env_report_props["车型型号"] = t2[0]
                        env_report_props["发动机型号"] = t3[0]
                        env_report_props["公开时间"] = t4[0]
                        env_report_props["生产企业"] = t5[0]
                        t6 = t6[0].replace("windows.open('", "").replace("window.open('", "")
                        t6 = t6[:-2]
                        env_report_props["详情"] = t6

                        env_report_props["备注"] = "环保公告"

                        entity = {"type": "政府文件", "name": env_report_props["信息公开编号"], "props": env_report_props}
                        print(entity)
                        entities.append(entity)
                        relation = {"head": env_report_props["信息公开编号"], "tail": h1, "type": "文件关系", "props": {}}
                        print(relation)
                        relations.append(relation)


    props["车辆类型"] = table_dict["车辆名称："]
    props["公告批次"] = table_dict["公告批次："]
    props["公告型号"] = table_dict["产品号："]
    props["品牌"] = table_dict["中文品牌："]
    props["所属企业"] = table_dict["企业名称："]
    props["企业地址"] = table_dict["企业地址："]

    entity = {"type": "企业", "name": props["所属企业"], "props": {"地址": props["企业地址"]}}
    print(entity)
    entities.append(entity)
    relation = {"head": props["所属企业"], "tail": h1, "type": "拥有产品", "props": {}}
    print(relation)
    relations.append(relation)

    props["免检"] = table_dict["免检："]
    props["免检有效期止"] = table_dict["免检有效期止："]

    engines = props["发动机型号"].split(";")
    engines_companys = props["发动机生产企业"].split(";")
    engines_outputs = props["发动机排量"].split(";")
    engines_powers = props["发动机功率"].split(";")
    for i in range(len(engines)):
        engine_props = {}
        engine_props["所属企业"] = engines_companys[i]
        engine_props["排量(ml)"] = engines_outputs[i]
        engine_props["功率(kw)"] = engines_powers[i]
        entity = {"type": "发动机", "name": engines[i], "props": engine_props}
        print(entity)
        entities.append(entity)
        relation = {"head": engine_props["所属企业"], "tail": engines[i], "type": "拥有产品", "props": {}}
        print(relation)
        relations.append(relation)
        relation = {"head": h1, "tail": engines[i], "type": "配置", "props": {}}
        print(relation)
        relations.append(relation)

    props["反光标识型号"] = table_dict["标识型号："]
    props["反光标识企业"] = table_dict["标识企业："]
    props["反光标识商标"] = table_dict["标识商标："]

    entity = {"type": "车", "name": h1, "props": props}
    print(entity)
    entities.append(entity)

    r = {"entities": entities, "relations": relations}
    return r




def Wangli_run(base_path):
    '''
    预处理：
    文件结构为
    :return:
    '''
    for html in os.listdir(f"{base_path}"):
        h = etree.parse(f"{base_path}/{html}", etree.HTMLParser())
        Wangli_HtmlToJson(h)

Wangli_run("./Liu_html")
