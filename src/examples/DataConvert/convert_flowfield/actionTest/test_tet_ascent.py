# %%
# sys.path.append("home/hoody/spack/opt/spack/linux-ubuntu18.04-skylake/gcc-7.5.0/conduit-0.8.3-k6sdyyhkcdpoyeuapjbrt77fgzdoj7dt")
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
conduit.relay.io.load(actions, "clampingValue.yaml")
print(actions)
a.execute(actions)

# %%
# in jupyter
# ascent.jupyter.AscentViewer(a).show()

# %%
# close ascent
a.close()


