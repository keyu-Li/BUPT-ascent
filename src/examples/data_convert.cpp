//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
// Copyright (c) Lawrence Livermore National Security, LLC and other Ascent
// Project developers. See top-level LICENSE AND COPYRIGHT files for dates and
// other details. No copyright assignment is required to contribute to Ascent.
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//

//-----------------------------------------------------------------------------
///
/// file: conduit_example1.cpp
///
//-----------------------------------------------------------------------------

#include <iostream>
#include <vector>
#include "conduit.hpp"
#include<iostream>
#include<string>
#include<fstream>
#include<sstream>
#include<vector>
#include<algorithm>
#include<cmath>
#include<iomanip>
#include "conduit_blueprint.hpp"
#include"ascent.h"
#include<conduit_relay.hpp>
#define VARIABLESNUM 12

using namespace std;
using namespace conduit;
class ParseData
{	
public:
	ParseData();
	void init();
	string dataStandard(string str);//将str标准化以便于解析
	vector<string>variable;		    	//保存variable的属性x,y,z....
	vector<vector<double>>variValue;//3.578363732E-002 -7.619999815E-003 -3.125776330E-012 1.015216064E+003 2.199494781E+002 -1.460772514E+000 1.723183414E-005...
	vector<int>vetexPos;            //存四面体四个顶点
	double str2double(string s);
	int str2Int(string s);
	bool isStandard=false;
	int nodeNum;
	int element;
	int faceneighborConnections;
	string zoneType;
	string zone;
	string title;
};

//将数据标准化，以便于解析
string ParseData::dataStandard(string str)
{
	string res = "";
	int indexBe = -1;
	int index = str.find("=");
	while (index != -1)
	{
		res = res + string(str.begin() + (indexBe + 1), str.begin() + index);
		res = res + " " + "=" + " ";
		indexBe = index;
		index = str.find("=", index + 1);
	}
	res = res + string(str.begin() + (indexBe + 1), str.begin() + str.size());
	return res;
}

ParseData::ParseData()
{
	variValue.resize(VARIABLESNUM);
	
	init();
}

//string->double
double ParseData::str2double(string s)
{
	double d;
	stringstream ss;
	ss << s;
	ss >> setprecision(32) >> d;
	ss.clear();
	return d;
}

//string->int
int ParseData::str2Int(string s)
{
	int i;
	stringstream ss;
	ss << s;
	ss >> setprecision(16) >> i;
	ss.clear();
	return i;
}

//初始化
void ParseData::init()
{
	ifstream inf;
	inf.open("flowfield.dat", ios::in);
    if (!inf.is_open())
		cout << "open file is field!" << endl;
	string line;
	int index = 0;

	while (getline(inf, line))
	{
		stringstream ss;
		vector<string>vv;
		string t;
		if (!isStandard) {
			line = dataStandard(line);
		}
		ss << line;
		while (ss >> t)
		{
			if (t[t.size() - 1] == ',')t = t.substr(0, t.size() - 1);
				vv.push_back(t);
		}
    
		if (vv.size()) {
			//将第一个元素变成大写
			string uuper = vv[0];
			transform(uuper.begin(), uuper.end(), uuper.begin(), ::toupper);
			if (uuper == "TITLE")
			{
				title = vv[2];
			}
			//这里就是VARIABLES的值
			else if (uuper == "VARIABLES")
			{
				variable.push_back(vv[2]);
				for (int i = 1; i < VARIABLESNUM; i++)
				{
					getline(inf, line);
					line=string(line.begin()+1,line.end()-2);
					variable.push_back(line);
				}
			}
			else if (uuper == "ZONE")
			{
				zone = vv[3];
			}

			//Nodes、Element、ZONETYPE
			else if (uuper == "NODES")
			{
				nodeNum = str2Int(vv[2]);
				element = str2Int(vv[5]);
				zoneType = vv[8];
				getline(inf, line);
			}
			else if (uuper == "FACENEIGHBORCONNECTIONS")
			{
				faceneighborConnections = str2Int(vv[2]);
				getline(inf,line);
				getline(inf,line);
			}
			else if (uuper == "DT")
			{
				isStandard = true;
				index = 0;
			}
			else 
			{	
				if (index < nodeNum)
				{
					for (int i = 0; i < VARIABLESNUM; i++)
					{
						variValue[i].push_back(str2double(vv[i]));
					}
				}
				else if(index >= nodeNum && index < nodeNum + element)
				{
					vetexPos.push_back(str2Int(vv[0]));
					vetexPos.push_back(str2Int(vv[1]));
					vetexPos.push_back(str2Int(vv[2]));
					vetexPos.push_back(str2Int(vv[3]));
				}
				index++;
			}
		}
	}
  
	inf.close();
}

int main()
{
	ParseData pd;
	Node n;
	n["coordsets/coords/type"]="explicit";
	n["coordsets/coords/values/x"]=pd.variValue[0];
	n["coordsets/coords/values/y"]=pd.variValue[1];
	n["coordsets/coords/values/z"]=pd.variValue[2];
	n["topologies/mesh/type"]="unstructured";
	n["topologies/mesh/coordset"] = "coords";
  n["topologies/mesh/elements/shape"] = "tet";
	n["topologies/mesh/elements/connectivity"].set(pd.vetexPos);

	//创建分支并赋予各个field值
	for(int i = 3; i < VARIABLESNUM; i++)
	{
		stringstream ss;
		string res;
		ss<<"fields/"<<pd.variable[i]<<"/association";
		ss>>res;
		ss.clear();
		n[res]="vertex";
		ss<<"fields/"<<pd.variable[i]<<"/topology";
		ss>>res;
		ss.clear();
		n[res]="mesh";
		ss<<"fields/"<<pd.variable[i]<<"/volume_dependent";
		ss>>res;
		n[res]="false";
		ss.clear();
		ss<<"fields/"<<pd.variable[i]<<"/values";
		ss>>res;
		n[res].set(pd.variValue[i]);
	}

	conduit::relay::io::save(n,"tet1.yaml");
	return 0;
}
