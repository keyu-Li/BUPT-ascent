#include"testParse.h"
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
	//cout << res << endl;
	return res;
}

ParseData::ParseData()
{
	variValue.resize(VARIABLESNUM);
	
	init();
}

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
		//cout << line << endl;
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
				//cout << vv[2] << endl;//这里就是title的值
				title = vv[2];
			}
			//这里就是VARIABLES的值
			else if (uuper == "VARIABLES")
			{
				//cout << vv[2] << endl;
				variable.push_back(vv[2]);
				for (int i = 1; i < VARIABLESNUM; i++)
				{
					getline(inf, line);
					//cout << line << endl;
					variable.push_back(line);
				}
			}
			else if (uuper == "ZONE")
			{
					//cout << vv[3] << endl;
				zone = vv[3];
			}

			//Nodes、Element、ZONETYPE
			else if (uuper == "NODES")
			{
				//cout << vv[2] << " " << vv[5] << " " << vv[8] << endl;
				nodeNum = stoi(vv[2]);
				element = stoi(vv[5]);
				zoneType = vv[8];
				getline(inf, line);
			}
			else if (uuper == "FACENEIGHBORCONNECTIONS")
			{
				//cout << vv[2] << endl;
				faceneighborConnections = stoi(vv[2]);
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
						variValue[i].push_back(vv[i]);
					}
				}
				else if(index >= nodeNum && index < nodeNum + element)
				{
					vetexPos.push_back({ vv[0],vv[1],vv[2],vv[3] });
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
	cout << pd.dataStandard("");
	cout << "TITLE: " << pd.title << endl;
	cout << "VARIABLES: ";
	for (int i = 0; i < pd.variable.size(); i++)
	{
		cout << pd.variable[i] << " ";
	}
	cout << endl;
	cout << "ZONE: " << pd.zone << endl;
	cout << "Nodes: " << pd.nodeNum << " Element:" << pd.element << " ZoneType:" << pd.zoneType << endl;
	cout << "FACENEIGHBORCONNECTIONS: " << pd.faceneighborConnections << endl;
	for (int i = 0; i < pd.variValue.size(); i++)
	{
		for (int j = 0; j < pd.variValue[0].size(); j++)
		{
			cout << pd.variValue[i][j]<<" ";
		}
		cout << endl;
	}

	for (int i = 0; i < pd.vetexPos.size(); i++)
	{
		for (int j = 0; j < pd.vetexPos[0].size(); j++)
		{
			cout << pd.vetexPos[i][j] << " ";
		}
		cout << endl;
	}

	return 0;
}
