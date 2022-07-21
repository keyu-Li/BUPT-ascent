#pragma once
#include<iostream>
#include<string>
#include<fstream>
#include<sstream>
#include<vector>
#include<algorithm>
using namespace std;
#define VARIABLESNUM 12
class ParseData
{	
public:
	ParseData();
	void init();                     //解析具体操作
	string dataStandard(string str); //将str标准化以便于解析
	vector<string>variable;          //保存variable的属性x,y,z....
	vector<vector<string>>variValue; //3.578363732E-002 -7.619999815E-003 -3.125776330E-012 1.015216064E+003 2.199494781E+002 -1.460772514E+000 1.723183414E-005...
	vector<vector<string>>vetexPos;  //用于保存4个顶点值
	bool isStandard;                 //每行的数据是否标准
	int nodeNum;                     //点的数量
	int element;                     //顶点所对应的行数
	int faceneighborConnections;    
	string zoneType;                 
	string zone;
	string title;
};
