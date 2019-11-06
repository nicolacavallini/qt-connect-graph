import re

from os import listdir
from os.path import isfile, join

from graphviz import Digraph

def get_source_files(path,extensions_list):

    file_list = [f for f in listdir(path) if isfile(join(path, f))]

    source_list = []
    for f in file_list:
        for e in extensions_list:
            if (f[-len(e):]==e):
                source_list.append(path+"/"+f)
    return source_list


def connnection_list_from_file(filename,conncetion_list):
    conncetion_list[filename]=[]
    with open(filename, "r") as file:
        connection = ""
        acc = False
        for l in file:
            if ("connect(") in l:
                acc = True
            if acc:
                connection +=l
            if (");") in l:
                acc = False
                connection = re.sub(' ', '', connection)
                if connection!="" and connection[:2]!="//":
                    connection = re.sub('\n', '', connection)

                    conncetion_list[filename].append(connection)
                connection = ""
    return conncetion_list

def print_dic(conncetion_list):
    for f,cl in conncetion_list.items():
        print(f)
        for c in cl:
            print("->"+c)

def update_node_dicionary(dic,class_method):
    if class_method[0] not in dic:
        dic[class_method[0]] = [class_method[1]]
    else:
        dic[class_method[0]].append(class_method[1])

def unpack_signals_and_slots(conncetion_dic):
    signal_dic = {}
    slot_dic = {}

    for f,cl in conncetion_dic.items():
        print(f)
        for c in cl:
            c = c.split(',')
            if (len(c)==4):
                signal = c[1][1:].split('::')[-2:]
                slot = c[3][1:-2].split('::')[-2:]
                update_node_dicionary(signal_dic,signal)
                update_node_dicionary(slot_dic,slot)

    return signal_dic, slot_dic

def plot_cluster(digraph,signal_dic):

    signals = []

    for object,methods in signal_dic.items():
        obj = ''.join([c for c in object if c.isupper()])
        cluster_name = "cluster_"+str(obj)
        for m in methods:
            with digraph.subgraph(name=cluster_name) as c:
                signal_name=obj+"_"+m
                signals.append(signal_name)
                c.node(signal_name,signal_name)
                c.attr(label=object)

    return signals




if __name__ == "__main__":

    path="../STeAM-Experimental/source/lite/client00/"

    source_files = get_source_files(path,[".h",".cpp"])

    conncetion_dic = {}

    #for sf in source_files:
    #    connnection_list_from_file(sf,conncetion_dic)

    connnection_list_from_file(path+"Window.cpp",conncetion_dic)

    signal_dic, slot_dic = unpack_signals_and_slots(conncetion_dic)

    print_dic(signal_dic)

    print_dic(slot_dic)

    g = Digraph('G', filename='connection-diagram.gv')
    g.attr(compound='true')

    signal_list = plot_cluster(g,signal_dic)

    slot_list = plot_cluster(g,slot_dic)

    print(signal_list)

    for signal,slot in zip(signal_list,slot_list):
        g.edge(signal,slot)


    g.view()
