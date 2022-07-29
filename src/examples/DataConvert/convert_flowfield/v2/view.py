import sys
from mpi4py import MPI
import conduit
import conduit.relay as relay
import conduit.relay.mpi
import ascent

input = conduit.Node()
relay.io.load(input, 'tet_0.yaml')
# relay.io.load(input, 'tet_1.yaml')
# relay.io.load(input, 'tet_2.yaml')
# relay.io.load(input, 'tet_3.yaml')
actions = conduit.Node()
relay.io.load(actions, 'view_actions.yaml')
a = ascent.Ascent()
a.open()
a.publish(input)
a.execute(actions)
a.close()