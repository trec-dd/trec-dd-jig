#/bin/bash

if [ ! -d "bin" ]; then
   mkdir bin
fi

g++ -std=c++0x -g -o bin/lemur_dd -I../include -I../contrib/lemur/include -DP_NEEDS_GNU_CXX_NAMESPACE=1 system/Lemur_DD.cpp ../contrib/lemur/obj/liblemur.a ../install/lib/libindri.a -lstdc++ -lm -lpthread -lz
