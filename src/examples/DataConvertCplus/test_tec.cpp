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
#include"ascent.hpp"
#include<conduit_relay.hpp>
using namespace std;
using namespace conduit;
using namespace ascent;
int main()
{

    Node mesh;
    conduit::relay::io::load("tet1.yaml",mesh);

    Ascent a;
    a.open();
    a.publish(mesh);

    Node actions;
    conduit::relay::io::load("test_tet_ascent.yaml",actions);
    cout<<actions.to_yaml()<<endl;
    a.execute(actions);
    
    a.close();
    return 0;
}