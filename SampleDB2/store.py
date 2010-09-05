#!/usr/bin/env python

import os, os.path, sys, getpass, time, glob, shutil
try:
    import json
except ImportError:
    print "ERROR: Cannot import json module"
    sys.exit(1)

class StoreLockedError(Exception):
    def __init__(self, user, tm):
        self.user = user
        self.time = tm
class StoreNotLockedError(Exception):
    pass
class DocNotFoundError(Exception):
    pass
class JSONCancelError(Exception):
    pass

class JSONDoc:
    def __init__(self, path, write=False, new_doc = False):
        self._dict = json.load(open(path))
        self._write = write
        self._path = path
        self._new_doc = new_doc

    def __getattr__(self, name):
        if name.startswith("_"):
            return self.__dict__[name]
        else:
            if name in self._dict:
                return self._dict[name]
            else:
                raise AttributeError

    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name] = value
        else:
            if self._write:
                self._dict[name] = value
            else:
                raise JSONDocReadOnlyError
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if self._new_doc:
                os.unlink(self._path)
            if exc_type is JSONCancelError:
                return True
        if self._write:
            json.dump(self._dict, open(self._path, "w"), indent = 2)

class JSONStore:
    def __init__(self, path, lock=False, create = False, break_lock = False):
        self.path = path
        if not self.path.endswith("/"):
            self.path+="/"
        self.locked = False
        if not os.path.exists(path) and create:
            os.mkdir(path)
        if lock:
            if os.path.exists(path+"/.lock"):
                if break_lock:
                    os.unlink(path+"/.lock")
                else:
                    raise StoreLockedError(open(path+"/.lock").read(),
                                           os.path.getmtime(path+"/.lock"))
            open(path+"/.lock", "w").write(getpass.getuser())
            self.locked = True

    def Get(self, rel):
        print self.path+rel
        return JSONDoc(self.path+rel)

    def Exists(self, rel):
        return os.path.exists(self.path+rel)

    def Create(self, rel, mkdirs = True):
        if not os.path.exists(os.path.dirname(self.path+rel)) and mkdirs:
            os.makedirs(os.path.dirname(self.path+rel))
        open(self.path+rel, "w").write("{}")
        return JSONDoc(self.path+rel, True, new_doc=True)

    def Copy(self, rel, rel2):
        shutil.copyfile(self.path+rel, self.path+rel2)
        return JSONDoc(self.path+rel2, True, new_doc=True)

    def Write(self, rel):
        if not os.path.exists(self.path+rel):
            raise DocNotFoundError
        return JSONDoc(self.path+rel, True)

    def FindByName(self, name):
        flist = []
        for (path, dirs, files) in os.walk(self.path):
            for f in files:
                if f == name:
                    flist.append(os.path.relpath(path+"/"+name, self.path))
        return flist

    def Collect(self, rels, props):
        d = {}
        for k in props:
            d[k] = []
        for r in rels:
            with self.Get(r) as j:
                for k in props:
                    d[k].append(getattr(j, k, ""))
        return d

    def Glob(self, rel, ignore_under=False):
        for l in glob.glob(self.path+rel):
            if ignore_under and os.path.basename(l).startswith("_"):
                continue
            yield os.path.relpath(l, self.path)

def openStore(path, **opts):
    try:
        return JSONStore("./test_store", **opts)
    except StoreLockedError, e:
        print "JSON Store locked by user %s for %d minutes" % (e.user, (time.time() - e.time)/60)
        print "Break the lock? [n]"
        if raw_input() == "y":
            return JSONStore("./test_store", lock = True, break_lock = True)
        else:
            raise


if __name__ == "__main__":
    store = openStore("./test_store", create=True, lock=True)
    with store.Create("/EG/_sample_.json") as j:
        j.name = "/EG"
        j.cross_section = -1
        j.events = -1
        j.pt_bin = -1
    store.FindByName("_sample_.json")

