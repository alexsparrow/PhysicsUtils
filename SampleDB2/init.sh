#!/usr/bin/env bash
kinit $1@CERN.CH
aklog -cell cern.ch
voms-proxy-init