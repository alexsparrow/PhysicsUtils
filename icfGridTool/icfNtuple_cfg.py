# Starting with a skeleton process which gets imported with the following line
from PhysicsTools.PatAlgos.patTemplate_cfg import *
process.setName_("SUSYCAF")


import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing ('standard')

#---set defaults
#  for standard options
#options.files = "somefile.root" # will select example files automatically
options.output = "SusyCAF_Tree.root"
options.secondaryOutput = "" #switch PAT-tuple output off by default
options.maxEvents = 100
#  for SusyCaf specifics
options.register('GlobalTag', "", VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, "GlobalTag to use")
options.register('JetCorrections', '900GeV', VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.string, "GlobalTaget corrections to use")
options.register('mcInfo', False, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "process MonteCarlo data")
options.register('silentMessageLogger', True, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "silence MessageLogger")
options.register('patify', True, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "run SUSYPAT on the fly")
options.register('fromRECO', True, VarParsing.VarParsing.multiplicity.singleton, VarParsing.VarParsing.varType.int, "process RECO data (else PAT is assumed)")

#---parse user input
try:
    options.parseArguments()
except:
    pass
options._tagOrder =[]

#-- Message Logger ------------------------------------------------------------
if options.silentMessageLogger:
    process.MessageLogger.categories.append('PATSummaryTables')
    process.MessageLogger.cerr.PATSummaryTables = cms.untracked.PSet(
            limit = cms.untracked.int32(-1),
            reportEvery = cms.untracked.int32(100)
    )
    process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.load('Configuration.StandardSequences.Services_cff')
process.add_( cms.Service( "TFileService",
    fileName = cms.string( options.output ),
    closeFileFast = cms.untracked.bool(True) ) 
)

#-- Input Source --------------------------------------------------------------
if options.files == []:
    if options.fromRECO:
        if options.mcInfo:
            if options.GlobalTag == "": options.GlobalTag = 'START3X_V16C::All'
	        #first file in /MinBias/Summer09-STARTUP3X_V8P_900GeV-v1/GEN-SIM-RECO
            options.files = '/store/mc/Summer09/MinBias/GEN-SIM-RECO/STARTUP3X_V8P_900GeV-v1/0011/FC9DC27A-060A-DF11-88E7-001CC47D01BA.root'
	        # Due to problem in production of LM samples: same event number appears multiple times
            process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
        else:
            if options.GlobalTag == "": options.GlobalTag = 'GR09_R_34X_V3::All'
	        #first file of run 124230 in /MinimumBias/BeamCommissioning09-SD_AllMinBias-Jan23Skim-v1/RAW-RECO
            options.files = '/store/data/BeamCommissioning09/MinimumBias/RAW-RECO/SD_AllMinBias-Jan23Skim-v1/0014/FC0BF28C-C009-DF11-94C8-0026189438E3.root'
    else:
        if options.mcInfo:
            if options.GlobalTag == "": options.GlobalTag = 'START3X_V16C::All'
            options.files = 'rfio://castorcms/?svcClass=cmscafuser&path=/castor/cern.ch/cms/store/caf/user/edelhoff/SusyCAF/examplePAT/MinBias_Summer09_MC_V00-05-10.root'
            process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
        else:
            if options.GlobalTag == "": options.GlobalTag = 'GR09_R_34X_V3::All'
            options.files = 'rfio://castorcms/?svcClass=cmscafuser&path=/castor/cern.ch/cms/store/caf/user/edelhoff/SusyCAF/examplePAT/BeamCommissioning09_MinimumBias_Jan23Skim_V00-05-10.root'

process.source = cms.Source('PoolSource', fileNames = cms.untracked.vstring(options.files) )
process.maxEvents.input = options.maxEvents

#-- Calibration tag -----------------------------------------------------------
process.GlobalTag.globaltag = options.GlobalTag

schedule = cms.Schedule()
if options.patify and options.fromRECO:
    from PhysicsTools.Configuration.SUSY_pattuple_cff import addDefaultSUSYPAT, getSUSY_pattuple_outputCommands
    #Apply SUSYPAT: Parameters are: mcInfo, HLT menu, Jet energy corrections, MC version ('31x' or '31xReReco332')
    #addDefaultSUSYPAT(process,options.mcInfo,'HLT',options.JetCorrections,None,['IC5','SC5','AK7','KT4','AK5PF','AK7PF','AK5JPT','AK5Track']) 
    addDefaultSUSYPAT(process,True,'HLT','Summer09_7TeV','31x',['IC5','SC5','AK5PF','AK5JPT','AK5Track'])
    process.jetGenJetMatch.maxDeltaR  = cms.double(0.5) #default AK5 jet
#    process.jetGenJetMatchAK7.maxDeltaR  = cms.double(0.5)
    process.jetGenJetMatchSC5.maxDeltaR  = cms.double(0.5) 
    process.jetGenJetMatchIC5.maxDeltaR  = cms.double(0.5)
 #   process.jetGenJetMatchKT4.maxDeltaR  = cms.double(0.5)
    process.jetGenJetMatchAK5PF.maxDeltaR  = cms.double(0.5) 
 #   process.jetGenJetMatchAK7PF.maxDeltaR  = cms.double(0.5)
    process.jetGenJetMatchAK5JPT.maxDeltaR  = cms.double(0.5)
    process.jetGenJetMatchAK5Track.maxDeltaR  = cms.double(0.5) 
    process.susyPat = cms.Path(process.seqSUSYDefaultSequence)
    schedule.append(process.susyPat)
    SUSY_pattuple_outputCommands = getSUSY_pattuple_outputCommands( process )

    #-- Output module configuration -----------------------------------------------
    process.out.fileName = options.secondaryOutput
    # Custom settings
    process.out.splitLevel = cms.untracked.int32(99)  # Turn on split level (smaller files???)
    process.out.overrideInputFileSplitLevels = cms.untracked.bool(True)
    process.out.dropMetaData = cms.untracked.string('DROPPED')   # Get rid of metadata related to dropped collections

    process.out.outputCommands = cms.untracked.vstring('drop *', *SUSY_pattuple_outputCommands )
#    if options.secondaryOutput == "" and hasattr(process,"out"): # remove outpath 
    del process.out
    del process.outpath

process.load('SUSYBSMAnalysis.SusyCAF.SusyCAF_nTuple_cfi')
process.p = cms.Path( (process.nTupleCommonSequence) * process.susyTree)

if options.mcInfo:
    process.p.replace( process.nTupleCommonSequence, process.nTupleCommonSequence + process.nTupleGenSequence )
else:
    process.p.replace( process.nTupleCommonSequence, process.nTupleCommonSequence + process.nTupleDataSequence )


if options.fromRECO and not options.patify:
    process.p.replace( process.nTupleCommonSequence, process.nTupleCommonSequence + process.nTupleRecoSequence )
else:
    if  options.patify:
        #little havyhanded: want too have met values which are not in SUSYPAT in those trees
         process.p.replace( process.nTupleCommonSequence, process.nTupleCommonSequence + process.nTupleRecoMetSequence )
    if options.mcInfo:
        process.p.replace( process.nTupleCommonSequence, process.nTupleCommonSequence + process.nTuplePatSequence + process.nTuplePatJetMatchedSequence)
    else:
        process.p.replace( process.nTupleCommonSequence, process.nTupleCommonSequence + process.nTuplePatSequence + process.nTuplePatJetSequence)

schedule.append(process.p)
