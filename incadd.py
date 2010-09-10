#!/usr/bin/env python
import sys, json, shutil, subprocess, os.path
from optparse import OptionParser

def usage():
    print "Usage %s <outfile> <infile1> <infile2> ..." % sys.argv[0]
    sys.exit(1)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-l","--loop",action="store_true",
                      default=False, help='Carry on hadding')

    (options, args) = parser.parse_args()
    if len(args) < 2:
        usage()
    finished = False
    while not finished:
        finished = True
        ofile = args[1]
        ifiles = [f for f in args[2:]]
        json_path = args[1].replace("root","json")

        if not os.path.exists(json_path):
            open(json_path,"w").write('{ "added" : []}')
        jadded = json.load(open(json_path,"r"))
        afiles = []
        for f in ifiles:
            if f == ofile:
                continue
            if os.path.getsize(f) > 50000:
                if not any([unicode(f) == a for a in jadded["added"]]):
                    action = "HADD"
                    afiles.append(f)
                else:
                    action = "IGNORE"
            else:
                action = "TOOSMALL"
                if options.loop:
                    finished = False
            print "File {0:<40} {1:<10}".format(f, action)
        if len(afiles) == 0:
            print "Up to date!"
            sys.exit(0)
        else:
            if os.path.exists(ofile):
                print "Moving previous iteration out of the way"
                shutil.move(ofile, "_"+ofile)
            print "%d new files found" % len(afiles)
            params = ["hadd", ofile]
            if os.path.exists("_"+ofile):
                params.append("_"+ofile)
            params.extend(afiles)
            p = subprocess.Popen(params)
            (o, e) = p.communicate()
            if p.returncode == 0:
                jadded["added"].extend(afiles)
                json.dump(jadded, open(json_path,"w"))
                print "Done"
        if os.path.exists("_"+ofile):
            os.unlink("_"+ofile)


