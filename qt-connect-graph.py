import re

from os import listdir
from os.path import isfile, join

from graphviz import Digraph

def get_uppercase_letters(input):
    return ''.join([c for c in input if c.isupper()])

def get_source_files(path,extensions_list):

    file_list = [f for f in listdir(path) if isfile(join(path, f))]

    source_list = []
    for f in file_list:
        for e in extensions_list:
            if (f[-len(e):]==e):
                source_list.append(path+"/"+f)
    return source_list


def connnection_list_from_file(filename,conncetion_dic):
    conncetion_dic[filename]=[]
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

                    conncetion_dic[filename].append(connection)
                connection = ""
    return conncetion_dic

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

    signal_to_slot_list = []

    for f,cl in conncetion_dic.items():
        for c in cl:
            c = c.split(',')
            if (len(c)==4):
                
                signal = c[1][1:].split('::')[-2:]
                slot = c[3][1:-2].split('::')[-2:]

                sgn = get_uppercase_letters(signal[0])+"_"+signal[1]
                slt = get_uppercase_letters(slot[0])+"_"+slot[1]

                signal_to_slot_list.append((sgn,slt))

                update_node_dicionary(signal_dic,signal)
                update_node_dicionary(slot_dic,slot)

    return signal_dic, slot_dic, signal_to_slot_list

def plot_cluster(digraph,signal_dic):

    signals = []

    for object,methods in signal_dic.items():
        obj = ''.join([c for c in object if c.isupper()])
        cluster_name = "cluster_"+str(obj)
        for m in methods:
            with digraph.subgraph(name=cluster_name) as c:
                c.attr(style='filled', color='lightgrey')
                signal_name=obj+"_"+m
                signals.append(signal_name)
                c.node(signal_name,signal_name)
                c.attr(label=object)

    return signals




if __name__ == "__main__":

    path="../STeAM-Experimental/source/lite/client00/"

    source_files = get_source_files(path,[".h",".cpp"])

    conncetion_dic = {}

    for sf in source_files:
        connnection_list_from_file(sf,conncetion_dic)

    signal_dic, slot_dic, signal_to_slot_list = unpack_signals_and_slots(conncetion_dic)

    g = Digraph('G', filename='connection-diagram.gv')
    g.attr(compound='true',size='16,11')

    signal_list = plot_cluster(g,signal_dic)

    slot_list = plot_cluster(g,slot_dic)

    for signal_to_slot in signal_to_slot_list:
        sgn = signal_to_slot[0]
        slt = signal_to_slot[1]
        g.edge(sgn,slt)


    g.view()
