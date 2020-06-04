######################################
#### Modified version of https://github.com/DAZSLE/ZPrimePlusJet/blob/Hbb/fitting/PbbJet/limit.py
#### Simple way to run it:
#### - GoodnessOfFit: python bkgEstTests.py -M GoodnessOfFit -d ttHbb_combined.root -t 100 -a (or saturated or KS)
#### - Bias: python ../../bkgEstTests.py -M Bias -d ../mc_msd100to150_msdbin5_pt2bin_polyDegs22/ttHbb_combined.root -t 100 --datacard-alt ../biasTest_mc_msd100to150_msdbin5_pt2bin_polyDegs22/ttHbb_combined.root  --seed 64832687 --rMin -30 --rMax 30 --toysFrequentist
#### - FTest: python ../../bkgEstTests.py -M FTest --datacard-alt ../mc_msd100to150_msdbin5_pt2bin_polyDegs22/ttHbb_combined.root -t 100 -d ttHbb_combined.root  --seed 424371915
######################################
#!/usr/bin/env python
import ROOT as r,sys,math,array,os
from optparse import OptionParser

#from tools import *
import glob

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

def end():
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = raw_input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]

def plotgaus(iFName,injet,iLabel,options):
    lCan   = r.TCanvas(str(iLabel),str(iLabel),500,400)
    lCan.SetLeftMargin(0.12)
    lCan.SetBottomMargin(0.15)
    lCan.SetTopMargin(0.12)
    if type(iFName)==type("string"):
        lFile = r.TFile(iFName)
        lTree = lFile.Get("tree_fit_sb")
    elif type(iFName)==type([]):
        lTree = r.TChain("tree_fit_sb")
        for f in iFName: lTree.Add(f)


    lH = r.TH1D('h_bias','h_bias',50,-4,4)
    lH_1 = r.TH1D('h_bias_1','h_bias',50,-4,4)
    lH_2 = r.TH1D('h_bias_2','h_bias',50,-4,4)
    lTree.Project('h_bias_1','(%s-%s)/%sLoErr'% (options.poi,injet,options.poi),
                  '%s>%s&&(%sHiErr+%s)<%i&&(%s-%sLoErr)>%i'%(options.poi,injet,
                                                             options.poi,options.poi,float(options.rMax)-1,
                                                             options.poi,options.poi,float(options.rMin)+1))
    lTree.Project('h_bias_2','(%s-%s)/%sHiErr'% (options.poi,injet,options.poi),
                  '%s<%s&&(%sHiErr+%s)<%i&&(%s-%sLoErr)>%i'%(options.poi,injet,
                                                             options.poi,options.poi,float(options.rMax)-1,
                                                             options.poi,options.poi,float(options.rMin)+1))
    lH = lH_1
    lH.Add(lH_2)
    print 'Tree Entries = %s , pull entries = %s'%(lTree.GetEntriesFast(),lH.GetEntries())
    print lH.GetMean()
    print lH.GetBinCenter(lH.GetMaximumBin())
    gaus_func = r.TF1("gaus_func","gaus(0)",-3,3)
    #gaus_func = r.TF1("gaus_func","gaus(0)",-2.5,2.5)
    gaus_func.SetParameter(0,20)
    gaus_func.SetParameter(1,0)
    gaus_func.SetParameter(2,1)
    lH.Fit(gaus_func,"mler")
    gaus_func.Draw("same")
    muLabel = {'r': '#mu', 'r_z': '#mu_{Z}'}
    lH.GetXaxis().SetTitle("Bias (#hat{%s} - %s)/#sigma_{%s}"%(muLabel[options.poi], muLabel[options.poi], muLabel[options.poi]))
    lH.GetYaxis().SetTitle("Pseudoexperiments")
    lH.GetYaxis().SetTitleOffset(0.8)
    gaus_func.SetLineColor(r.kRed)
    gaus_func.SetLineStyle(2)
    lH.SetMaximum(2.*lH.GetMaximum())
    lH.Draw("ep")
    gaus_func.Draw("sames")
    lH.Draw("ep sames")


    tLeg = r.TLegend(0.5,0.6,0.89,0.89)
    tLeg.SetLineColor(r.kWhite)
    tLeg.SetLineWidth(0)
    tLeg.SetFillStyle(0)
    tLeg.SetTextFont(42)
    if options.poi=='r':
        tLeg.AddEntry(lH,"#splitline{Pseudodata}{Hbb(%s GeV) #mu=%s}"%(options.mass, options.r),"lep")
    elif options.poi=='r_z':
        tLeg.AddEntry(lH,"#splitline{Pseudodata}{Zbb(%s GeV) #mu_{Z}=%s}"%('90', options.r),"lep")
    tLeg.AddEntry(gaus_func,"#splitline{Gaussian fit}{mean = %+1.2f, s.d. = %1.2f}"%(gaus_func.GetParameter(1),gaus_func.GetParameter(2)),"l")
    tLeg.Draw("same")


    l = r.TLatex()
    l.SetTextAlign(11)
    l.SetTextSize(0.06)
    l.SetTextFont(62)
    l.SetNDC()
    l.DrawLatex(0.12,0.91,"CMS")
    l.SetTextSize(0.05)
    l.SetTextFont(52)
    l.DrawLatex(0.23,0.91,"Preliminary")
    l.SetTextFont(42)
    l.DrawLatex(0.70,0.91,"%.1f fb^{-1} (13 TeV)"%options.lumi)
    l.SetTextFont(52)
    l.SetTextSize(0.045)


    l.DrawLatex(0.15,0.82,'gen. pdf = %s(n_{#rho}=%i,n_{p_{T}}=%i)'%(options.pdf2, options.NR2,options.NP2))
    l.DrawLatex(0.15,0.75,'fit pdf = %s(n_{#rho}=%i,n_{p_{T}}=%i)'%(options.pdf1, options.NR1,options.NP1))

    lCan.Modified()
    lCan.Update()
    lCan.SaveAs(options.odir+'/'+iLabel+".png")
    #lCan.SaveAs(options.odir+'/'+iLabel+".pdf")
    #lCan.SaveAs(options.odir+'/'+iLabel+".C")
    #end()


def plotftest(iToys,iCentral,prob,iLabel,options):
    lCan   = r.TCanvas(str(iLabel),str(iLabel),800,600)
    lCan.SetLeftMargin(0.12)
    lCan.SetBottomMargin(0.12)
    lCan.SetRightMargin(0.1)
    lCan.SetTopMargin(0.1)

    if options.method=='FTest':
        lH = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+1)
        lH_cut = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+1)
    elif options.method=='GoodnessOfFit' and options.algo=='saturated':
        lH = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+100)
        lH_cut = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+100)
    elif options.method=='GoodnessOfFit' and options.algo=='KS':
        lH = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+0.05)
        lH_cut = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+0.05)

    if options.method=='FTest':
        lH.GetXaxis().SetTitle("F = #frac{-2log(#lambda_{1}/#lambda_{2})/(p_{2}-p_{1})}{-2log#lambda_{2}/(n-p_{2})}")
        lH.GetXaxis().SetTitleSize(0.025)
        lH.GetXaxis().SetTitleOffset(2)
        lH.GetYaxis().SetTitle("Pseudodatasets")
        lH.GetYaxis().SetTitleOffset(0.85)
    elif options.method=='GoodnessOfFit' and options.algo=='saturated':
        lH.GetXaxis().SetTitle("-2log#lambda")
        lH.GetYaxis().SetTitle("Pseudodatasets")
        lH.GetYaxis().SetTitleOffset(0.85)
    elif options.method=='GoodnessOfFit' and options.algo=='KS':
        lH.GetXaxis().SetTitle("KS")
        lH.GetYaxis().SetTitle("Pseudodatasets")
        lH.GetYaxis().SetTitleOffset(0.85)
    for val in iToys:
        lH.Fill(val)
        if val > iCentral:
            lH_cut.Fill(val)
    lH.SetMarkerStyle(20)
    lH.Draw("pez")
    lLine  = r.TArrow(iCentral,0.25*lH.GetMaximum(),iCentral,0)
    lLine.SetLineColor(r.kBlue+1)
    lLine.SetLineWidth(2)

    lH_cut.SetLineColor(r.kViolet-10)
    lH_cut.SetFillColor(r.kViolet-10)
    lH_cut.Draw("histsame")

    if options.method=='FTest':
        fdist = r.TF1("fDist", "[0]*TMath::FDist(x, [1], [2])", 0,max(max(iToys),iCentral)+1)
        fdist.SetParameter(0,lH.Integral()*((max(max(iToys),iCentral)+1)/70.))
        fdist.SetParameter(1,options.p2-options.p1)
        fdist.SetParameter(2,options.n-options.p2)
        fdist.Draw('same')
        #lH.Fit(fdist,'mle')
    elif options.method=='GoodnessOfFit' and options.algo=='saturated':
        chi2_func = r.TF1('chisqpdf','[0]*ROOT::Math::chisquared_pdf(x,[1])',0,max(max(iToys),iCentral)+100)
        chi2_func.SetParameter(0,lH.Integral())
        chi2_func.SetParameter(1,50)
        chi2_func.Draw('same')
        lH.Fit(chi2_func,"mle")
    lH.Draw("pezsame")
    lLine.Draw()

    tLeg = r.TLegend(0.6,0.6,0.89,0.89)
    tLeg.SetLineColor(r.kWhite)
    tLeg.SetLineWidth(0)
    tLeg.SetFillStyle(0)
    tLeg.SetTextFont(42)
    tLeg.AddEntry(lH,"toy data (ntoys = %i)"%len(iToys),"lep")
    tLeg.AddEntry(lLine,"observed = %.1f"%iCentral,"l")
    tLeg.AddEntry(lH_cut,"p-value = %.2f"%(1-prob),"f")
    if options.method=='FTest':
        #tLeg.AddEntry(fdist,"f-dist fit, ndf = (%.1f #pm %.1f, %.1f #pm %.1f) "%(fdist.GetParameter(1),fdist.GetParError(1),fdist.GetParameter(2),fdist.GetParError(2)),"l")
        tLeg.AddEntry(fdist,"F-dist, ndf = (%.0f, %.0f) "%(fdist.GetParameter(1),fdist.GetParameter(2)),"l")
    elif options.method=='GoodnessOfFit' and options.algo=='saturated':
        tLeg.AddEntry(chi2_func,"#chi^{2} fit, ndf = %.1f #pm %.1f"%(chi2_func.GetParameter(1),chi2_func.GetParError(1)),"l")

    tLeg.Draw("same")

    l = r.TLatex()
    l.SetTextAlign(11)
    l.SetTextSize(0.06)
    l.SetTextFont(62)
    l.SetNDC()
    l.DrawLatex(0.12,0.91,"CMS")
    l.SetTextSize(0.05)
    l.SetTextFont(52)
    if options.isData:
        l.DrawLatex(0.23,0.91,"Preliminary")
    else:
        l.DrawLatex(0.23,0.91,"Simulation")
    l.SetTextFont(42)
    l.DrawLatex(0.70,0.91,"%.1f fb^{-1} (13 TeV)"%options.lumi)
    l.SetTextFont(52)
    l.SetTextSize(0.045)



    lCan.SaveAs(options.odir+'/'+iLabel+".png")
    lCan.SaveAs(options.odir+'/'+iLabel+".pdf")
    #lCan.SaveAs(options.odir+'/'+iLabel+".C")
    #end()

def nllDiff(iFName1,iFName2):
    lFile1 = r.TFile.Open(iFName1)
    lTree1 = lFile1.Get("limit")
    lFile2 = r.TFile.Open(iFName2)
    lTree2 = lFile2.Get("limit")
    lDiffs=[]
    for i0 in range(0,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lTree2.GetEntry(i0)
        diff = 2*(lTree1.nll-lTree1.nll0)-2*(lTree2.nll-lTree2.nll0)
        lDiffs.append(diff)
    return lDiffs


def fStat(iFName1,iFName2,p1,p2,n):
    lFile1 = r.TFile.Open(iFName1)
    lTree1 = lFile1.Get("limit")
    lFile2 = r.TFile.Open(iFName2)
    lTree2 = lFile2.Get("limit")
    lDiffs=[]
    for i0 in range(0,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lTree2.GetEntry(i0)
        if lTree1.limit-lTree2.limit>0:
            F = (lTree1.limit-lTree2.limit)/(p2-p1)/(lTree2.limit/(n-p2))
            print i0, ":", lTree1.limit, "-", lTree2.limit, "=", lTree1.limit-lTree2.limit, "F =", F
            lDiffs.append(F)
    print "number of toys with F>0: %s / %s"%(len(lDiffs),lTree1.GetEntries())
    return lDiffs

def goodnessVals(iFName1):
    lFile1 = r.TFile.Open(iFName1)
    lTree1 = lFile1.Get("limit")
    lDiffs=[]
    for i0 in range(0,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lDiffs.append(lTree1.limit)
    return lDiffs

################################################################
def ftest(base,alt,ntoys,iLabel,options):
    if not options.justPlot:
        baseName = base.split('/')[-1].replace('.root','')
        altName  = alt.split('/')[-1].replace('.root','')
        os.chdir( options.odir )
        exec_me('combine -M GoodnessOfFit %s  --rMax %s --rMin %s --algorithm saturated -n %s --freezeParameters %s'% (base, options.rMax,options.rMin,baseName, options.freezeNuisances),options.dryRun)
        exec_me('mv higgsCombine%s.GoodnessOfFit.mH120.root base1.root'%baseName, options.dryRun)
        exec_me('combine -M GoodnessOfFit %s --rMax %s --rMin %s --algorithm saturated  -n %s --freezeParameters %s' % (alt,options.rMax,options.rMin,altName, options.freezeNuisances),options.dryRun)
        exec_me('mv higgsCombine%s.GoodnessOfFit.mH120.root base2.root'%altName, options.dryRun)
        exec_me('combine -M GenerateOnly %s --rMax %s --rMin %s --toysFrequentist -t %i --expectSignal %f --saveToys -n %s --freezeParameters %s -s %s' % (base,options.rMax,options.rMin,ntoys,options.r,baseName,options.freezeNuisances,options.seed),options.dryRun)
        #exec_me('cp higgsCombine%s.GenerateOnly.mH120.%s.root %s/'%(baseName,options.seed,options.odir))
        exec_me('combine -M GoodnessOfFit %s --rMax %s --rMin %s -t %i --toysFile %s/higgsCombine%s.GenerateOnly.mH120.%s.root --algorithm saturated -n %s --freezeParameters %s -s %s' % (base,options.rMax,options.rMin,ntoys,options.odir,baseName,options.seed,baseName, options.freezeNuisances,options.seed),options.dryRun)
        exec_me('mv higgsCombine%s.GoodnessOfFit.mH120.%s.root toys1_%s.root'%(baseName,options.seed,options.seed),options.dryRun)
        exec_me('combine -M GoodnessOfFit %s --rMax %s --rMin %s -t %i --toysFile %s/higgsCombine%s.GenerateOnly.mH120.%s.root --algorithm saturated -n %s --freezeParameters %s -s %s' % (alt,options.rMax,options.rMin,ntoys,options.odir,baseName,options.seed,altName, options.freezeNuisances,options.seed),options.dryRun)
        exec_me('mv higgsCombine%s.GoodnessOfFit.mH120.%s.root toys2_%s.root'%(altName,options.seed,options.seed),options.dryRun)
    if options.dryRun: sys.exit()
    nllBase=fStat("%s/base1.root"%options.odir,"%s/base2.root"%options.odir,options.p1,options.p2,options.n)
    if not options.justPlot:
        print "Using these toys input %s/toys1_%s.root and %s/toys2_%s.root"%(options.odir,options.seed,options.odir,options.seed)
        nllToys=fStat("%s/toys1_%s.root"%(options.odir,options.seed),"%s/toys2_%s.root"%(options.odir,options.seed),options.p1,options.p2,options.n)
    else:
        nToys1 = len(glob.glob(os.path.join(options.odir,"toys1_*.root")))
        nToys2 = len(glob.glob(os.path.join(options.odir,"toys2_*.root")))
        if nToys1==nToys2:
            print "Found %s toy files"%nToys1
            nllToys=[]
            for i in range(0,nToys1):
                if not os.path.exists("%s/toys1_%s.root"%(options.odir,i)):
                    print "cannot find job %i, skipping it"%i
                else:
                    print "="*20 +" job %i "%i+"="*20
                    nllToys += (fStat("%s/toys1_%s.root"%(options.odir,i),"%s/toys2_%s.root"%(options.odir,i),options.p1,options.p2,options.n))
        else:
            print "Using these toys input %s/toys1.root and %s/toys2.root"%(options.odir,options.odir)
            nllToys=fStat("%s/toys1.root"%(options.odir),"%s/toys2.root"%(options.odir),options.p1,options.p2,options.n)
    lPass=0
    for val in nllToys:
        #print val,nllBase[0]
        if nllBase[0] > val:
            lPass+=1
    pval = 1
    if len(nllToys)>0:
        pval = float(lPass)/float(len(nllToys))
        print "FTest p-value",pval
    plotftest(nllToys,nllBase[0],pval,iLabel,options)
    return float(lPass)/float(len(nllToys))

##############################################################
def goodness(base,ntoys,iLabel,options):
    '''Run combine GoodnessOfFit. First quanfities GOF for the single data (or MC) experiment from the combine datacard. Then, throws pseudoexperiements based on the experiment of the datacard and finally quantifies GOF for each experiment. If justPlot option, creates nice plots of the test'''

    if not options.justPlot:
        # --fixedSignalStrength %f  --freezeParameters tqqnormSF,tqqeffSF
        exec_me('combine -M GoodnessOfFit %s  --rMax 20 --rMin -20 --algorithm %s -n %s --freezeParameters %s'% (base,options.algo,base.split('/')[-1].replace('.root',''),options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GoodnessOfFit.mH120.root %s/goodbase.root'%(base.split('/')[-1].replace('.root',''),options.odir),options.dryRun)
        exec_me('combine -M GenerateOnly %s --rMax 20 --rMin -20 --toysFrequentist -t %i --expectSignal %f --saveToys -n %s --freezeParameters %s' % (base,ntoys,options.r,base.split('/')[-1].replace('.root',''),options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GenerateOnly.mH120.123456.root %s/'%(base.split('/')[-1].replace('.root',''),options.odir),options.dryRun)
        exec_me('combine -M GoodnessOfFit %s --rMax 20 --rMin -20 -t %i --toysFile %s/higgsCombine%s.GenerateOnly.mH120.123456.root --algorithm %s -n %s --freezeParameters %s' % (base,ntoys,options.odir,base.split('/')[-1].replace('.root',''),options.algo,base.split('/')[-1].replace('.root',''),options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GoodnessOfFit.mH120.123456.root %s/goodtoys.root'%(base.split('/')[-1].replace('.root',''),options.odir),options.dryRun)
    if options.dryRun: sys.exit()
    nllBase=goodnessVals('%s/goodbase.root'%options.odir)
    nllToys=goodnessVals('%s/goodtoys.root'%options.odir)
    lPass=0
    for val in nllToys:
        if nllBase[0] > val:
            lPass+=1
    print "GoodnessOfFit p-value",float(lPass)/float(len(nllToys))
    plotftest(nllToys,nllBase[0],float(lPass)/float(len(nllToys)),iLabel,options)
    return float(lPass)/float(len(nllToys))

##############################################################
def bias(base,alt,ntoys,mu,iLabel,options):
    '''Generates pseudoexperiments based on the alternative function, and then fits each pseudoexperiment with the nominal function.'''

    toysOptString = ''
    if options.toysFreq:
        toysOptString='--toysFrequentist'
    elif options.toysNoSyst:
        toysOptString='--toysNoSystematics'

    if not options.justPlot:
        if options.scaleLumi>0:     ### ALE: I dont understand why we need this.
            ##### Get snapshots with lumiscale=1 for Toy generations ########
            snapshot_base ="combine -M MultiDimFit  %s  -n .saved "%(alt)
            snapshot_base += " -t -1 --algo none --saveWorkspace %s "%(toysOptString)
            snapshot_base += " --freezeParameters %s "%(options.freezeNuisances)
            snapshot_base += " --setParameterRange r=%s,%s "%(options.rMin,options.rMax)
            snapshot_base += " --setParameters lumiscale=1,%s"%options.setParameters
            exec_me(snapshot_base,options.dryRun)

        if options.scaleLumi>0:
            ##### Generation toys from snapshots , setting lumiscale to 10x########
            generate_base ="combine -M GenerateOnly -d higgsCombine.saved.MultiDimFit.mH120.root --snapshotName MultiDimFit "
            generate_base +=" --setParameters lumiscale=%s "%(options.scaleLumi)
        else:
            generate_base ="combine -M GenerateOnly %s %s "%(alt, toysOptString)
        generate_base += " -t %s -s %s "%(ntoys,options.seed)
        generate_base += " --saveToys -n %s --redefineSignalPOIs %s"%(iLabel,options.poi)
        generate_base += " --freezeParameters %s "%(options.freezeNuisances)
        generate_base += " --setParameterRange r=%s,%s "%(options.rMin,options.rMax)
        generate_base += " --setParameters %s "%(options.setParameters)
        generate_base += " --trackParameters  'rgx{.*}'"
        exec_me(generate_base,options.dryRun)

        # generate and fit in one step:
        #fitDiag_base = "combine -M FitDiagnostics %s  -n %s  --redefineSignalPOIs %s" %(base,iLabel,options.poi)
        # generate and fit separately:
        fitDiag_base = "combine -M FitDiagnostics %s --toysFile higgsCombine%s.GenerateOnly.mH120.%s.root -n %s  --redefineSignalPOIs %s" %(base,iLabel,options.seed,iLabel,options.poi)
        fitDiag_base += ' --robustFit 1 --saveNLL  --saveWorkspace --setRobustFitAlgo Minuit2,Migrad'
        fitDiag_base += ' -t %s -s %s '%(ntoys,options.seed)
        fitDiag_base += " --freezeParameters %s "%(options.freezeNuisances)
        fitDiag_base += " --setParameterRange r=%s,%s "%(options.rMin,options.rMax)
        if options.scaleLumi>0:
            fitDiag_base += " --setParameters %s,lumiscale=%s " %(options.setParamters,options.scaleLumi)
        else:
            fitDiag_base += " --setParameters %s "%(options.setParameters)
        fitDiag_base += " %s "%(toysOptString)

        exec_me(fitDiag_base ,options.dryRun)
        exec_me('mv  fitDiagnostics%s.root %s/biastoys_%s_%s.root'%(iLabel, options.odir, iLabel, options.seed), options.dryRun)
    if options.dryRun: sys.exit()
    plotgaus("%s/biastoys_%s_%s.root"%(options.odir,iLabel,options.seed),mu,"pull"+iLabel+"_"+str(options.seed),options)

##############################################################
def fit(base,options):
    exec_me('combine -M MaxLikelihoodFit %s -v 2 --freezeParameters tqqeffSF,tqqnormSF --rMin=-20 --rMax=20 --saveNormalizations --plot --saveShapes --saveWithUncertainties --minimizerTolerance 0.001 --minimizerStrategy 2'%base)
    exec_me('mv mlfit.root %s/'%options.odir)
    exec_me('mv higgsCombineTest.MaxLikelihoodFit.mH120.root %s/'%options.odir)

def limit(base):
    exec_me('combine -M Asymptotic %s  ' % base)
    exec_me('mv higgsCombineTest.Asymptotic.mH120.root limits.root')
    #exec_me('mv higgsCombineTest.Asymptotic.mH120.123456.root limits.root')

def plotmass(base,mass):
    exec_me('combine -M MaxLikelihoodFit %s --saveWithUncertainties --saveShapes' % base)
    exec_me('cp ../plot.py .')
    #exec_me('cp ../tdrstyle.py .')
    exec_me('python plot.py --mass %s' % str(mass))

def setup(iLabel,mass,iBase,iRalph):
    #exec_me('mkdir %s' % iLabel)
    exec_me('sed "s@XXX@%s@g" card_%s_tmp2.txt > %s/card_%s.txt' %(mass,iBase,iLabel,iBase))
    exec_me('cp %s*.root %s' % (iBase,iLabel))
    exec_me('cp %s*.root %s' % (iRalph,iLabel))
    #os.chdir (iLabel)

def setupMC(iLabel,mass,iBase):
    exec_me('mkdir %s' % iLabel)
    exec_me('sed "s@XXX@%s@g" mc_tmp2.txt > %s/mc.txt' %(mass,iLabel))
    exec_me('cp %s*.root %s' % (iBase,iLabel))
    #os.chdir (iLabel)

def generate(mass,toys):
    for i0 in range(0,toys):
        fileName='runtoy_%s.sh' % (i0)
        sub_file  = open(fileName,'a')
        sub_file.write('#!/bin/bash\n')
        sub_file.write('cd  /afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_1_20/src  \n')
        sub_file.write('eval `scramv1 runtime -sh`\n')
        sub_file.write('cd - \n')
        sub_file.write('cp -r %s . \n' % os.getcwd())
        sub_file.write('cd ZQQ_%s \n' % mass)
        sub_file.write('combine -M GenerateOnly --toysNoSystematics -t 1 mc.txt --saveToys --expectSignal 1 --seed %s \n' % i0)
        sub_file.write('combine -M MaxLikelihoodFit card_ralpha.txt -t 1  --toysFile higgsCombineTest.GenerateOnly.mH120.%s.root  > /dev/null \n' % i0 )
        sub_file.write('mv mlfit.root %s/mlfit_%s.root  \n' % (os.getcwd(),i0))
        sub_file.close()
        exec_me('chmod +x %s' % os.path.abspath(sub_file.name))
        exec_me('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(sub_file.name)))

###########################################################################
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-m','--mass'   ,action='store',type='int',dest='mass'   ,default=125, help='mass')
    parser.add_option('-n','--n' ,action='store',type='int',dest='n'   ,default=None, help='number of bins')
    parser.add_option('--p1' ,action='store',type='int',dest='p1'   ,default=None, help='number of parameters for default datacard (p1 > p2)')
    parser.add_option('--p2' ,action='store',type='int',dest='p2'   ,default=None, help='number of parameters for alternative datacard (p2 > p1)')
    parser.add_option('--msd_start', default=100, type=int, help='start of the mass range')
    parser.add_option('--msd_stop', default=150, type=int, help='stop of the mass range')
    parser.add_option('--nmsdbins', default=10, type=int, help='number of mass bins')
    parser.add_option('--nptbins', default=2, type=int, help='number of pt bins')
    parser.add_option('--pt1', default=1, type=int, help='degree in pt for default datacard')
    parser.add_option('--rho1', default=1, type=int, help='degree in rho for default datacard')
    parser.add_option('--pt2', default=1, type=int, help='degree in pt for alternative datacard')
    parser.add_option('--rho2', default=1, type=int, help='degree in rho for alternative datacard')
    parser.add_option('-t','--toys'   ,action='store',type='int',dest='toys'   ,default=300, help='number of toys')
    parser.add_option('-s','--seed'   ,action='store',type='int',dest='seed'   ,default=-1, help='random seed')
    parser.add_option('--sig'    ,action='store',type='int',dest='sig'    ,default=1 ,help='sig')
    parser.add_option('-d','--datacard'   ,action='store',type='string',dest='datacard'   ,default=None, help='datacard name')
    parser.add_option('--datacard-alt'   ,action='store',type='string',dest='datacardAlt'   ,default=None, help='alternative datacard name')
    parser.add_option('--poi'   ,action='store',type='string',dest='poi'   ,default='r', help='poi')
    parser.add_option('-M','--method'   ,dest='method'   ,default='GoodnessOfFit',
                      choices=['GoodnessOfFit','FTest','Asymptotic','Bias','MaxLikelihoodFit'],help='combine method to use')
    parser.add_option('-a','--algo'   ,dest='algo'   ,default='saturated',
                      choices=['saturated','KS'],help='GOF algo  to use')
    parser.add_option('-o','--odir', dest='odir', default=None ,help='directory to write plots and output toys', metavar='odir')
    parser.add_option('--just-plot', action='store_true', dest='justPlot', default=False, help='just plot')
    parser.add_option('--data', action='store_true', dest='isData', default=False, help='is data')
    parser.add_option('-l','--lumi'   ,action='store',type='float',dest='lumi'   ,default=36.4, help='lumi')
    parser.add_option('--scaleLumi'   ,action='store',type='float',dest='scaleLumi'   ,default=-1, help='scale nuisances by scaleLumi')
    parser.add_option('-r','--r',dest='r', default=0 ,type='float',help='default value of r')
    parser.add_option('--rMin',dest='rMin', default=-20 ,type='float',help='minimum of r (signal strength) in profile likelihood plot')
    parser.add_option('--rMax',dest='rMax', default=20,type='float',help='maximum of r (signal strength) in profile likelihood plot')
    parser.add_option('--freezeNuisances'   ,action='store',type='string',dest='freezeNuisances'   ,default='None', help='freeze nuisances')
    parser.add_option('--setParameters'   ,action='store',type='string',dest='setParameters'   ,default='None', help='setParameters')
    parser.add_option('--pdf1'   ,action='store',type='string',dest='pdf1'   ,default='poly', help='fit pdf1')
    parser.add_option('--pdf2'   ,action='store',type='string',dest='pdf2'   ,default='poly', help='gen pdf2')
    parser.add_option('--nr1','--NR1' ,action='store',type='int',dest='NR1'   ,default=2, help='order of rho polynomial for fit pdf')
    parser.add_option('--np1','--NP1' ,action='store',type='int',dest='NP1'   ,default=2, help='order of pt polynomial for fit pdf')
    parser.add_option('--nr2','--NR2' ,action='store',type='int',dest='NR2'   ,default=2, help='order of rho polynomial for gen pdf')
    parser.add_option('--np2','--NP2' ,action='store',type='int',dest='NP2'   ,default=2, help='order of pt polynomial for gen pdf')

    parser.add_option('--dry-run',dest="dryRun",default=False,action='store_true',help="Just print out commands to run")
    parser.add_option('--toysFrequentist'       ,action='store_true',default = False,dest='toysFreq', metavar='toysFreq', help='generate frequentist toys')
    parser.add_option('--toysNoSystematics'       ,action='store_true',default = False,dest='toysNoSyst', metavar='toysNoSyst', help='generate toys with nominal systematics')

    (options,args) = parser.parse_args()

    if options.n is None:
      options.n = options.nptbins*options.nmsdbins
    if options.p1 is None:
      options.p1 = (options.pt1+1)*(options.rho1+1)
    if options.p2 is None:
      options.p2 = (options.pt2+1)*(options.rho2+1)

    if options.datacard is None:
      msdbinsize = int( (options.msd_stop - options.msd_start)/options.nmsdbins )
      options.datacard = 'output/2017/v05/met20_deepTagMD_bbvsLight08695/mc_msd%dto%d_msdbin%d_pt%dbin_polyDegs%d%d'%(options.msd_start,options.msd_stop,msdbinsize,options.nptbins,options.pt1,options.rho1)+'/ttHbb_combined.root'
    if options.datacardAlt is None:
      msdbinsize = int( (options.msd_stop - options.msd_start)/options.nmsdbins )
      options.datacardAlt = 'output/2017/v05/met20_deepTagMD_bbvsLight08695/mc_msd%dto%d_msdbin%d_pt%dbin_polyDegs%d%d'%(options.msd_start,options.msd_stop,msdbinsize,options.nptbins,options.pt2,options.rho2)+'/ttHbb_combined.root'

    options.datacard    = os.path.abspath(options.datacard)
    options.datacardAlt = os.path.abspath(options.datacardAlt)

    if options.odir is None:
      options.odir = os.path.join( os.path.dirname(options.datacard),'bkgEstTests' )
    if not os.path.exists(options.odir): os.makedirs(options.odir)

    import tdrstyle
    tdrstyle.setTDRStyle()

    r.gStyle.SetOptStat(0)
    r.gStyle.SetOptFit(0)
    r.gStyle.SetOptTitle(0)
    r.gStyle.SetPaintTextFormat("1.2g")
    r.gROOT.SetBatch()
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.FATAL)

    if options.method=='GoodnessOfFit':
        iLabel= 'goodness_%s_%s'%(options.algo,options.datacard.split('/')[-1].replace('.root',''))
        goodness(options.datacard, options.toys, iLabel, options)

    elif options.method=='MaxLikelihoodFit':
        fit(options.datacard,options)

    elif options.method=='FTest':
        ptrho_base = os.path.dirname(os.path.abspath(options.datacard)).split('polyDegs')[1]
        ptrho_alt  = os.path.dirname(os.path.abspath(options.datacardAlt)).split('polyDegs')[1]
        iLabel= 'ftest_ptrho%s_vs_ptrho%s'%(ptrho_base, ptrho_alt)
        #iLabel= 'ftest_%s_vs_%s'%(options.datacard.split('/')[-1].replace('.root',''),options.datacardAlt.split('/')[-1].replace('.root',''))
        ftest(options.datacard, options.datacardAlt, options.toys, iLabel, options)

    elif options.method=='Bias':
        iLabel= 'bias_%s%i%i_vs_%s%i%i_%s%i'%(options.pdf1, options.NR1, options.NP1, options.pdf2, options.NR2, options.NP2,
                                              options.poi, options.r)
        bias(options.datacard, options.datacardAlt, options.toys, options.r, iLabel, options)
