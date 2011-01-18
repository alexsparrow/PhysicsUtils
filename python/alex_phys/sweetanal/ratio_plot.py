#!/usr/bin/env python
import ROOT as r
import sys
import os.path
import os
import copy

import alex_phys.root_utils as root_utils

# Fucking hell ROOT will segv in this classif your histograms aren't SumW2ed
# BEWARE!!!!!

class RatioPlot:
    def __init__(self,
                 name,
                 hist_mc,
                 hist_data,
                 labels = [],
                 signal_names = [],
                 rebin = 20,
                 scale=1.,
                 **opts):
        self.name = name
        self._hist_mc = {}
        for name, hist in hist_mc.iteritems():
            self._hist_mc[name] = hist.Clone()
            self._hist_mc[name].Rebin(rebin)
            self._hist_mc[name].Scale(scale)
        self._hist_data = hist_data.Clone()
        self._hist_data.Rebin(rebin)
        self._signal_names = signal_names
        self._conf = RatioPlot.default_config()
        self.auto_hist_style()
        self._conf.update(opts)
        self._labels = copy.deepcopy(labels)


    @staticmethod
    def default_config():
        return {
            "canvas_width" : 1200,
            "canvas_height" : 1200,
            "data_marker_style" : 20,
            "data_line_width" : 3,
            "data_line_color" : 1,
            "data_fill_color" : 1,
            "data_fill_color" : 1,

            "error_line_color" : r.kTeal + 3,
            "error_marker_color" : r.kAzure + 6,
            "error_fill_color" : r.kAzure+6,
            "error_line_width" : 3,

            "central_line_color" : r.kTeal + 3,
            "central_marker_color" : r.kTeal + 3,
            "central_fill_color": 0,
            "central_line_width" : 3,

            "total_line_color" : r.kAzure + 2,
            "total_line_width" : 3,
            "total_fill_color" : r.kAzure + 2,
            "total_fill_style" : 3245,

            "leg_shadow_color" : 0,
            "leg_border_size" : 0,
            "leg_fill_style" : 4100,
            "leg_fill_color" : 0,
            "leg_line_color" : 0,
            "leg_loc" : "left",
            "leg_pos" : (0.12, 0.55, 0.6, 0.88),

            "margin_left" : None,
            "margin_right" : None,
            "margin_top" : None,
            "margin_bottom" : 0.15,

            "hist_xmin" : 0,
            "hist_xmax" : 500,
            "hist_ymax_factor" : 1.5,
            "hist_xmax_factor" : 1.1,
            "hist_xfixed" : False,
            "hist_yfixed" : False,
            "hist_xrange" : None,
            "hist_ytitle" : "",
            "hist_add_title_label" : True,
            "ratio_ytitle" : "data / mc",
            "unity_line_wdith" : 2,
            "unity_line_color" : 2,
            "unity_fill_color" : 2,
            "unity_fill_style" : 3002
            }

    @staticmethod
    def min_x(h):
        for i in range(1, h.GetNbinsX()+1):
            if h.GetBinContent(i) != 0:
                return h.GetBinLowEdge(i)

    @staticmethod
    def max_x(h):
        for i in reversed(range(1, h.GetNbinsX()+1)):
            if h.GetBinContent(i) > 5:
                return h.GetBinLowEdge(i) + h.GetBinWidth(i)

    @staticmethod
    def max_y(h):
        return h.GetMaximum()


    def auto_hist_style(self):
        cols = [r.kBlue, r.kGreen, r.kRed, r.kOrange, r.kMagenta, r.kYellow]
        for idx, (name, hist) in enumerate(self._hist_mc.iteritems()):
            self._conf["%s_line_width" % name] = 3
            self._conf["%s_line_color" % name] = cols[idx]

    def stylise(self, ob, name):
        style_funcs = {
            "shadow_color" : "SetShadowColor",
            "border_size" : "SetBorderSize",
            "line_color" : "SetLineColor",
            "line_width" : "SetLineWidth",
            "fill_color" : "SetFillColor",
            "fill_style" : "SetFillStyle",
            "marker_color" : "SetMarkerColor",
            "marker_style" : "SetMarkerStyle"}
        for k, v in style_funcs.iteritems():
            if "%s_%s" % (name, k) in self._conf:
                getattr(ob, v)(self._conf["%s_%s" % (name, k)])


    def plot(self, path,  mkdirs = True):
        leg = r.TLegend(*self._conf["leg_pos"])

        leg.SetTextSize(0.03)
        #leg = r.TLegend(0.5, 0.4, 0.95, 0.85)
        self.stylise(leg, "leg")
        c = r.TCanvas("c_%s" % self.name,
                      "canvas_%s" % self.name,
                      self._conf["canvas_width"],
                      self._conf["canvas_height"])
        mainpad = r.TPad("", "", 0.01, 0.25, 0.99, 0.99)
        #mainpad.SetLogy()
        mainpad.SetNumber(1)
        if self._conf["margin_bottom"] is not None:
            mainpad.SetBottomMargin(self._conf["margin_bottom"])
        if self._conf["margin_left"] is not None:
            mainpad.SetLeftMargin(self._conf["margin_left"])
        mainpad.Draw()
        ratiopad = r.TPad("", "", 0, 0.05, 0.99, 0.26)
        ratiopad.SetNumber(2)
        if self._conf["margin_bottom"] is not None:
            ratiopad.SetBottomMargin(self._conf["margin_bottom"]) # was 0.3
        if self._conf["margin_left"] is not None:
            ratiopad.SetLeftMargin(self._conf["margin_left"])
        ratiopad.Draw()
        c.cd(1)
        self.stylise(self._hist_data, "data")
        draw = [(k,v) for k,v in self._hist_mc.iteritems()]
        total = None
        for name, hist in draw:
            self.stylise(hist, name)
            leg.AddEntry(hist, name, "LP")
            if not name in self._signal_names:
                if total is None:
                    total = hist.Clone()
                else:
                    total.Add(hist)
        central = total.Clone()
        error = total.Clone()
        self.stylise(error, "error")
        self.stylise(central, "central")
        self.stylise(total, "total")
        leg.AddEntry(total, "Standard Model", "Lf")

        min_x = min([self._conf["hist_xmin"],
                     self.min_x(total), self.min_x(self._hist_data)])
        max_x = min([
            self._conf["hist_xmax"],
            max([self.max_x(total),
                 self.max_x(self._hist_data)])])*self._conf["hist_xmax_factor"]
        max_y =  self._conf["hist_ymax_factor"]*max([self.max_y(total),
                                                     self.max_y(self._hist_data)])
        if self._conf["hist_xrange"] is not None:
            (min_x, max_x) = self._conf["hist_xrange"]
        if not self._conf["hist_xfixed"]:
            error.GetXaxis().SetRangeUser(min_x, max_x)
        if not self._conf["hist_yfixed"]:
                error.GetYaxis().SetRangeUser(0.001, max_y)

        error.SetTitle("")
        error.GetXaxis().SetTitle(self.name)
        error.GetYaxis().SetTitle(self._conf["hist_ytitle"])

        error.Draw("hist")
        central.Draw("hist same")
        total.Draw("9E2same")
        for name, hist in self._hist_mc.iteritems():
            hist.Draw("hist same")
        self._hist_data.Draw("9SAMEP")
        if self._conf["hist_add_title_label"]:
            self._labels.append((0.05, 0.95, self.name))
        for x, y, text in self._labels:
            l = r.TLatex()
            l.SetNDC()
            l.DrawLatex(x, y, text)
        error.Draw("axis same")
        c.cd(1).Update()
        leg.Draw()
        c.cd(2)
        # Draw unity
        unity = r.TBox(error.GetBinLowEdge(error.GetXaxis().GetFirst()),
                       0.89,
                       error.GetBinLowEdge(error.GetXaxis().GetLast())+error.GetBinWidth(error.GetXaxis().GetLast()),
                       1.11)

        self.stylise(unity, "unity")
        unity.Draw()
        # Draw ratio

        bottom = total.Clone()
        top = self._hist_data.Clone()
        top.GetYaxis().SetTitle(self._conf["ratio_ytitle"])
        #top.GetXaxis().SetTitle("")
        top.SetTitle("")
        top.Divide(bottom)
        top.SetTitleSize(0.1, "XYZ")
        top.SetTitleOffset(0.44, "X")
        top.SetTitleOffset(0.3, "Y")
        top.SetLabelSize(0.06, "XY")
        if not self._conf["hist_xfixed"]:
            top.GetXaxis().SetRangeUser(min_x, max_x)
        top.GetYaxis().SetRangeUser(0, 2)
        top.SetLabelSize(0.15, "XYZ")
        top.SetTitleSize(1.05, "X")
        top.SetNdivisions(4, "Y")
        top.Draw()
        unity.Draw()
        #sys.exit()
        c.Update()
        if not os.path.exists(os.path.dirname(path)):
            if mkdirs:
                os.makedirs(os.path.dirname(path))
            else:
                raise IOError("Directory '%s' does not exist (mkdirs: disabled)"
                              % os.path.dirname(path))
        c.SaveAs(path)
