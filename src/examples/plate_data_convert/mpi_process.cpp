#include <iostream>
#include <fstream>
#include <vector>
#include <iomanip>
#include <string>
#include <cstring>
#include <algorithm>
#include <map>

#include <mpi.h>

#include <ascent.hpp>
#include <conduit_blueprint.hpp>
#include <conduit_relay.hpp>
#include <conduit_relay_mpi.hpp>

using namespace std;
int comm_size=4;

int main() {
    int rank = 0;
	MPI_Init(NULL,NULL);
	MPI_Comm_size(MPI_COMM_WORLD, &comm_size);
	//cout << comm_size << endl;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);

	
	conduit::Node n;

    if(rank == 0) {
        conduit::Node subNodes[comm_size];
        for(int i = 0; i < comm_size; ++i) {
            string cur = "mesh_" + to_string(i) + ".json";
            conduit::relay::io::load(cur, subNodes[i]);
        }
        n = subNodes[0];
		for(int t = 1; t < comm_size; ++t) {
			conduit::relay::mpi::send_using_schema(subNodes[t], t, 0, MPI_COMM_WORLD);
			//subNodes[t].print();
		}
	} else {
		conduit::relay::mpi::recv_using_schema(n, 0, 0, MPI_COMM_WORLD);
	}

    ascent::Ascent a;
	conduit::Node ascent_opts;
	ascent_opts["mpi_comm"] = MPI_Comm_c2f(MPI_COMM_WORLD);
	ascent_opts["runtime/type"] = "ascent";
	ascent_opts["actions_file"] = "mesh_filter.yaml";
    //ascent_opts["runtime/backend"] = "openmp";
	a.open(ascent_opts);
	conduit::Node actions;
	a.publish(n);
	a.execute(actions);
	a.close();



	MPI_Finalize();

    return 0;
}

