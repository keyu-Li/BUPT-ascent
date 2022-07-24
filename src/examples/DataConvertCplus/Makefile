###############################################################################
# Copyright (c) Lawrence Livermore National Security, LLC and other Ascent
# Project developers. See top-level LICENSE AND COPYRIGHT files for dates and
# other details. No copyright assignment is required to contribute to Ascent.
###############################################################################

###############################################################################
#
# Makefile for CPP Ascent examples.
#
# To build all examples:
#  env ASCENT_DIR={ascent install path} make
#
# From within an ascent install:
#  make
#
# Which corresponds to:
#
#  make ASCENT_DIR=../../../../..
#
###############################################################################

# ASCENT_DIR ?= ../../../../../
ASCENT_DIR ?=../../../../../
# See $(ASCENT_DIR)/share/ascent/ascent_config.mk for detailed linking info
include $(ASCENT_DIR)/share/ascent/ascent_config.mk

# make 'all' the default target
.PHONY: default
default: all

CXX_FLAGS = -std=c++11
INC_FLAGS = $(ASCENT_INCLUDE_FLAGS)
LNK_FLAGS = $(ASCENT_LINK_RPATH) $(ASCENT_LIB_FLAGS)

data_convert: data_convert.exe
	echo "[done building data_convert.exe]"
# data_convert.exe
data_convert.exe:
			$(CXX) $(CXX_FLAGS) $(INC_FLAGS) data_convert.cpp $(LNK_FLAGS) -o data_convert.exe

generation: test_tec.exe
	echo "[done building test_tec.exe]"
test_tec.exe:
			$(CXX) $(CXX_FLAGS) $(INC_FLAGS) test_tec.cpp $(LNK_FLAGS) -o test_tec.exe

all: data_convert.exe test_tec.exe
	 echo "[done building all]"
clean:
	 rm -f data_convert.exe
	 rm -f test_tec.exe

