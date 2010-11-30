def setup_root():
    import ROOT as r
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = r.kWarning
    r.gROOT.SetStyle("Plain") #To set plain bkgds for slides
    r.gStyle.SetTitleBorderSize(0)
    r.gStyle.SetCanvasBorderMode(0)
    r.gStyle.SetCanvasColor(0)#Sets canvas colour white
    r.gStyle.SetOptStat(1110)#set no title on Stat box
    r.gStyle.SetLabelOffset(0.001)
    r.gStyle.SetLabelSize(0.05)
    r.gStyle.SetLabelSize(0.05,"Y")#Y axis
    r.gStyle.SetTitleSize(0.06)
    r.gStyle.SetTitleW(0.7)
    r.gStyle.SetTitleH(0.07)
    r.gStyle.SetOptTitle(1)
    r.gStyle.SetOptStat(0)
    r.gStyle.SetAxisColor(1, "XYZ");
    r.gStyle.SetStripDecimals(r.kTRUE);
    r.gStyle.SetTickLength(0.03, "XYZ");
    r.gStyle.SetNdivisions(510, "XYZ");
    r.gStyle.SetPadTickX(1);
    r.gStyle.SetPadTickY(1);
    r.gStyle.SetLabelColor(1, "XYZ");
    r.gStyle.SetLabelFont(42, "XYZ");
    r.gStyle.SetLabelOffset(0.007, "XYZ");
    r.gStyle.SetLabelSize(0.05, "XYZ");
    r.gStyle.SetHatchesLineWidth(3)

def tdr_hist_style(h):
    h.SetTitleFont(42, "XYZ")
    h.SetTitleSize(0.06, "XYZ")
    h.SetTitleOffset(0.2, "X")
    h.SetTitleOffset(0.35, "Y")
    h.SetLabelFont(42, "XYZ")
    h.SetLabelOffset(0.007, "XYZ")
    h.SetLabelSize(0.05, "XYZ")

def mkhists(**kwargs):
    import ROOT
    d = {}
    for k,v in kwargs.iteritems():
        d[k] = ROOT.TH1D(k, "", *v)
    return d

def ensure_tfile(path):
    import utils
    import ROOT
    utils.ensure_dir(path)
    return ROOT.TFile(path, "recreate")
