import os
import sys
import math
import numpy as np
import vtk
import time

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


class c2v(object):
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

        self.var_name = []
        self.variables = []
        self.var_vtkarr = []
        
        self.elems_num = 0  # 元素数
        self.start_read_zone = False

        self.elems_faces_map = {}
        self.elems_nodes_map = {}

        self.nodes_neigh_map = {}
        self.elems_center_map = {}
        self.elems_nodes_num = 0

        self.p_uvw = vtk.vtkFloatArray()
        self.p_uvw.SetNumberOfComponents(3)
        self.p_uvw.SetName("uvw")
    
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

        self.p_uvw = vtk.vtkFloatArray()
        self.p_uvw.SetNumberOfComponents(3)
        self.p_uvw.SetName("uvw")
        self.p_uvw.SetNumberOfTuples(0)

    def convert_to_vtk(self, file_path, dat_dim=2):
        print("Reading " + file_path + " ...")
        self.data_dim = dat_dim
        with open(file_path, encoding="utf-8") as f:
            time_start = time.time()
            line = f.readline()
            while line:
                temp_data = line.strip().split(' ')
                if temp_data[0].upper() == 'TITLE':
                    self.title = line.strip().split('\"')[-2]
                    print("Title:",self.title)
                elif temp_data[0].upper() == 'VARIABLES':
                    while True:
                        name = line.strip().split('\"')[-2]
                        vtk_array = vtk.vtkFloatArray()
                        vtk_array.SetNumberOfComponents(1)
                        vtk_array.SetName(name)
                        self.var_vtkarr.append(vtk_array)
                        self.var_name.append(name)

                        line = f.readline()
                        temp_data = line.strip().split(' ')
                        if temp_data[0].upper() == 'ZONE':
                            print(len(self.var_name),self.var_name)
                            break
                
                if temp_data[0].upper() == 'ZONE':
                    self.block_name = temp_data[1].split('\"')[-2]
                    print('Block:',self.block_name)
                    self.block_num += 1
                    self.start_read_zone = True
                    line = f.readline() #  STRANDID=0, SOLUTIONTIME=0
                    line = f.readline() #  Nodes=8577592, Faces=25441300, Elements=8432000, ZONETYPE=FEPolyhedron
                    N_F_E = line.strip().split(', ')
                    for nfe in N_F_E :
                        nd = nfe.split('=')
                        if nd[0] == 'Nodes':
                            self.nodes_num = int(nd[1])
                        elif nd[0] == 'Faces':
                            self.faces_num = int(nd[1])
                        elif nd[0] == 'Elements':
                            self.elems_num = int(nd[1])

                    line = f.readline() # DATAPACKING=BLOCK
                    line = f.readline() # VARLOCATION=([4-15]=CELLCENTERED)
                    line = f.readline() # TotalNumFaceNodes=101763340, NumConnectedBoundaryFaces=0, TotalNumBoundaryConnections=0
                    if line.strip().split(', ')[0].split('=')[0].upper() == 'TOTALNUMFACENODES':
                        self.total_faces_nodes_num = int(line.strip().split(', ')[0].split('=')[-1])
                    if self.total_faces_nodes_num == 0:
                        self.total_faces_nodes_num = self.faces_num*2
                    print('total_faces_nodes_num ',self.total_faces_nodes_num)
                    line = f.readline() # DT=(SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE SINGLE )

                    count = 0 
                    ele_id = 0
                    tmp_var = []
                    print('Read', self.var_name[ele_id], 'start ...')
                    while count < self.nodes_num*(3):
                        line = f.readline()
                        data = line.strip().split(' ')
                        for dat in data:
                            tmp_var.append(float(dat))
                            count += 1
if count % self.nodes_num == 0:
                                self.variables.append(tmp_var)
                                tmp_var = []
                                ele_id += 1
                                print('Read', self.var_name[ele_id], 'start ...')
                                break
                    tmp_var = []
                    count = 0
                    while count < self.elems_num*(len(self.var_name)-3):   
                        line = f.readline()
                        data = line.strip().split(' ')
                        for dat in data:
                            tmp_var.append(float(dat))
                            count += 1
                            if count % self.elems_num == 0:
                                self.variables.append(tmp_var)
                                tmp_var = []
                                ele_id += 1
                                if ele_id < len(self.var_name):
                                    print('Read', self.var_name[ele_id], 'start ...')
                                break
                    print('Read basic data done')
                
                if self.start_read_zone:
                    if temp_data[0] == '#' and  temp_data[-1].upper() == 'FACE':
                        print('Read the number of vertices per face start ...')
                        count = 0 
                        while count < self.faces_num:
                            line = f.readline()
                            data = line.strip().split(' ')
                            for dat in data:
                                self.faces_nodes_num.append(int(dat))
                                count += 1
        
                    elif temp_data[0] == '#' and  temp_data[1].upper() == 'FACE' and  temp_data[2].upper() == 'NODES':
                        print('Read the vertices per face start ...')
                        count = 0
                        faceid = 0 
                        face_inid = []
                        while count < self.total_faces_nodes_num:
                            line = f.readline()
                            data = line.strip().split(' ')
                            for dat in data:
                                face_inid.append(int(dat)-1)
                                count += 1
                                if len(self.faces_nodes_num) == 0 :
                                    if len(face_inid) >= 2:
                                        self.faces.append(face_inid)
                                        face_inid = []
                                        faceid += 1
                                elif len(face_inid) >= self.faces_nodes_num[faceid]:
                                    self.faces.append(face_inid)
                                    face_inid = []
                                    faceid += 1
                                    
                    elif temp_data[0] == '#' and  temp_data[1].upper() == 'LEFT' and  temp_data[2].upper() == 'ELEMENTS':
                        print('Read the left elements start ...')
                        count = 0
                        while count < self.faces_num:
                            line = f.readline()
                            data = line.strip().split(' ')
                            for dat in data:
                                if not int(dat)-1 in self.elems_faces_map:
                                    self.elems_faces_map[int(dat)-1] = [count]
                                else :
                                    self.elems_faces_map[int(dat)-1].append(count)
                                count += 1
                        print('Read structure data done')    

                    elif temp_data[0] == '#' and  temp_data[1].upper() == 'RIGHT' and  temp_data[2].upper() == 'ELEMENTS':
                        print('Read the right elements start ...')
                        count = 0
                        while count < self.faces_num:
                            line = f.readline()
                            data = line.strip().split(' ')
                            for dat in data:
                                if not int(dat)-1 in self.elems_faces_map:
                                    self.elems_faces_map[int(dat)-1] = [count]
                                else :
                                    self.elems_faces_map[int(dat)-1].append(count)
                                    # self.elems_faces_map[int(dat)-1].insert(0,count)
                                count += 1
                        print('Read structure data done')   
                        time_end = time.time()
                        print('faces num: ', len(self.faces),' read tim',time_end - time_start)
                        self._change()
                        self._inter()
                        self._save(file_path[:-4] +'_'+self.block_name+ '.vtk')
                        self._init_data()
                        

                line = f.readline()
        
    def _save(self, vtk_path):
        print('Write points start ...')
        points = vtk.vtkPoints()
        for i in range(len(self.variables[0])):
            points.InsertNextPoint(self.variables[0][i], self.variables[1][i], self.variables[2][i])
        
        ugrid = vtk.vtkUnstructuredGrid()
        ugrid.SetPoints(points)

        ugrid.GetPointData().SetVectors(self.p_uvw)
        for var_id in range(3,len(self.var_name)):
            if not self.var_name[var_id] == 'u' and not self.var_name[var_id] == 'v' and not self.var_name[var_id] == 'w':
                ugrid.GetPointData().SetActiveScalars(self.var_name[var_id])
                ugrid.GetPointData().SetScalars(self.var_vtkarr[var_id])

        print('Write cells start ...')
        cell2,cell4,cell5,cell6,cell8,cellO = 0,0,0,0,0,0
        for key,val in self.elems_nodes_map.items():
            if self.data_dim == 2 and len(val) == 4:
                cell = vtk.vtkQuad()
                # cell = vtk.vtkPixel()
                cnt = 0
                for ind in val:
                    cell.GetPointIds().SetId(cnt, ind)
                    cnt += 1
                cell2 += 1
                ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
            elif len(val) == 4:
                cell = vtk.vtkTetra()
                cnt = 0
                for ind in val:
                    cell.GetPointIds().SetId(cnt, ind)
                    cnt += 1
                cell4 += 1
                ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
            elif len(val) == 5:
                cell = vtk.vtkPyramid()
                cnt = 0
                for ind in val:
                    cell.GetPointIds().SetId(cnt, ind)
                    cnt += 1
                cell5 += 1
                ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
            elif len(val) == 6:
                cell = vtk.vtkWedge()
                cnt = 0
                for ind in val:
                    cell.GetPointIds().SetId(cnt, ind)
                    cnt += 1
                cell6 += 1
                ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
            elif len(val) == 8:
                cell = vtk.vtkHexahedron()
                cnt = 0
                for ind in val:
                    cell.GetPointIds().SetId(cnt, ind)
                    cnt += 1
                cell8 += 1
                ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
            else :
                cellO += 1
        print('quad:',cell2,' tetr:', cell4, ' pyra:', cell5,' wedg:', cell6, ' hexa:', cell8, ' other:', cellO)
        
        # print('Write data into',vtk_path,'file ...')
        # writer = vtk.vtkUnstructuredGridWriter()
        # # writer.SetFileName(vtk_path)
        # writer.SetFileName(vtk_path[:-4]+'_uns.vtk')
        # writer.SetInputData(ugrid)
        # writer.Update()
        # writer.Write() 
        # print('Write data done')

        uns2poly = vtk.vtkDataSetSurfaceFilter() # UnstructuredGrid -> PolyData
        uns2poly.SetInputData(ugrid)
        uns2poly.Update()

        normal = vtk.vtkPolyDataNormals()
        normal.SetInputData(uns2poly.GetOutput())
        normal.SetComputePointNormals(1) #开启点法向量计算
        normal.SetComputeCellNormals(0)  #关闭单元法向量计算
        normal.ComputePointNormalsOn()
        normal.Update()
        
        print('Write data into',vtk_path,'file ...')
        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(vtk_path[:-4]+'_nor_poly.vtk')
        writer.SetInputData(normal.GetOutput())
        writer.Update()
        writer.Write() 
        print('Write data done')

    def _change(self):
        mean = 0
        count = 0.0 
        tmp_arr = []
        
        time_start = time.time()
        # key:
        # val:face id list
        for key,val in self.elems_faces_map.items():
            
            # 从中找出完全不同的两个面
            tmp_arr = []
            for faceid in val:
                for nid in self.faces[faceid]:
                    tmp_arr.append(nid)

            vv = np.unique(tmp_arr).tolist()
            if key < 0:
                print(key,':',len(vv))
                continue 

            # sorted(vv, key=lambda id:(self.variables[2][id],self.variables[1][id],self.x[id]))
            if self.data_dim == 2 and len(vv) == 4:
                faceid = val[0]
                a = self.faces[faceid][0]
                b = self.faces[faceid][1]
                c = 0

                a_list = [a]
                b_list = [b]
                vv = [a,b]
                for it in range(len(val)):
                    if it == 0:
                        continue
                    fid = val[it]
                    diff_list = list(set(self.faces[fid]).difference(set(a_list)))
                    if len(diff_list) == 2:
                        diff_list2 = list(set(self.faces[fid]).difference(set(b_list)))
                        if len(diff_list2) == 1:
                            vv.append(diff_list2[0])
                            break

                for it in range(len(val)):
                    fid = val[it]
                    diff_list = list(set(self.faces[fid]).difference(set(vv)))
                    if len(diff_list) == 1:
                        vv.append(diff_list[0])
                        break

                self.elems_nodes_map[key] = vv
                np_a = np.array([self.variables[0][vv[0]],self.variables[1][vv[0]],self.variables[2][vv[0]]])
                np_b = np.array([self.variables[0][vv[1]],self.variables[1][vv[1]],self.variables[2][vv[1]]])
                np_c = np.array([self.variables[0][vv[2]],self.variables[1][vv[2]],self.variables[2][vv[2]]])
                np_d = np.array([self.variables[0][vv[3]],self.variables[1][vv[3]],self.variables[2][vv[3]]])
                np_center = ((np_b + np_a)/2 + (np_c + np_d)/2)/2

                for nid in vv:
                    if not nid in self.nodes_neigh_map:
                        self.nodes_neigh_map[nid] = [key]
                    else:
                        self.nodes_neigh_map[nid].append(key)
                self.elems_center_map[key] = np_center.tolist()
            elif len(vv) == 4:
                self.elems_nodes_map[key] = vv
                np_a = np.array([self.variables[0][vv[0]],self.variables[1][vv[0]],self.variables[2][vv[0]]])
                np_b = np.array([self.variables[0][vv[1]],self.variables[1][vv[1]],self.variables[2][vv[1]]])
                np_c = np.array([self.variables[0][vv[2]],self.variables[1][vv[2]],self.variables[2][vv[2]]])
                np_d = np.array([self.variables[0][vv[3]],self.variables[1][vv[3]],self.variables[2][vv[3]]])
                np_center = ((np_b + np_a)/2 + (np_c + np_d)/2)/2

                for nid in vv:
                    if not nid in self.nodes_neigh_map:
                        self.nodes_neigh_map[nid] = [key]
                    else:
                        self.nodes_neigh_map[nid].append(key)
                self.elems_center_map[key] = np_center.tolist()
            elif len(vv) == 5:
                for fid in val:
                    if len(self.faces[fid]) == 4:
                        t_vv = [t_nid for t_nid in self.faces[fid]]
                        t_vv.append(list(set(vv).difference(set(self.faces[fid])))[0])
                        self.elems_nodes_map[key] = t_vv

                        np_a = np.array([self.variables[0][t_vv[0]],self.variables[1][t_vv[0]],self.variables[2][t_vv[0]]])
                        np_b = np.array([self.variables[0][t_vv[1]],self.variables[1][t_vv[1]],self.variables[2][t_vv[1]]])
                        np_c = np.array([self.variables[0][t_vv[2]],self.variables[1][t_vv[2]],self.variables[2][t_vv[2]]])
                        np_d = np.array([self.variables[0][t_vv[3]],self.variables[1][t_vv[3]],self.variables[2][t_vv[3]]])
                        np_a1 = np.array([self.variables[0][t_vv[4]],self.variables[1][t_vv[4]],self.variables[2][t_vv[4]]])

                        np_center = (((np_b + np_a)/2 + (np_c + np_d)/2)/2 + np_a1)/2
                        self.elems_center_map[key] = np_center.tolist()

                        for nid in t_vv:
                            if not nid in self.nodes_neigh_map:
                                self.nodes_neigh_map[nid] = [key]
                            else:
                                self.nodes_neigh_map[nid].append(key)
                        break
            elif len(vv) == 6:
                quadrilateral = []
                triangle = []
                for it in range(len(val)):
                    fid = val[it]
                    if len(self.faces[fid]) == 4:
                        quadrilateral.append(fid)
                    elif len(self.faces[fid]) == 3:
                        triangle.append(fid)
                    else:
                        print('polyhedron6 is not wedge!')
                        break

                set_face_a = set(self.faces[quadrilateral[0]]).intersection(set(self.faces[triangle[0]]))
                set_face_b = set(self.faces[quadrilateral[0]]).intersection(set(self.faces[triangle[1]]))
                set_face_a1 = set(self.faces[quadrilateral[1]]).intersection(set(self.faces[triangle[0]]))
                set_face_b1 = set(self.faces[quadrilateral[1]]).intersection(set(self.faces[triangle[1]]))
                low_beg = list(set_face_a.intersection(set_face_a1))[0]
                high_beg = list(set_face_b.intersection(set_face_b1))[0]
                vv = []
                beg = 0
                for it in range(3):
                    if self.faces[triangle[0]][it] == low_beg:
                        beg = it
                        break
                for it in range(3):
                    vv.append(self.faces[triangle[0]][(it+beg)%3])
                beg = 0
                for it in range(3):
                    if self.faces[triangle[1]][it] == high_beg:
                        beg = it
                        break
                for it in range(3):
                    vv.append(self.faces[triangle[1]][(it+beg)%3])
                
                self.elems_nodes_map[key] = vv

                np_a = np.array([self.variables[0][vv[0]],self.variables[1][vv[0]],self.variables[2][vv[0]]])
                np_b = np.array([self.variables[0][vv[1]],self.variables[1][vv[1]],self.variables[2][vv[1]]])
                np_c = np.array([self.variables[0][vv[2]],self.variables[1][vv[2]],self.variables[2][vv[2]]])
                np_a1 = np.array([self.variables[0][vv[3]],self.variables[1][vv[3]],self.variables[2][vv[3]]])
                np_b1 = np.array([self.variables[0][vv[4]],self.variables[1][vv[4]],self.variables[2][vv[4]]])
                np_c1 = np.array([self.variables[0][vv[5]],self.variables[1][vv[5]],self.variables[2][vv[5]]])

                np_center = (((np_b + np_a)/2 + np_c)/2 + ((np_b1 + np_a1)/2 + np_c1)/2)/2
                self.elems_center_map[key] = np_center.tolist()

                for nid in vv:
                    if not nid in self.nodes_neigh_map:
                        self.nodes_neigh_map[nid] = [key]
                    else:
                        self.nodes_neigh_map[nid].append(key)
            elif len(vv) == 8:
                faceid = val[0]
                a = self.faces[faceid][0]
                b = self.faces[faceid][1]
                c = self.faces[faceid][2]
                d = self.faces[faceid][3]

                ab_list = [a,b]
                a1b1_list = []
                for it in range(len(val)):
                    if it == 0:
                        continue
                    fid = val[it]
                    diff_list = list(set(self.faces[fid]).difference(set(ab_list)))
                    if len(diff_list) == 2:
                        a1b1_list = diff_list
                        break

                bc_list = [b,c]
                b1c1_list = []
                for it in range(len(val)):
                    if it == 0:
                        continue
                    fid = val[it]
                    diff_list = list(set(self.faces[fid]).difference(set(bc_list)))
                    if len(diff_list) == 2:
                        b1c1_list = diff_list
                        break
                
                a1 = list(set(a1b1_list).difference(set(b1c1_list)))[0]
                b1 = list(set(a1b1_list).intersection(set(b1c1_list)))[0]
                c1 = list(set(b1c1_list).difference(set(a1b1_list)))[0]
                d1 = list(set(vv).difference(set([a,b,c,d,a1,b1,c1])))[0]
                vv = [a,b,c,d,a1,b1,c1,d1]
                self.elems_nodes_map[key] = vv

                # 定位到中心点，然后计算其中心点的位置，便于后期对实质每个点的插值
                np_a = np.array([self.variables[0][a],self.variables[1][a],self.variables[2][a]])
                np_b = np.array([self.variables[0][b],self.variables[1][b],self.variables[2][b]])
                np_c = np.array([self.variables[0][c],self.variables[1][c],self.variables[2][c]])
                np_d = np.array([self.variables[0][d],self.variables[1][d],self.variables[2][d]])
                np_a1 = np.array([self.variables[0][a1],self.variables[1][a1],self.variables[2][a1]])
                np_b1 = np.array([self.variables[0][b1],self.variables[1][b1],self.variables[2][b1]])
                np_c1 = np.array([self.variables[0][c1],self.variables[1][c1],self.variables[2][c1]])
                np_d1 = np.array([self.variables[0][d1],self.variables[1][d1],self.variables[2][d1]])
                np_center = (((np_b + np_a)/2 + (np_c + np_d)/2)/2 + ((np_b1 + np_a1)/2 + (np_c1 + np_d1)/2)/2)/2
                self.elems_center_map[key] = np_center.tolist()

                for nid in vv:
                    if not nid in self.nodes_neigh_map:
                        self.nodes_neigh_map[nid] = [key]
                    else:
                        self.nodes_neigh_map[nid].append(key)

            else:
                print(len(vv),' - key:',key,'  val:',vv) 
            mean += len(vv)
            count = count + 1    
        self.elems_faces_map.clear()
        self.elems_nodes_num = mean
        time_end = time.time()
        print('elem means: ', float(mean) / count, ' change tim',time_end - time_start)

    def _inter(self):
        time_start = time.time()
        print("Interpolation ...")
        for nodeid in range(self.nodes_num):
            if not nodeid in self.nodes_neigh_map:
                self.p_uvw.InsertNextTuple([0,0,0])
                for varid in range(3,len(self.var_vtkarr)):
                    self.var_vtkarr[varid].InsertNextValue(0)
                continue
            
            var_neigh_arr = []
            for varid in range(0,len(self.var_name)):
                var_neigh_arr.append([])

            neigh_xyz = []
            for elemid in self.nodes_neigh_map[nodeid]:
                # xyz 
                neigh_xyz.append(self.elems_center_map[elemid])
                # neigh
                # center
                for var_id in range(3,len(self.var_name)):
                    var_neigh_arr[var_id].append(self.variables[var_id][elemid])

            # interpolation
            # save self.p_uvw
            p0 = [self.variables[0][nodeid], self.variables[1][nodeid], self.variables[2][nodeid]]
            tu,tv,tw = [],[],[]
            for var_id in range(3,len(self.var_name)):
                if self.var_name[var_id] == 'u':
                    tu = interpolation(p0,neigh_xyz,var_neigh_arr[var_id])
                elif self.var_name[var_id] == 'v':
                    tv = interpolation(p0,neigh_xyz,var_neigh_arr[var_id])
                elif self.var_name[var_id] == 'w':
                    tw = interpolation(p0,neigh_xyz,var_neigh_arr[var_id])
                else :
                    self.var_vtkarr[var_id].InsertNextValue(interpolation(p0,neigh_xyz,var_neigh_arr[var_id]))
            self.p_uvw.InsertNextTuple([tu,tv,tw])

        time_end = time.time()
        print("Interpolation done",time_end - time_start)


# 输入:
#   Patch dat文件,即: 
#       python .\convert_tecplot_to_multivtk.py patch.dat
#   如果输出的网格错误，则再后面输入参数1，如
#       python .\convert_tecplot_to_multivtk.py patch.dat 1
# 输出:
#   多个vtk的polydata文件, 一个Zone一个vtk文件
def help():
    print('convert_patch_tec2multivtk:')
    print('=============================== HELP ===============================')
    print('>> 输入:')
    print('   Patch dat文件,即:')
    print('       python .\convert_tecplot_to_multivtk.py patch.dat')
    print('   如果输出的网格错误，则再后面输入参数1，如')
    print('       python .\convert_tecplot_to_multivtk.py patch.dat 1')
    print('>> 输出:')
    print('   多个vtk的polydata文件, 一个Zone一个vtk文件')
    print('================================ END ================================')
    print('')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        obj = c2v()
        obj.convert_to_vtk(sys.argv[1])
    elif len(sys.argv) == 3:
        obj = c2v()
        print("file,dim:")
        print("    ",sys.argv[1],sys.argv[2])
        obj.convert_to_vtk(sys.argv[1],int(sys.argv[2]))
    else:
        help()
