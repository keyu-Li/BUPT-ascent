# %%
import conduit
import conduit.blueprint
import ascent

import numpy as np

# %%
mesh = conduit.Node()
conduit.relay.io.load(mesh, "tet.yaml")
print(mesh)


# %%
a = ascent.Ascent()
a.open()
a.publish(mesh)

actions = conduit.Node()
conduit.relay.io.load(actions, "test_tet_ascent.yaml")
print(actions)
a.execute(actions)

# %%
# in jupyter
ascent.jupyter.AscentViewer(a).show()

# %%
# close ascent
a.close()


