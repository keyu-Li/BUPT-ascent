

===================================== script/convert_volume_tec2vtk.py ===================================== 
# 输入:
#  Volume dat文件,即: 
#       python .\convert_tecplot_to_multivtk.py volume.dat
#  输出:
#   单个的unstructuredgrid的vtk文件，输出在输入文件的位置上

# 注意：
# 位置“x, y, z”和属性“u, v, w”是必须存在的
# 属性的排列顺序要和文件中属性的排列顺序一样,不包括xyz的属性
# 如： attribute_name = ["rho", "u", "v", "w", "t", "p", "mach", "criterionQ"]
================================================================================================



==================================== script/convert_patch_tec2multivtk.py ==================================== 
# 输入:
#   Patch dat文件,即: 
#       python .\convert_tecplot_to_multivtk.py patch.dat
#   如果输出的网格错误，则再后面输入参数1，如
#       python .\convert_tecplot_to_multivtk.py patch.dat 1
# 输出:
#   多个vtk的polydata文件, 一个Zone一个vtk文件
================================================================================================