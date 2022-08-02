Add
===========

- read_data_split.cpp 数据划分程序
- mpi_process.cpp 并行ascent程序
- makefile_serial
- makefile_mpi

Compile
===========

- 修改makefile_serial内的依赖路径为本地
- make clean
- make
- ./read_data_split plate.dat

- 修改makefile_mpi内的依赖路径为本地
- make clean
- make
- ./mpi_process

Description
==============================================

- 目标数据plate.dat
- 读取坐标和场，读取面和cell的相邻关系
- 拷贝至conduit数据
- 数据进行划分
- 读取划分数据，mpi并行处理渲染
