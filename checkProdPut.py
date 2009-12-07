#! /usr/bin/env python
import sys
import glob
from optparse import OptionParser

def normalize(mstr):
    ary=mstr.split("+")
    if len(ary)==0:
        return mstr.strip()
    else:
        ostr=ary[0].strip()
        for ar in ary[1:]:
            ostr+="+"+ar.strip()
        return ostr

def parse_produces(mstr):
    mstr=mstr[len("produces"):]
    prod_type=mstr[mstr.find("<")+1:mstr.rfind(">")].lstrip().rstrip()
    prod=normalize(mstr[mstr.find("(")+1:mstr.rfind(")")])
    return (prod,prod_type)

def parse_put(mstr):
    put_name=mstr[mstr.find("(")+1:mstr.find(",")].lstrip().rstrip()
    mstr=mstr[mstr.find("(")+1:mstr.rfind(")")]
    return (normalize(mstr.split(",")[1]),put_name)

def parse_type(mstr):
    mstr=mstr[:mstr.find("(")]
    var_type=mstr[mstr.find("<")+1:mstr.rfind(">")].lstrip().rstrip()
    var_name=mstr[mstr.rfind(">")+1:].lstrip().rstrip()
    return (var_name,var_type)

def diff_dict(d1,d2):
    diffs=[]
    for (key1,val1) in d1.iteritems():
        found=False
        for (key2,val2) in d2.iteritems():
            if val1==val2:
                found=True
                break
        if not found:
		diffs.append(key1)
    return diffs

def parse_file(fname,quiet,check_types=True):
    produces={}
    puts={}
    types={}
    put_var={}
    produces_type={}
    i=0
    for l in open(fname,'r'):
        i+=1
        line=l.lstrip().rstrip()
        if line.startswith("produces"):
            (var,t)=parse_produces(line)
            produces[i]=var
            produces_type[var]=t
        elif line.startswith("iEvent.put"):
            (name,var)=parse_put(line[len("iEvent.put"):])
            puts[i]=name
            put_var[name]=var
        elif line.startswith("event.put"):
            (name,var)=parse_put(line[len("event.put"):])
            puts[i]=name
            put_var[name]=var
        elif line.startswith("std::auto_ptr"):
            (var2,t)=parse_type(line[len("std::auto_ptr"):])
            types[var2]=t

    diff1=diff_dict(produces,puts)
    diff2=diff_dict(puts,produces)
    bad_types=False
    if not quiet:
        print "For file: %s" % fname
        for d in diff1:
            print "Unamtched produces on line %d: " % d
            print " > %s" % produces[d]
        for d in diff2:
            print "Unmatched put on line %d: " % d
            print " > %s" % puts[d]
    if  (len(diff1)+len(diff2))==0:
        if check_types:
            for (k,v) in produces_type.iteritems():
                if not types[put_var[k]]==v:
                    if not quiet:
                        print "Wrong type %s: %s != %s" % (put_var[k],
                                                       types[put_var[k]],v)
                        bad_types=True
    elif not quiet:
        print " + %d differences found" % (len(diff1)+len(diff2))
    return (len(diff1)+len(diff2))==0 and not (bad_types and check_types)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-q","--quiet",action="store_true",default=False)
    parser.add_option("-c","--check-types",action="store_true",default=False)
    (options, args) = parser.parse_args()
    good=True
    count=0
    for arg in args:
        for f in glob.glob(arg):
            good=good and parse_file(f,options.quiet,options.check_types)
            count+=1
    print "Processed %d files" % count
    if good:
        print "All tests passed OK"
    else:
        print "Problems found"

