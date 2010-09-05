from store import openStore
from utils2 import se_path_to_url
from icf.core import PSet
import sys

class BreakMeOut(Exception): pass

def sample(name,
           version=None,
           n_events = -1,
           format = ("ICF", 2),
           path="/vols/cms02/as1604/db/PhysicsUtils/SampleDB2/test_store",
	   node = "IC_DCACHE"
	):
    store = openStore(path)
    if not store.Exists(name+"/_sample_.json"):
        print "Sample '%s' not found" % name
        sys.exit(1)
    samp = store.Get(name+"/_sample_.json")
    vers = None
    if version is not None:
        if not store.Exists("%s/%s.json" % (name, version)):
            print "No version '%s' for sample '%s'" % (version,name)
            sys.exit(1)
        vers = store.Get("%s/%s.json" % (name, version))
    else:
        if not store.Exists("%s/%s.json" % (name, samp.latest)):
            print "Oops the sample specified latest version '%s' cannot be found" % samp.latest
        vers = store.Get("%s/%s.json" % (name, sampl.latest))
    ps = PSet(Format = format)
    if samp.cross_section == -1:
        ps._quiet_set("Weight", 1.0)
    else:
        ps._quiet_set("CrossSection", samp.cross_section)
    total_events = 0
    files = []
    for b in vers.blocks:
	if b["node"] != node:
	    continue
        try:
            for f in b["files"]:
                if f["events"] == -1:
                    continue
                files.append(str(se_path_to_url(f["path"], "dcap")))
                total_events += f["events"]
                if n_events != -1 and total_events >= n_events:
                    raise BreakMeOut
        except BreakMeOut:
            break
    ps._quiet_set("File", files)
    name = samp.name[1:].replace("/", "_")
    if version is not None:
	name += "_"+vers.name
    ps._quiet_set("Name", str(name))
    ps._quiet_set("Events", total_events)
    return ps
