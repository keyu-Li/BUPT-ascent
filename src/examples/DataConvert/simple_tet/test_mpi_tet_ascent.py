import sys
from mpi4py import MPI
import conduit
import conduit.relay as relay
import conduit.relay.mpi
import ascent.mpi


comm_id   = MPI.COMM_WORLD.py2f()
comm_rank = relay.mpi.rank(comm_id)
comm_size = relay.mpi.size(comm_id)
mpi_options = conduit.Node()
mpi_options["mpi_comm"] = comm_id 
mpi_options["runtime/type"] = "ascent"
mpi_options["runtime/backend"] = "openmp"
input = conduit.Node()
input['coordsets/coords/type'] = "explicit"
input['state/domain_id'] = comm_rank
if comm_rank == 0:
    # input['coordsets/coords/values/x'] = [0.0, 10.0, 0.0, 0.0, -10.0, 0.0, 0.0]
    # input['coordsets/coords/values/y'] = [0.0, 0.0, 10.0, 0.0, 0.0, -10.0, 0.0]
    # input['coordsets/coords/values/z'] = [0.0, 0.0, 0.0, 10.0, 0.0, 0.0, -10.0]
    input['coordsets/coords/values/x'] = [0.0, 10.0, 0.0, 0.0]
    input['coordsets/coords/values/y'] = [0.0, 0.0, 10.0, 0.0]
    input['coordsets/coords/values/z'] = [0.0, 0.0, 0.0, 10.0]
    input['topologies/mesh/type'] = 'unstructured'
    input['topologies/mesh/coordset'] = 'coords'
    input['topologies/mesh/elements/shape'] = "tet"
    input['topologies/mesh/elements/connectivity'] = [0,1,2,3]
    input['fields/field_1/association'] = "element"
    input['fields/field_1/topology'] = "mesh"
    input['fields/field_1/volume_dependent'] = "false"
    input['fields/field_1/values'] = [0.0]
else:
    # input['coordsets/coords/values/x'] = [0.0, 10.0, 0.0, 0.0, -10.0, 0.0, 0.0]
    # input['coordsets/coords/values/y'] = [0.0, 0.0, 10.0, 0.0, 0.0, -10.0, 0.0]
    # input['coordsets/coords/values/z'] = [0.0, 0.0, 0.0, 10.0, 0.0, 0.0, -10.0]
    input['coordsets/coords/values/x'] = [0.0, -10.0, 0.0, 0.0]
    input['coordsets/coords/values/y'] = [0.0, 0.0, -10.0, 0.0]
    input['coordsets/coords/values/z'] = [0.0, 0.0, 0.0, -10.0]
    input['topologies/mesh/type'] = 'unstructured'
    input['topologies/mesh/coordset'] = 'coords'
    input['topologies/mesh/elements/shape'] = "tet"
    input['topologies/mesh/elements/connectivity'] = [0,1,2,3]
    input['fields/field_1/association'] = "element"
    input['fields/field_1/topology'] = "mesh"
    input['fields/field_1/volume_dependent'] = "false"
    input['fields/field_1/values'] = [10.0]

a = ascent.mpi.Ascent()
a.open(mpi_options)
a.publish(input)

actions = conduit.Node()
conduit.relay.io.load(actions, "simple_action.yaml")

print(actions)
a.execute(actions)

ascent.jupyter.AscentViewer(a).show()

a.close()
    