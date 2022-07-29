from mpi4py import MPI
import conduit
import conduit.relay as relay
import conduit.relay.mpi
import ascent.mpi
import time


class c2m(object):
    def __init__(self):
        self.title = ''     # 标题
        self.block_name = ''
        self.data_dim = 2
        self.block_num = 0  
        self.nodes_num = 0  # 节点数

        self.var_name = [] # 存储variable的name
        self.variables = [] # 里面有len(variable)个list

        self.elems_num = 0  # 元素数
        self.start_read_zone = False

        self.elems_node_list = []

        self.node = conduit.Node()
        ## mpi
        self.comm_id = 0
        self.comm_size = 0
        self.subnodes = []
        self.rank_map = []
        # subnode
        self.points_values = []
        self.subelements = []
        self.points_map = [] # length is comm_size
        self.reverse_points_map = [] # length is comm_size
        self.bounds = []
        self.cuts = [2, 2, 2]
        
    def _init_mpi(self, comm_id):
        self.comm_id = comm_id
        self.comm_size = relay.mpi.size(comm_id)
        self.points_values = [[[] for _ in range(len(self.var_name))] for _ in range(self.comm_size)]
        self.subnodes = [ conduit.Node() for _ in range(self.comm_size)]
        self.subelements = [ [] for _ in range(self.comm_size) ]
        self.points_map = [ [] for _ in range(self.comm_size)] # 可能不需要这个
        self.reverse_points_map = [ [-1 for _ in range(self.nodes_num)] for _ in range(self.comm_size) ]
        self.rank_map = [ -1 for _ in range(self.nodes_num)]
        # bounds
        self.bounds = self._init_bounds()
    
    def divide_to_rank(self):
        comm_id   = MPI.COMM_WORLD.py2f()
        self._init_mpi(comm_id)
        
        # 遍历所有的element
        offset = 0
        while offset < len(self.elems_node_list):
            point_idx = self.elems_node_list[offset]
            point_rank = self.get_point_rank(self.variables[0][point_idx], self.variables[1][point_idx], self.variables[2][point_idx])
            for i in range(4):
                idx = self.elems_node_list[i+offset]
                # 如果point在rank中不存在，新增
                if self.reverse_points_map[point_rank][idx] == -1:
                    for var_id in range(len(self.var_name)):
                        self.points_values[point_rank][var_id].append(self.variables[var_id][idx])
                    self.subelements[point_rank].append(len(self.points_values[point_rank][0])-1)
                    self.reverse_points_map[point_rank][idx] = len(self.points_values[point_rank][0])-1
                # 如果存在，找到rank中点的位置
                else:
                    self.subelements[point_rank].append(self.reverse_points_map[point_rank][idx])
            offset += 4
        # 写入subnodes
        for rk in range(self.comm_size):
            self.subnodes[rk]['state/domain'] = rk
            # self.subnodes[0]['state/cycle'] = 0
            self.subnodes[rk]['coordsets/coords/type'] = 'explicit'
            self.subnodes[rk]['coordsets/coords/values/x'] = self.points_values[rk][0]
            self.subnodes[rk]['coordsets/coords/values/y'] = self.points_values[rk][1]
            self.subnodes[rk]['coordsets/coords/values/z'] = self.points_values[rk][2]

            self.subnodes[rk]['topologies/mesh/type'] = "unstructured"
            self.subnodes[rk]['topologies/mesh/coordset'] = "coords"
            self.subnodes[rk]['topologies/mesh/elements/shape'] = "tet"
            self.subnodes[rk]['topologies/mesh/elements/connectivity'] = self.subelements[rk]
            for i in range(3, len(self.var_name)):
                self.subnodes[rk]['fields/{}/association'.format(self.var_name[i])] = 'vertex'
                self.subnodes[rk]['fields/{}/topology'.format(self.var_name[i])] = 'mesh'
                self.subnodes[rk]['fields/{}/volume_dependent'.format(self.var_name[i])] = 'false'
                self.subnodes[rk]['fields/{}/values'.format(self.var_name[i])] = self.points_values[rk][i]
            conduit.relay.io.save(self.subnodes[rk], 'tet_{}.yaml'.format(rk))
            
        
        
    def get_point_rank(self, x,y,z):
        a = int((x - self.bounds[0][0]) // ((self.bounds[0][1] - self.bounds[0][0])/self.cuts[0]))
        b = int((y - self.bounds[1][0]) // ((self.bounds[1][1] - self.bounds[1][0])/self.cuts[1]))
        c = int((z - self.bounds[2][0]) // ((self.bounds[2][1] - self.bounds[2][0])/self.cuts[2]))
        return (a + b*self.cuts[0] + c*self.cuts[1]*self.cuts[0])%self.comm_size
        
    def _init_bounds(self):
        min_x, max_x = min(self.variables[0]), max(self.variables[0])
        min_y, max_y = min(self.variables[1]), max(self.variables[1])
        min_z, max_z = min(self.variables[2]), max(self.variables[2])
        return [
            [min_x, max_x],
            [min_y, max_y],
            [min_z, max_z]
        ]
    
    def _init_data(self):
        self.block_name = ''
        self.nodes_num = 0  # 节点数
    
        self.variables = []
        for var_id in range(0,len(self.var_name)):
            self.var_vtkarr[var_id].SetNumberOfTuples(0)
        
        self.elems_num = 0  # 元素数
        self.start_read_zone = False

        self.elems_node_list = []
        
        self.node.reset()
        self.node['state/domain'] = 0
        self.node['state/cycle'] = 0
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
                            self.elems_node_list.append(int(data)-1)
                else:
                    end_time = time.time()
                    print("--------END--------, time is {}".format(end_time-time_start))
                    break

    def name(arg1, arg2):
        # description
        pass

if __name__ == "__main__":
    comm_id   = MPI.COMM_WORLD.py2f()
    comm_rank = relay.mpi.rank(comm_id)
    n = conduit.Node()
    if comm_rank == 0:
        tester = c2m()
        tester.convert_to_mesh('../../flowfield.dat')
        tester.divide_to_rank()

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
        conduit.relay.io.save(tester.node, "tet.yaml")

        n = tester.subnodes[0]
        for i in range(1, tester.comm_size):
            relay.mpi.send_using_schema(tester.subnodes[i], dest=i, tag=0, comm=comm_id)
    else:
        relay.mpi.recv_using_schema(n, source=0, tag=0, comm=comm_id)
    actions = conduit.Node()
    relay.io.load(actions, 'actions.yaml')
    a = ascent.mpi.Ascent()
    mpi_options = conduit.Node()
    mpi_options["mpi_comm"] = comm_id 
    mpi_options["runtime/type"] = "ascent"
    mpi_options["runtime/backend"] = "openmp"
    a.open(mpi_options)
    a.publish(n)
    a.execute(actions)
    a.close()
        