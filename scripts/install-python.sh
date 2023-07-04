#!/bin/bash

PY_DIR_NAME=Python-3.11.2
PATH_DIR=`pwd`

# INSTALL PYTHON
wget https://www.python.org/ftp/python/3.11.2/Python-3.11.2.tar.xz
tar -xf $PY_DIR_NAME.tar.xz
cd $PY_DIR_NAME && ./configure --prefix=$PATH_DIR/python && make altinstall -j4 && cd $PATH_DIR
rm -rf $PATH_DIR/$PY_DIR_NAME*
