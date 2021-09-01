#!/bin/bash

#Delete old kit.
rm submission/PTSPExec.zip
rm -rf submission/ptsp_exec/

#Create directory structure
mkdir submission/ptsp_exec
mkdir submission/ptsp_exec/maps
mkdir submission/ptsp_exec/maps/StageZ
mkdir submission/ptsp_exec/src
mkdir submission/ptsp_exec/src/controllers  
mkdir submission/ptsp_exec/src/controllers/greedy 
mkdir submission/ptsp_exec/src/controllers/random
mkdir submission/ptsp_exec/src/controllers/lineofsight
mkdir submission/ptsp_exec/src/controllers/keycontroller
mkdir submission/ptsp_exec/src/framework
mkdir submission/ptsp_exec/src/framework/core
mkdir submission/ptsp_exec/src/framework/graph
mkdir submission/ptsp_exec/src/framework/utils
mkdir submission/ptsp_exec/src/framework/sec
mkdir submission/ptsp_exec/src/wox
mkdir submission/ptsp_exec/src/wox/serial

#Copy contents
#cp maps/all/* submission/ptsp_exec/maps/StageZ/
cp maps/league2/ptsp* submission/ptsp_exec/maps/StageZ/
cp out/production/Framework/controllers/greedy/*.class submission/ptsp_exec/src/controllers/greedy/
cp out/production/Framework/controllers/lineofsight/*.class submission/ptsp_exec/src/controllers/lineofsight/
cp out/production/Framework/controllers/random/*.class submission/ptsp_exec/src/controllers/random/
cp out/production/Framework/controllers/keycontroller/*.class submission/ptsp_exec/src/controllers/keycontroller/
cp out/production/Framework/framework/core/*.class submission/ptsp_exec/src/framework/core/
cp out/production/Framework/framework/graph/*.class submission/ptsp_exec/src/framework/graph/
cp out/production/Framework/framework/utils/*.class submission/ptsp_exec/src/framework/utils/
cp out/production/Framework/framework/sec/*.class submission/ptsp_exec/src/framework/sec/
cp out/production/Framework/framework/Submit.class submission/ptsp_exec/src/framework/
cp out/production/Framework/framework/core/Exec.class submission/ptsp_exec/src/framework/core/
cp out/production/Framework/framework/ExecSync.class submission/ptsp_exec/src/framework/
cp out/production/Framework/framework/ExecReplay.class submission/ptsp_exec/src/framework/
cp out/production/Framework/framework/ExecFromData.class submission/ptsp_exec/src/framework/
cp out/production/Framework/wox/serial/*.class submission/ptsp_exec/src/wox/serial/
cp lib/jdom.jar submission/ptsp_exec/src/
cp lib/xercesImpl.jar submission/ptsp_exec/src/

#Create zip
cd submission/ptsp_exec/
zip -r ../PTSPExec.zip *
