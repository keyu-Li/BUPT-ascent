import imp
import os
import sys
import time
import math
import numpy as np
import conduit
import conduit.utils


# 计算两点间的距离
def distance(p, pi):
    dis = (p[0] - pi[0]) * (p[0] - pi[0]) + (p[1] - pi[1]) * (p[1] - pi[1]) + (p[2] - pi[2]) * (p[2] - pi[2])
    m_result = math.sqrt(dis)
    return m_result

def interpolation(p0, p_lst, v_lst):
    sum0 = 0
    sum1 = 0
    p_dist = []
    # 遍历获取该点距离所有采样点的距离
    cnt = 0
    for point in p_lst:
        if p0[0] == point[0] and p0[1] == point[1] and p0[2] == point[2]:
            return v_lst[cnt]
        p_dist.append( distance(p0, point))
        cnt += 1

    for it in range(len(p_dist)):
        sum0 += v_lst[it] / math.pow(p_dist[it], 2)
        sum1 += 1.0 / math.pow(p_dist[it], 2)

    return sum0 / sum1

class c2m(object):
    def __init__(self):
        self.title = ''     # 标题
        self.block_name = ''
        self.data_dim = 2
        self.block_num = 0  
        self.nodes_num = 0  # 节点数
        self.faces_num = 0  # 面片数
        self.faces = []     # 面对应节点的索引
        self.faces_nodes_num = [] # 每个面片的节点数
        self.total_faces_nodes_num = 0  # 所有面的总节点数

        self.var_name = [] # 存储variable的name
        self.variables = [] # 里面有len(variable)个list
        # self.var_vtkarr = []

        self.elems_num = 0  # 元素数
        self.start_read_zone = False

        self.elems_faces_map = {}
        self.elems_nodes_map = {}

        self.elems_node_list = []

        
        self.nodes_neigh_map = {}
        self.elems_center_map = {}
        self.elems_nodes_num = 0

        self.node = conduit.Node()

    
    def _init_data(self):
        self.block_name = ''
        self.nodes_num = 0  # 节点数
        self.faces_num = 0  # 面片数
        self.faces = []     # 面对应节点的索引
        self.faces_nodes_num = [] # 每个面片的节点数
        self.total_faces_nodes_num = 0  # 所有面的总节点数
    
        self.variables = []
        for var_id in range(0,len(self.var_name)):
            self.var_vtkarr[var_id].SetNumberOfTuples(0)
        
        self.elems_num = 0  # 元素数
        self.start_read_zone = False

        self.elems_faces_map = {}
        self.elems_nodes_map = {}

        self.nodes_neigh_map = {}
        self.elems_center_map = {}
        self.elems_nodes_num = 0
        self.elems_node_list = []
        
        self.node.reset()
        # self.node['state/domain'] = 0
        # self.node['state/cycle'] = 0
        self.node['coordsets/coords/type'] = 'explicit'

    
    def convert_to_mesh(self, file_path, dat_dim=2):
        self._init_data()
        print("Reading " + file_path + " ...")
        self.data_dim = dat_dim
        with open(file_path, encoding="utf-8") as f:
            time_start = time.time()
            line = f.readline()
            while line:
                temp_data = line.strip().split(" ")
                if temp_data[0].upper() == 'TITLE':
                    self.title = line.strip().split('\"')[-2]
                    print("Title:", self.title)
                    line = f.readline()
                elif temp_data[0].upper() == 'VARIABLES':
                    while True:
                        name = line.strip().split('\"')[-2]
                        # print(name)
                        self.var_name.append(name)
                        line = f.readline()
                        temp_data = line.strip().split(' ')
                        if temp_data[0].upper() == 'ZONE':
                            print(len(self.var_name),self.var_name)
                            break
                elif temp_data[0].upper() == 'ZONE':
                    self.block_name = temp_data[1].split('\"')[-2]
                    print('Block:',self.block_name)
                    self.block_num += 1
                    self.start_read_zone = True
                    line = f.readline() #  STRANDID=0, SOLUTIONTIME=0
                    line = f.readline() # Nodes=37364, Elements=190922, ZONETYPE=FETetrahedron
                    N_E = line.strip().split(', ')
                    for ne in N_E:
                        nd = ne.split('=')
                        if nd[0] == 'Nodes':
                            self.nodes_num = int(nd[1])
                        elif nd[0] == 'Elements':
                            self.elems_num = int(nd[1])
                    line = f.readline() # DATAPACKING=POINT
                    line = f.readline() # FACENEIGHBORCONNECTIONS=737908
                    line = f.readline() # FACENEIGHBORMODE=LOCALONETOONE
                    line = f.readline() # FEFACENEIGHBORSCOMPLETE=YES
                    line = f.readline() # DT=(SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE )
                    print('Read Point')
                    count = 0
                    # 初始化self.variables
                    for i in range(len(self.var_name)):
                        self.variables.append([])
                    print(len(self.variables))
                    while(count < self.nodes_num):
                        count += 1
                        line = f.readline()
                        datas = line.strip().split(' ')
                        if len(datas) != len(self.var_name):
                            raise("数据长度{} 对不上 变量数量 {}, {}".format(len(datas), len(self.var_name), line))
                        for index in range(len(self.var_name)):
                            self.variables[index].append(float(datas[index]))
                    print("Read elems")
                    count = 0
                    while(count < self.elems_num):
                        count += 1
                        line = f.readline()
                        datas = line.strip().split(' ')
                        if len(datas) != 4:
                            raise("数据不是4面体？")
                        for data in datas:
                            self.elems_node_list.append(int(data))
                else:
                    end_time = time.time()
                    print("--------END--------, time is {}".format(end_time-time_start))
                    break


if __name__ == '__main__':
    tester = c2m()
    tester.convert_to_mesh('./flowfield.dat')
    print("self.var_name = {}".format(tester.var_name))
    print("self.nodes_num is {} and len(self.variables[0]) is {}".format(tester.nodes_num, len(tester.variables[0])))
    tester.node['coordsets/coords/values/x'] = tester.variables[0]
    tester.node['coordsets/coords/values/y'] = tester.variables[1]
    tester.node['coordsets/coords/values/z'] = tester.variables[2]

    tester.node['topologies/mesh/type'] = "unstructured"
    tester.node['topologies/mesh/coordset'] = "coords"
    tester.node['topologies/mesh/elements/shape'] = "tet"
    tester.node['topologies/mesh/elements/connectivity'] = tester.elems_node_list
    for i in range(3, len(tester.var_name)):
        tester.node['fields/{}/association'.format(tester.var_name[i])] = 'vertex'
        tester.node['fields/{}/topology'.format(tester.var_name[i])] = 'mesh'
        tester.node['fields/{}/volume_dependent'.format(tester.var_name[i])] = 'false'
        tester.node['fields/{}/values'.format(tester.var_name[i])] = tester.variables[i]
    print(tester.node)
    conduit.relay.io.save(tester.node, "tet.yaml")


                    
