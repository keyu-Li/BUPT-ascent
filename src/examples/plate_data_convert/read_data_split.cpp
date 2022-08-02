#include <iostream>
#include <fstream>
#include <vector>
#include <iomanip>
#include <string>
#include <cstring>
#include <algorithm>
#include <map>

#include <ascent.hpp>
#include <conduit_blueprint.hpp>
#include <conduit_relay.hpp>

using namespace std;
int comm_size=4;
double* x;
double* y;
double* z;
double* rho;
double* u;
double* v;
double* w;
double* t;
double* p;
double* mach;
double* mu;
double* mu_turb;
double* k;
double* omega;
double* gmFactor;
double* reThetat;
double* fReRatio;
//
int* sizes;//每个面包含的顶点数量
int* connectivity;//每个面包含的顶点索引 
int* offsets;//每个面的顶点索引起点 
int* Left_cell;//每个面左侧的cell
int* Right_cell;//每个面右侧的cell 
int Nodes,Faces,Elements,TotalNumFaceNodes;//顶点数，面数，cell数 ，所有面包含的点数之和 
double bounds[3][2];
int cnts[3]={2,2,2};

double* sub_k;
int* sub_body_sizes;
int* sub_body_offsets;
int* sub_body_connectivity;
double* sub_x;
double* sub_y;
double* sub_z;
int* sub_sizes;
int* sub_offsets;
int* sub_connectivity;
//vector<int>* rank_cell = new vector<int>[comm_size];
//vector<int> rank_cell[comm_size];
struct node{
	int x,id;//体编号，面编号 
}; 
node* body;//所有体包含的面编号 
int* body_sizes;//每个体包含的面数量
int* body_connectivity;//每个体包含的面索引 
int* body_offsets;//每个体的面索引起点 
bool cmp(node x,node y){
	if(x.x==y.x) return x.id<y.id;
	else return x.x<y.x;
}
int string_to_int(string str){
	int result=0;
	sscanf(str.c_str(),"%d",&result);
	return result;
}
double string_to_double(string str){
	double result=0;
	sscanf(str.c_str(),"%lf",&result);
	return result;
}
int get_point_rank(double x,double y,double z){
	int a=(x-bounds[0][0])/((bounds[0][1]-bounds[0][0])/cnts[0]);
	int b=(y-bounds[1][0])/((bounds[1][1]-bounds[1][0])/cnts[1]);
	int c=(z-bounds[2][0])/((bounds[2][1]-bounds[2][0])/cnts[2]);
	return (a+b*cnts[0]+c*cnts[0]*cnts[1])%comm_size;
}
int main(int argc, char** argv) {
	conduit::Node subNodes[comm_size];

	ifstream in;
	in.open(argv[1]);
	if(!in){
		cout<<"文件打开错误！"<<endl;
	}
	string temp;
	int numbers;
	while(in>>temp){
		if(temp.substr(0,5)=="Nodes"){
			int len=temp.length();
			Nodes=string_to_int(temp.substr(6,len));
			//cout<<Nodes<<endl;
		}
		else if(temp.substr(0,5)=="Faces"){
			int len=temp.length();
			Faces=string_to_int(temp.substr(6,len));
			//cout<<Faces<<endl;
		}
		else if(temp.substr(0,8)=="Elements"){
			int len=temp.length();
			Elements=string_to_int(temp.substr(9,len));
			//cout<<Elements<<endl;
		}
		else if(temp.substr(0,17)=="TotalNumFaceNodes"){
			int len=temp.length();
			TotalNumFaceNodes=string_to_int(temp.substr(18,len));
			//cout<<TotalNumFaceNodes<<endl;
		}
		else if(!((temp[0]>='0'&&temp[0]<='9')||(temp[0]=='-'&&temp[1]>='0'&&temp[1]<='9'))) continue;
		else{//数据部分 
			break;
		}
	}
	x = new double[Nodes];
	y = new double[Nodes];
	z = new double[Nodes];
	rho = new double[Elements];
	u = new double[Elements];
	v = new double[Elements];
	w = new double[Elements];
	t = new double[Elements];
	p = new double[Elements];
	mach = new double[Elements];
	mu = new double[Elements];
	mu_turb = new double[Elements];
	k = new double[Elements];
	omega = new double[Elements];
	gmFactor = new double[Elements];
	reThetat = new double[Elements];
	fReRatio = new double[Elements];
	sizes = new int[Faces];
	connectivity = new int[TotalNumFaceNodes];
	offsets = new int[Faces];
	Left_cell = new int[Faces];
	Right_cell = new int[Faces];
	for(int i=1;i<=Nodes;++i){
		x[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Nodes;++i){
		y[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Nodes;++i){
		z[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		rho[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		u[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		v[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		w[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		t[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		p[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		mach[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		mu[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		mu_turb[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		k[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		omega[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		gmFactor[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		reThetat[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=Elements;++i){
		fReRatio[i-1]=string_to_double(temp);
		in>>temp; 
	}
	for(int i=1;i<=5;++i){//忽略注释 
		in>>temp; 
	}
	for(int i=1;i<=Faces;++i){
		sizes[i-1]=string_to_int(temp);
		in>>temp; 
	}
	offsets[0]=0;
	for(int i=1;i<Faces;++i){
		offsets[i]=offsets[i-1]+sizes[i-1];
	}
	for(int i=1;i<=3;++i){//忽略注释 
		in>>temp; 
	}
	for(int i=1;i<=TotalNumFaceNodes;++i){
		connectivity[i-1]=string_to_int(temp)-1;
		in>>temp; 
	}
	for(int i=1;i<=3;++i){//忽略注释 
		in>>temp; 
	}
	int num=2*Faces; 
	for(int i=1;i<=Faces;++i){
		Left_cell[i-1]=string_to_int(temp)-1;
		if(Left_cell[i-1]==-1) num--;
		in>>temp; 
	}
	for(int i=1;i<=3;++i){//忽略注释 
		in>>temp; 
	}
	for(int i=1;i<=Faces;++i){
		Right_cell[i-1]=string_to_int(temp)-1;
		if(Right_cell[i-1]==-1) num--;
		if(i!=Faces) in>>temp; 
	}
	body = new node[num];
	body_sizes = new int[Elements];
	body_connectivity = new int[num];
	body_offsets = new int[Elements];
	for(int i=0;i<Elements;++i) body_sizes[i]=0;
	int id=0;
	for(int i=1;i<=Faces;++i){
		if(Left_cell[i-1]==-1) continue;
		body[id].x=Left_cell[i-1];
		body[id++].id=i-1;
		body_sizes[Left_cell[i-1]]++;
	}
	for(int i=1;i<=Faces;++i){
		if(Right_cell[i-1]==-1) continue;
		body[id].x=Right_cell[i-1];
		body[id++].id=i-1;
		body_sizes[Right_cell[i-1]]++;
	}
	sort(body,body+num,cmp);
	for(int i=0;i<num;++i){
		body_connectivity[i]=body[i].id;
	}
	body_offsets[0]=0;
	for(int i=1;i<Elements;++i){
		body_offsets[i]=body_offsets[i-1]+body_sizes[i-1];
	}

	cout << "read done." << endl;

	int rank_cell[comm_size][Elements];
	int rank_size[comm_size];
	for(int i = 0; i < comm_size; ++i) {
		rank_size[i] = 0;
	}
	
	sub_k = new double[Elements];
	sub_body_sizes = new int[Elements];
	sub_body_offsets = new int[Elements];
	sub_body_connectivity = new int[6*Elements];
	sub_x = new double[Nodes];
	sub_y = new double[Nodes];
	sub_z = new double[Nodes];
	sub_sizes = new int[Faces];
	sub_offsets = new int[Faces];
	sub_connectivity = new int[4*Faces];
	map<int,int>point_map,face_map;

	for(int i=0;i<Nodes;++i){
		if(i==0){
			bounds[0][0]=0;bounds[0][1]=0;bounds[1][0]=0;bounds[1][1]=0;bounds[2][0]=0;bounds[2][1]=0;
		}
		bounds[0][0]=min(bounds[0][0],x[i]);
		bounds[0][1]=max(bounds[0][1],x[i]);
		bounds[1][0]=min(bounds[1][0],y[i]);
		bounds[1][1]=max(bounds[1][1],y[i]);
		bounds[2][0]=min(bounds[2][0],z[i]);
		bounds[2][1]=max(bounds[2][1],z[i]);
	}
	for(int i=0;i<Elements;++i){
		int body_start=body_offsets[i],body_end=(i==Elements-1?num:body_offsets[i+1]);
		for(int j=body_start;j<body_end;++j){
			int face_id=body_connectivity[j];
			int flag=0;
			int point_begin=offsets[face_id],point_end=(face_id==Faces-1?TotalNumFaceNodes:offsets[face_id+1]);
			for(int k=point_begin;k<point_end;++k){
				if(k==point_begin){
					int a=(x[connectivity[k]]-bounds[0][0])/((bounds[0][1]-bounds[0][0])/cnts[0]);
					int b=(y[connectivity[k]]-bounds[1][0])/((bounds[1][1]-bounds[1][0])/cnts[1]);
					int c=(z[connectivity[k]]-bounds[2][0])/((bounds[2][1]-bounds[2][0])/cnts[2]);
					int rank_id = (a+b*cnts[0]+c*cnts[0]*cnts[1])%comm_size;
					//int rank_id=get_point_rank(x[connectivity[k]],y[connectivity[k]],z[connectivity[k]]);
					rank_cell[rank_id][rank_size[rank_id]++] = i;
					flag=1;
				}
				else break;
			}
			if(flag) break;
		}
	}

	for(int i=0;i<comm_size;++i){
		int cell_count = rank_size[i];
		point_map.clear();
		face_map.clear();
		sub_body_offsets[0]=0;
		sub_offsets[0]=0;
		int map_point_count=0,map_face_count=0;
		int sub_connectivity_size=0,sub_face_size=0,sub_point_size=0;
		for(int j=0;j<rank_size[i];++j){//100000
			sub_k[j]=k[rank_cell[i][j]];
			int cell_id=rank_cell[i][j];
			int face_begin=body_offsets[cell_id],face_end=(cell_id==Elements-1?num:body_offsets[cell_id+1]);
			sub_body_sizes[j]=face_end-face_begin;
			if(j!=0) sub_body_offsets[j]=sub_body_offsets[j-1]+sub_body_sizes[j-1];
			for(int k=face_begin;k<face_end;++k){//6
				int face_id=body_connectivity[k];
				if(face_map[face_id]){
				}
				else{
					face_map[face_id]=++map_face_count;
					int point_begin=offsets[face_id],point_end=(face_id==Faces-1?TotalNumFaceNodes:offsets[face_id+1]);
					for(int l=point_begin;l<point_end;++l){//4
						if(point_map[connectivity[l]]==0) point_map[connectivity[l]]=++map_point_count;
						else continue;
						sub_x[sub_point_size]=x[connectivity[l]];
						sub_y[sub_point_size]=y[connectivity[l]];
						sub_z[sub_point_size++]=z[connectivity[l]];
					}
					sub_sizes[sub_face_size]=sizes[face_id];
					if(sub_face_size!=0) sub_offsets[sub_face_size]=sub_offsets[sub_face_size-1]+sub_sizes[sub_face_size-1];
					for(int l=0;l<4;++l){
						sub_connectivity[4*sub_face_size+l]=point_map[connectivity[point_begin+l]]-1;
					}
					sub_face_size++;
				}
				sub_body_connectivity[sub_connectivity_size++]=face_map[face_id]-1;
			}
		}

		subNodes[i]["state/domain"] = i;
		subNodes[i]["coordsets/coords/type"] = "explicit";
		subNodes[i]["coordsets/coords/values/x"].set_external(sub_x, sub_point_size);
		subNodes[i]["coordsets/coords/values/y"].set_external(sub_y, sub_point_size);
		subNodes[i]["coordsets/coords/values/z"].set_external(sub_z, sub_point_size);

		subNodes[i]["topologies/mesh/type"] = "unstructured";
		subNodes[i]["topologies/mesh/coordset"] = "coords";
		subNodes[i]["topologies/mesh/elements/shape"] = "polyhedral";
		subNodes[i]["topologies/mesh/elements/connectivity"].set_external(sub_body_connectivity, 6*cell_count);
		subNodes[i]["topologies/mesh/elements/sizes"].set_external(sub_body_sizes, cell_count);
		subNodes[i]["topologies/mesh/elements/offsets"].set_external(sub_body_offsets, cell_count);

		//设置拓扑形状类型
		subNodes[i]["topologies/mesh/subelements/shape"] = "polygonal";
		subNodes[i]["topologies/mesh/subelements/connectivity"].set_external(sub_connectivity, 4*sub_face_size);
		subNodes[i]["topologies/mesh/subelements/sizes"].set_external(sub_sizes, sub_face_size);
		subNodes[i]["topologies/mesh/subelements/offsets"].set_external(sub_offsets, sub_face_size);

		subNodes[i]["fields/k/association"] = "element";
		subNodes[i]["fields/k/topology"] = "mesh";
		subNodes[i]["fields/k/values"].set_external(sub_k, cell_count);

		conduit::relay::io::save(subNodes[i], "mesh_" + to_string(i) + ".json");

		ascent::Ascent a;
		a.open();
		a.publish(subNodes[i]);
		conduit::Node actions;
		conduit::Node & add_act = actions.append();
		add_act["action"] = "add_scenes";

		// declare a scene (s1) with one plot (p1) 
		// to render the dataset
		conduit::Node &scenes = add_act["scenes"];
		scenes["s1/plots/p1/type"] = "pseudocolor";
		scenes["s1/plots/p1/field"] = "k";
		scenes["s1/plots/p1/color_table/name"] = "Rainbow Desaturated";
		scenes["s1/renders/r1/image_name"] = "out_mesh_k_" + to_string(i);
		scenes["s1/renders/r1/camera/azimuth"] = 120.0;
		a.execute(actions);
		a.close();
	}
    return 0;
}

