#!/usr/bin/env python
from ROOT import *
import logging
import itertools
import sys
import os
import errno

# TODO:
# * The property mapping need to be improved
# * Initialise multiple plots at once similar to ROOTFiles
# * Add multiple convenience functions for Plots and Virtuals
# * The Plots multiplexer should support an arbitrary list of ones not to expand
# * The plots multiplexer should allow mapping of properties such as title x axis etc.

legend_centre =  (0.35, 0.7, 0.65, 0.95)
leg_top_right = (0.65, 0.7, 0.95, 0.95)
def isdict(ob):
    try:
        ob.items()
    except AttributeError:
        return False
    return True

def add_histos(draw):
    h = draw[0]._root.Clone()
    for i in draw:
        h.Add(i._root)
    return h

def norm_hist(x):
    x._root.Scale(1/x._root.Integral())

def splash_screen():
    print "=================================================================="
    print "/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\\"
    print "|XXXXXXXXX        XXXXXX XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX|"
    print "|XXXXXXXXX XXXXXX XXXXXX XXXXXXXXXXXX     XXXXXX       XXXXXXXXXX|"
    print "|XXXXXXXXX XXXXXX XXXXXX XXXXXXXXXXXX XXX XXXXXXXXX XXXXXXXXXXXXX|"
    print "|XXXXXXXXX        XXXXXX XXXXXXXXXXXX XXX XXXXXXXXX XXXXXXXXXXXXX|"
    print "|XXXXXXXXX XXXXXXXXXXXXX XXXXXXXXXXXX XXX XXXXXXXXX XXXXXXXXXXXXX|"
    print "|XXXXXXXXX XXXXXXXXXXXXX       XXXXXX     XXXXXXXXX XXXXXXXXXXXXX|"
    print "|XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX      XXXX|"
    print "|XXXXX XXXXX XXXXXX      XXXXXX     XXX     XXX     XXX XXXX XXXX|"
    print "|XXXX X XXX XX XXXX XXXXXXX   X XXXXXXXXX XXXXX XXXXXXX      XXXX|"
    print "|XXX XXX X XXXX XXX    XXXXX XX    XXXXXX XXXXX   XXXXX XXXXX XXX|"
    print "|XX XXXXX XXXXXX XX XXXXXXXX XXXXXX XXXXX XXXXX XXXXXXX XXXXXX XX|"
    print "|X XXXXXXXXXXXXXX X      XX   XX    XXXXX XXXXX     XXX XXXXXXX X|"
    print "\XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/"
    print "=================================================================="
    print "               P  L  O  T     M  E  I  S  T  E  R                 "
    print "=================================================================="

class PlotMeister(object):
    def __init__(self, name, **options):
        self.name=name
        self.input_files={}
        self.plots={}
        self.groups={}
        self._cache={}
        self.virtuals={}
        gROOT.SetStyle("Plain")
        if "batch" in options:
            self.SetBatch(options["batch"])

        splash_screen()
        log_levels = {"debug":logging.DEBUG, "warning":logging.WARNING,
                   "info":logging.INFO }
        FORMAT = "[%(levelname)s] %(name)s (%(funcName)s, l%(lineno)d) : %(message)s"
        if "logging" in options:
            logging.basicConfig(level=log_levels[options["logging"]],
                                format=FORMAT)
        else:
            logging.basicConfig(level=logging.WARNING,
                                format=FORMAT)
        self._log = logging.getLogger("PlotMeister")

        if "subdir" in options:
            self._sub_dir = True
        else:
            self._sub_dir = False

    def AddFile(self, name, f):
        self._log.info("Registering file %s", name)
        if name in self.input_files:
            raise IndexError("File %s already registere" % name)
        self.input_files[name]=f

    def AddPlot(self, name, p):
        self._log.info("Registering plot %s", name)
        if name in self.plots:
            raise IndexError("Plot %s already registered" % name)
        self.plots[name]=p
        p._hook_up(self)

    def AddGroup(self, name, group):
        self._log.info("Registering group %s",name)
        if name in self.groups:
            raise IndexError("Group %s already registered" % group)
        self.groups[name]=group

    def AddVirtual(self, name, virtual):
        self._log.info("Registering virtual %s",name)
        if name in self.virtuals:
            raise IndexError("Virtual %s already registered" % name)
        self.virtuals[name]=virtual
        virtual._hook_up(self)

    def SetBatch(self,batch):
        ROOT.gROOT.SetBatch(batch)

    def __iadd__(self, other):
        if getattr(other, '__iter__', False):
            l= list(other)
        else:
            l=[other]
        for i in l:
            if isinstance(i, RootFile):
                self.AddFile(i.name, i)
            elif isinstance(i, Plot):
                self.AddPlot(i.name, i)
            elif isinstance(i, Group):
                self.AddGroup(i.name, i)
            elif isinstance(i, Virtual):
                self.AddVirtual(i.name, i)
        return self

    def ParseURL(self, url):
        self._log.debug("Calling ParseURL: %s",url)
        groups = []
        for idx in range(len(url)):
            if url[idx]=="#" and (idx==0 or url[idx-1]!="\\") and url[idx+1]=="{":
                end=url.find("}",idx+1)
                if end < 0:
                    raise ValueError("Invalid group specification in url %s at %d. No '}' found" % (url,start))
                group_name=url[idx+2:end]
                if not group_name in self.groups:
                    raise ValueError("Invalid group name in url %s: %s" % (url,group_name))
                if not group_name in groups:
                    self._log.debug("Adding group %s", group_name)
                    groups.append(group_name)
        group_repl = []
        urls=[]
        for g in groups:
            group_repl.append(self.groups[g]._group.keys())
        self._log.debug("Group %s", group_repl)
        for i in itertools.product(*group_repl):
            url2=url
            for k in range(len(i)):
                self._log.debug("Doing replacement %s with %s", groups[k], self.groups[groups[k]]._group[i[k]])
                url2=url2.replace("#{%s}" % groups[k], self.groups[groups[k]]._group[i[k]])
            self._log.debug("Generated URL %s" % url)
            urls.append((url2, i))
        return (urls, groups)

    def LoadURL(self, url):
        self._log.debug("Calling LoadURL for url '%s'", url)
        if url in self._cache:
            return self._cache[url].Clone()
        else:
            if url.startswith("!"):
                return self.virtuals[url[1:]].Get()
            fname = url.split("/")[0]
            if not fname in self.input_files:
                raise NameError("File %s not registered." % fname)
            self._cache[url]=self.input_files[fname].GetObject("/".join(url.split("/")[1:]))
            return self._cache[url].Clone()

    def GetOutputPath(self):
         if self._sub_dir:
            try:
                self._log.debug("Creating subdir '%s'" % self.name)
                os.makedirs("./%s" % self.name)
            except OSError as exc:
                if exc.errno == errno.EEXIST:
                    pass
                else: raise
            return "./%s/" % self.name
         else: return "./"

    def PlotPNG(self):
        for (name,p) in self.plots.iteritems():
            self._log.info("Outputting PNG for plot '%s'", name)
            p.Draw()
            p._root.SaveAs(self.GetOutputPath()+p.GetOutputName()+".png")

    def PlotROOT(self,file_name=None):
        if file_name is None:
            fname=self.name+".root"
        else:
            fname = file_name
        self._log.info("Outputting ROOT file for '%s'", file_name)
        out=TFile(self.GetOutputPath()+fname,"recreate")
        out.cd()
        for (name, p) in self.plots.iteritems():
            p.Draw()
            p._root.Write()
            self._log.info("Writing plot %s to ROOT file", name)


class RootFile(object):
    def __init__(self,name,fname):
        self._root = TFile(fname)
        self.name = name
        self._log = logging.getLogger("RootFile")

    def GetObject(self,path):
        self._log.debug("Calling GetObject for path '%s'", path)
        split = path.split("/")
        # try:
        d = self._root
        for s in split[:-1]:
            oldd =d
            self._log.debug("Traversing into directory '%s'", s)
            d = d.Get(s)
            try:
                if not d.IsFolder(): raise ReferenceError
            except ReferenceError:
                print "=============== Hint ================="
                print "Other contents in directory:"
                oldd.ls()
                print "======================================"
                raise NameError("Path %s in %s not found for file %s" % (s,
                                                                         path,
                                                                         self.name))
        try:
            return d.Get(split[-1]).Clone()

        except ReferenceError:
             raise NameError("Path %s in %s not found for file %s" % (split[-1],
                                                                      path,
                                                                      self.name))
class ROOTObject(object):
    def __init__(self, ob, groups, group_repl, idx):
        self._root = ob
        self._groups = groups
        self._group_repl = group_repl
        self._idx = idx

class Plot(object):
    def __init__(self, name, **options):
        self._meister = None
        self.name = name
        self._inputs = []
        self._drawables = []
        self._options={}
        self._log = logging.getLogger("Plot")
        if "draw" in options:
            self._options["draw"]=options["draw"]
        else:
            self._options["draw"]="hist"
        if "inputs" in options:
            self._inputs.extend(options["inputs"])
        if "default" in options:
            self._options["default"] = options["default"]
        else:
            self._options["default"] = Prop( Draw = "hist",
                                             LCol = 1,
                                             LStyle = 0,
                                             FCol = 0,
                                             FStyle = 1001,
                                             LWidth = 1,
                                             Idx = 9999)
        if "mapping" in options:
            self._options["mapping"] = options["mapping"]
        if "x_range" in options:
            self._options["x_range"] = options["x_range"]
        if "legend" in options:
            self._options["legend"] = options["legend"]
        else:
            self._options["legend"] = None

        if "legend_fill_style" in options:
            self._options["legend_fill_style"] = options["legend_fill_style"]
        else:
            self._options["legend_fill_style"] =0
        if "legend_pos" in options:
            self._options["legend_pos"] = options["legend_pos"]
        else:
            self._options["legend_pos"] = (0.3, 0.7, 0.6, 0.9)
        if "margins" in options:
            self._options["margins"] = options["margins"]
        if "title" in options:
            self._options["title"] = options["title"]
        if "show_stats" in options:
            self._options["show_stats"] = options["show_stats"]
        else:
            self._options["show_stats"] = False
        if "logy" in options:
            self._options["logy"] = options["logy"]
        else:
            self._options["logy"] = False
        if "sweet_max" in options:
            self._options["sweet_max"] = options["sweet_max"]
        else:
            self._options["sweet_max"] = False
        if "sweet_scale" in options:
            self._options["sweet_scale"] = options["sweet_scale"]
        else:
            self._options["sweet_scale"] = 1.1
        if "rebin" in options:
            self._options["rebin"] = options["rebin"]

        if "prep_func" in options:
            self._options["prep_func"] = options["prep_func"]
        else:
            self._options["prep_func"] = None
        if "draw" in options:
            self._options["draw"] = options["draw"]
        if "x_title" in options:
            self._options["x_title"] = options["x_title"]
        if "y_title" in options:
            self._options["y_title"] = options["y_title"]

    def _hook_up(self, meister):
        self._meister = meister

    def _fetch_inputs(self):
        self._log.debug("Fetch inputs called")
        self._drawables = []
        if self._meister is None:
            raise ValueError("No link to PlotMeister")
        idx = 0
        for i in self._inputs:
            (urls, groups) = self._meister.ParseURL(i)
            for u in urls:
                self._drawables.append(ROOTObject(self._meister.LoadURL(u[0]),
                                                  groups,
                                                  u[1],idx))
                idx+=1

    def GetOutputName(self):
        return self.name

    def GetSortIndex(self,i):
        return self.GetProperty("Idx",i)

    def GetDrawOptions(self, i):
        opt = self.GetProperty("Draw", i)
        if "draw" in self._options:
            opt+=" %s" % self._options["draw"]
        return opt

    def Draw(self):
        self._log.debug("Draw called")
        self._fetch_inputs()
        self._log.debug("Drawing %d drawables", len(self._drawables))
        self._root = TCanvas(self.name)
        if self._options["logy"]:
            self._root.SetLogy()
        if self._options["margins"]:
                self._root.SetLeftMargin(self._options["margins"][0])
                self._root.SetTopMargin(self._options["margins"][1])
                self._root.SetRightMargin(self._options["margins"][2])
                self._root.SetBottomMargin(self._options["margins"][3])
        for i in self._drawables:
            i._root.SetLineColor(self.GetProperty("LCol",i))
            i._root.SetFillColor(self.GetProperty("FCol",i))
            i._root.SetLineStyle(self.GetProperty("LStyle",i))
            i._root.SetFillStyle(self.GetProperty("FStyle",i))
            i._root.SetLineWidth(self.GetProperty("LWidth", i))
            if "rebin" in self._options:
                i._root.Rebin(self._options["rebin"])
            if "x_range" in self._options:
                self.ApplyXRange(i)
            if "title" in self._options:
                i._root.SetTitle(self._options["title"])
            if "x_title" in self._options:
                i._root.GetXaxis().SetTitle(self._options["x_title"])
            if "y_title" in self._options:
                i._root.GetYaxis().SetTitle(self._options["y_title"])
            if self._options["prep_func"] is not None:
                self._options["prep_func"](i)
            i._root.SetStats(self._options["show_stats"])
        self._drawables.sort(key=self.GetSortIndex)
        if self._options["sweet_max"]:
            m=self._options["sweet_scale"]*max([h._root.GetMaximum() for h in self._drawables])
            for h in self._drawables:
                h._root.SetMaximum(m)

        if len(self._drawables):
            self._drawables[0]._root.Draw(self.GetDrawOptions(self._drawables[0]))
        for i in self._drawables[1:]:
            self._log.debug("Drawing drawable %d: %s", i._idx,self._options["draw"])
            i._root.Draw("%s same" % self.GetDrawOptions(i))
        if self._options["legend"] is not None:
            self._legend = TLegend( self._options["legend_pos"][0],
                                    self._options["legend_pos"][1],
                                    self._options["legend_pos"][2],
                                    self._options["legend_pos"][3] )

            self._legend.SetFillStyle(self._options["legend_fill_style"])
            for i in self._drawables:
                self._log.debug("Adding %s to drawables",
                                 self.GetProperty("Txt", i))
                self._legend.AddEntry(i._root, self.GetProperty("Txt",i),self._options["legend"])
            self._legend.Draw()
        if len(self._drawables):
            self._drawables[0]._root.Draw("axis same")

    def GetMap(self, i):
        self._log.debug("GetMap called for %s", i._group_repl)
        if len(i._groups) == 0:
            self._log.debug("No groups found - mapping should be array")
            try:
                return self._options["mapping"][i._idx]
            except:
                if len(self._drawables) == 1:
                    return self._options["mapping"]
                else:
                    raise TypeError("Dont be weird")

        elif isdict(self._options["mapping"]):
            self._log.debug("Mapping is dict")
            if i._group_repl in self._options["mapping"]:
                return self._options["mapping"][i._group_repl]
            else:
                if len(i._group_repl)==1 and i._group_repl[0] in self._options["mapping"]:
                        return self._options["mapping"][i._group_repl[0]]
                else:
                    self._log.debug("Could not find mapping for group %s" % str(i._group_repl))
                    return None
        elif getattr(self._options["mapping"], '__iter__', False) and len(i._groups) == 1:
            self._log.debug("Mapping is iterable")
            if len(self._options["mapping"] >= len(i._group_repl)):
                return self._options["mapping"][i._group_repl[0]]
            else:
                self._log.debug("No mapping found")
                return None
        else:
            raise TypeError("Illegal mapping type")

    def GetProperty(self, name, i):
        self._log.debug("GetProperty called for %s, %s", name, i._group_repl)
        m = self.GetMap(i)
        if m is not None and m.has(name):
            self._log.debug("Got value %s for property %s", str(m.get(name)),name)
            return m.get(name)
        elif name=="Txt":
            return "/".join(i._group_repl)
        else:
            self._log.debug("Falling back to defaults for %d , %s", i._idx, name)
            return self._options["default"].get(name)

    def ApplyXRange(self,i):
        i._root.GetXaxis().SetRangeUser(self._options["x_range"][0], self._options["x_range"][1])

def ROOTFiles(name,**options):
    f = []
    fgroup = {}
    for (k,v) in options.iteritems():
        f.append(RootFile(k,v))
        fgroup[k]=k
    if name is not None:
        f.append(Group(name,**fgroup))
    return f

class Virtual(object):
    def __init__(self, name, func, inputs):
        self.name = name
        self._func = func
        self._meister = None
        self._drawables = []
        self._inputs = inputs
        self._log = logging.getLogger("Virtual")

    def _hook_up(self, meister):
        self._meister = meister

    def _fetch_inputs(self):
        self._log.debug("Fetch inputs called")
        self._drawables = []
        if self._meister is None:
            raise ValueError("No link to PlotMeister")
        idx = 0
        for i in self._inputs:
            (urls, groups) = self._meister.ParseURL(i)
            for u in urls:
                self._drawables.append(ROOTObject(self._meister.LoadURL(u[0]),
                                                  groups,
                                                  u[1],idx))
                idx+=1

    def Get(self):
        self._fetch_inputs()
        self._root = self._func(self._drawables)
        return self._root

class Prop(object):
    def __init__(self, **args):
        self._dict = args
        for (k, v) in self._dict.iteritems():
            if not k in ["LCol", "FCol", "MCol", "LStyle",
                         "FStyle", "MStyle", "Txt", "Draw", "LWidth",
                         "Idx"]:
                raise NameError("Unrecognised property: %s" % k)

    def get(self, val):
        if not val in self._dict:
            raise NameError("Unrecognised property: %s" % val)
        return self._dict[val]

    def has(self, val):
        return val in self._dict

class Group(object):
    def __init__(self, name, *it, **args):
        self.name = name
        self._group = {}
        if len(args): self._group = args.copy()
        for i in it:
            for (n,gi) in i._group.iteritems():
                if n in self._group:
                    raise NameError("Trying to add duplicate name")
                else: self._group[n] = gi

if __name__=="__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    p = PlotMeister("MVA")
    p.SetBatch(True)
    p += RootFile("hello","./eWPol_Control_QCD_BCtoE_80to170.root")
    p += Group("ewpol", pre="RECO_ElPolPlots_PreMHT", post="RECO_ElPolPlots_PostMHT")
    p += Group("ecalhcal", ecal="MC_RECO_Ecal", hcal="MC_RECO_Hcal")
    p += Plot("sweet_plots",
              inputs = ["hello/#{ewpol}/#{ecalhcal}"],
              mapping = { ("pre", "ecal") : Prop( Draw = "P", LCol = kBlack, Txt = "ECAL - Pre MHT" ),
                          ("pre", "hcal") : Prop( LCol = kRed, Txt = "HCAL - Pre MHT"),
                          ("post", "ecal") : Prop( LCol = kGreen, Txt = "ECAL - Post MHT"),
                          ("post", "hcal") : Prop( LCol = kBlue, Txt = "HCAL - Post MHT") },
              legend = "L",
              legend_pos = (0.65, 0.7, 0.95, 0.95),
#              title = "Comparison of calorimeters",
              logy = True,
              x_range = (0, 1),
              margins = (0.1, 0.05, 0.05, 0.1)
              )
    p.PlotPNG() # Output a single file sweet_plots.png
    p.PlotROOT("sweet_plots2.root") # Produces an output ROOT file


