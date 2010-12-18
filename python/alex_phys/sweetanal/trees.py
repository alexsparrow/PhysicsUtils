#!/usr/bin/env python
import ROOT as r
import os.path, copy, array
import sys

from alex_phys.utils import progress

# Simple TTree runner
# No TChain support yet
# Inspired by wrappedChain from supy by Burt Betchart and Ted Laird

class BranchHelper:
    def __init__(self,
                 branchName,
                 leafName,
                 tree):
        self._name = leafName or branchName
#        self._value = copy.deepcopy(getattr(tree, leafName or branchName))
        self._value = copy.deepcopy(getattr(tree, branchName))
        def root_type():
            if type(self._value) == int:
                return array.array("l", [0])
            elif type(self._value) == long:
                return array.array("l", [0])
            elif type(self._value) == float:
                return array.array("d", [0.0])
            elif str(type(self._value)) == "<type 'ROOT.PyUIntBuffer'>":
                return array.array("i", [0]*256)
            elif str(type(self._value)) == "<type 'ROOT.PyDoubleBuffer'>":
                return array.array("d", [0]*256)
            elif str(type(self._value)) == "<type 'ROOT.PyFloatBuffer'>":
                return array.array("f", [0]*256)
            else:
                return r.AddressOf(self._value)
        self._address = root_type()
        self._scalar = (type(self._address) == array.array and len(self._address) == 1)
        if type(self._address) == array.array and len(self._address) > 1:
            self._value = self._address
        self._branch = tree.GetBranch(branchName)
        self._branch.SetAddress(self._address)
        self._entry = -1

    def Update(self, entry):
        self._entry = entry
        self._branch.GetEntry(entry)
        if self._scalar:
            self._value = self._address[0]

class TreeHelper:
    def __init__(self,
                 fname,
                 dname,
                 tname,
                 use_cache = False,
                 profile = False,
                 debug = False,
                 print_every = 1000,
                 ignore_branches = []):
        if not os.path.exists(fname):
            raise IOError("Specified file doesnt not exist: '%s'" % fname)
        self._name = fname.split("/")[-1].split(".root")[0]
        self._file = r.TFile(fname)
        self._dir = self._file.Get(dname)
        self._tree = self._dir.Get(tname)
        self._tree.GetEntry(0)
        self._branches = {}
        self._use_cache = use_cache
        self._profile = profile
        self._debug  = debug
        self._print_every = print_every
        if self._use_cache:
            self._tree.SetCacheSize(10000000)
            self._tree.SetCacheLearnEntries(5)

	# Minor workaround to a bug that seems to be in ROOT 5.27/06
        branch_list = self._tree.GetListOfBranches()
        for i in range(self._tree.GetNbranches()):
            b = branch_list[i]
            branchName = b.GetName()
            if branchName in ignore_branches:
                continue
            leafName = b.GetListOfLeaves().At(0).GetName()
            if leafName == "_": leafName = None
            if self._debug:
                print "Creating branch %s (%s)" % (branchName, leafName)
            self._branches[branchName] = BranchHelper(branchName, leafName, self._tree)

    def __del__(self):
        if self._profile:
            print "[TreeHelper] Read %d bytes with %d calls" % (
                self._file.GetBytesRead(),
                self._file.GetReadCalls())

    def __iter__(self):
        self._entry = -1
        self._last_entry = self._tree.GetEntries()
        return self

    def next(self):
        self._entry += 1
        if self._entry == self._last_entry:
            if self._print_every is not None:
                sys.stdout.write(
                    progress(self._entry, self._last_entry, text = self._name, term="\n"))
                sys.stdout.flush()
            raise StopIteration
        if self._print_every is not None and self._entry % self._print_every == 0:
            sys.stdout.write(progress(self._entry, self._last_entry, text = self._name))
            sys.stdout.flush()
        return self

    def __getattr__(self, name):
        if name in self._branches:
            if self._branches[name]._entry != self._entry:
                self._branches[name].Update(self._entry)
            return self._branches[name]._value
        else:
            return self.__dict__[name]
