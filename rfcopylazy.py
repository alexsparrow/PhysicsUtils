#!/usr/bin/env python
import os
import sys  
import subprocess

def copyf(src,dest):
    cmd=["rfcp",src,dest]
    print cmd
    subprocess.call(cmd)

def hadd(out_file,files):
    cmd=["hadd",out_file]+files
    print cmd
    subprocess.call(cmd)
    
if len(sys.argv)<3:
    print "Error: too few arguments"
    print "Usage: rfcopy.py [path] [output file] [[pattern]]"
    print "e.g. rfcopy.py $CASTOR_HOME/test/ wjets.root wjets"
    print "will copy all files '$CASTOR_HOME/test/wjets*' to current directory"
    print "and merge them into file wjets.root"
    sys.exit(0)

if len(sys.argv)==3:
    pattern=""
else:
    pattern=sys.argv[3]

path=sys.argv[1]
out_file=sys.argv[2]

#p=open(sys.argv[1])
p=os.popen("rfdir %s" % path)
files=[]
for line in p:
    fields=line.split()
    if ( fields[8].startswith(pattern) or pattern=="") and (fields[0][0]!="d"):
        files.append(fields[8])
for f in files:
    if not path.endswith("/"):
        path+="/"
    if not os.path.exists(f):
        copyf(path+f,"./")
    else:
        print "Skipping file %s since it already exists" % f
hadd(out_file,files)
