#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 20:03:51 2021

@author: rupeshdotel
"""

import matplotlib.pyplot as plt
import numpy as np
import LT.box as B
import class_fit as cf

#%%

d = np.load('/Users/rupeshdotel/analysis/work/pi0pippimeta/data/qfactor_data/gluexI.npz')

#event_num = d['event_num']
#kinfit_CL = d['kinfit_CL']
#chisq_ndf = d['chisq_ndf']
#num_combos = d['num_combos']
#combo_number = d['combo_number']


mpi0 = d['mpi0']
meta = d['meta']
metap = d['metap']

metappi0 = d['metappi0']
cost_etap = d['cost_etap']

#problems encountered during fitting with float32 so convert to float64
mpi0 = mpi0.astype('float64')
meta = meta.astype('float64')
metap = metap.astype('float64')

#mpi013 = d['mpi013']
#mpi024 = d['mpi024']
#mpi014 = d['mpi014']
#mpi023 = d['mpi023']

#mant = d['mant']
#num_unusedshowers = d['num_unusedshowers']

#mpipp = d['mpipp']
#mpi0p = d['mpi0p']
#mpippimpi0 = d['mpippimpi0']

#cost_pi0 = d['cost_pi0']
#pi0phiGJ = d['pi0phiGJ']


#etaprimephiGJ = d['etaprimephiGJ']

#%%
mep_bins = 18 # bins etaprime invariant mass
mp_bins = 12 # bins pi0 invariant mass
mep_min = 0.86 # left edge of etaprime invariant mass
mep_max = 1.05 # right edge of etaprime invariant mass
mp_min = 0.12 # left edge of pi0 invariant mass
mp_max = 0.15 # right edge of pi0 invariant mass
h_epi0 = B.histo2d( metap, mpi0, bins = (mep_bins, mp_bins),
                   range=np.array([ (mep_min, mep_max), (mp_min, mp_max)]), title = '2D_prompt', xlabel = "$M(\pi^{+}\pi^{-}\eta)$",
                   ylabel = "$M(\gamma\gamma)$")


epm = h_epi0.x_bin_center
pi0m = h_epi0.y_bin_center


def fit_histo(h2d):
     #define empty lists for parameters and their errors from  fits
     
     A_a, x0_a,  sigma_a, c0_a, b0_a = [], [], [], [], []
     

     for i in range(h2d.nbins_y): # looping over pi0mass bins
         h = h2d.project_x(bins=[i])
         M = h.bin_center
         C = h.bin_content
         dC = h.bin_error
         mr = np.linspace(M[0], M[-1], 1000)
         f = cf.gauss_fit()
         
         # set initial parameters for fitting
         f.A.set(C.max()) 
         f.x0.set(0.956)
         f.sigma.set(0.01)
         f.b0.set(0.05)
         f.db0.set(0.5)
         f.c0.set(500)
         
         # set bounds for the fit parameters
         f.A_min.set(0.); f.A_max.set(1e5)
         f.x0_min.set(0.95); f.x0_max.set(0.96)
         f.sigma_min.set(0.008); f.sigma_max.set(0.016)
         f.c0_min.set(0.); f.c0_max.set(1e5)
         f.b0_min.set(0.00); f.b0_max.set(0.20)
         
         
         f.set_fit_list(fit = ['A', 'x0', 'sigma',  'c0', 'b0'])
         f.fit_gaussbt(M, C, dC) # gauss peak with bernstein bkg
         A_a.append([f.A.value, f.A.err])
         x0_a.append([f.x0.value, f.x0.err])
         sigma_a.append([f.sigma.value, f.sigma.err])
         b0_a.append([f.b0.value, f.b0.err])
         c0_a.append([f.c0.value, f.c0.err])
         plt.figure()
         h.plot_exp()
         f.plot_fit()
         B.plot_line(mr, f.gauss(mr))
         B.plot_line(mr, f.bt_bkg(mr))
             
    
     
        
     return    np.array(A_a), np.array(x0_a),  np.array(sigma_a), np.array(b0_a), np.array(c0_a)
  
#%%
A_a, x0_a, S_a, B0_a, C0_a = fit_histo(h_epi0)  

#%%
A_value = A_a[:,0] ; A_err = A_a[:,1] 
x0_value = x0_a[:,0] ; x0_err = x0_a[:,1] 
S_value = S_a[:,0] ; S_err = S_a[:,1] 
B0_value = B0_a[:,0]  ; B0_err = B0_a[:,1] 
C0_value = C0_a[:,0]  ; C0_err = C0_a[:,1] 


A_fit = cf.gauss_fit()
A_fit.set_fit_list( fit = ['A', 'x0', 'sigma', 'c0', 'b0'])

# set parameters for combined gaussian linear fit 
A_fit.A.set(A_value.max())
A_fit.x0.set(0.1365)
A_fit.sigma.set(0.004)
A_fit.b0.set(0.8)
A_fit.db0.set(0.1)
A_fit.c0.set(50.)

#set bounds for  combined gaussian linear fit 
A_fit.A_min.set(100.); A_fit.A_max.set(3000.)
A_fit.x0_min.set(0.13); A_fit.x0_max.set(0.14)
A_fit.sigma_min.set(0.003); A_fit.sigma_max.set(0.03)

A_fit.b0_min.set(0.5); A_fit.b0_max.set(0.9)
A_fit.c0_min.set(45.); A_fit.c0_max.set(70.)

A_fit.fit_gaussbt(pi0m, A_value, A_err) # fit gauss peak with linear bkg
plt.figure();A_fit.plot_fit()
B.plot_line(pi0m, A_fit.gauss(pi0m))
B.plot_line(pi0m, A_fit.bt_bkg(pi0m))
B.plot_exp(pi0m, A_value, A_err,  plot_title = 'Fit the fit parameter A',  x_label = ' $M(\gamma\gamma)$' )


plt.figure()
px0 = B.polyfit(pi0m, x0_value, x0_err,   order = 1)
B.plot_exp(pi0m, x0_value,  x0_err, plot_title = 'Fit the fit parameter $x0$', x_label = 'bin centers of y-axis in 2D plot $M(\pi^{0})$')
B.plot_line(px0.xpl, px0.ypl)

plt.figure()
pS = B.polyfit(pi0m, S_value, S_err,   order = 2)
B.plot_exp(pi0m, S_value,  S_err, plot_title = 'Fit the fit parameter $sigma$', x_label = 'bin centers of y-axis in 2D plot $M(\pi^{0})$')
B.plot_line(pS.xpl, pS.ypl)


plt.figure()
pB0 = B.polyfit(pi0m, B0_value, B0_err,   order = 2)
B.plot_exp(pi0m, B0_value,  B0_err, plot_title = 'Fit the fit parameter $b0$', x_label = 'bin centers of y-axis in 2D plot $M(\pi^{0})$')
B.plot_line(pB0.xpl, pB0.ypl)



plt.figure()
pC0 = B.polyfit(pi0m, C0_value, C0_err,   order = 4)
B.plot_exp(pi0m, C0_value,  C0_err, plot_title = 'Fit the fit parameter $c0$', x_label = 'bin centers of y-axis in 2D plot $M(\pi^{0})$')
B.plot_line(pC0.xpl, pC0.ypl)

#%%

def bkg_fit(x,y): # x as etaprime mass and y as pi0mass
    
    f = cf.gauss_fit()
    f.b0.set(pB0.poly(y))
    f.db0.set(0.5) #  this should match f db0 value not A_fit db0 value
    f.m0.set(0.87)
    f.m1.set(1.05)
    f.c0.set(pC0.poly(y))
    Y = f.bt_bkg(x)
    return   Y
    

def peak_fit(x,y): # x as etaprime mass and y as pi0mass
    
    g = cf.gauss_fit()
    g.A.set(A_fit.signal_bt_bkg(y))
    g.x0.set(px0.poly(y))
    g.sigma.set(pS.poly(y))
    Y = g.gauss(x)
    return Y


def signal_fit(x,y):
    return peak_fit(x,y) + bkg_fit(x,y)
    


#%%
#calculate the q factors

qb_sel  = np.abs(bkg_fit(metap, mpi0))
qs_sel = np.abs(peak_fit(metap, mpi0))


q = qs_sel/(qb_sel + qs_sel)
qs = q
qb = 1-q

#%%

#sel = (mep_min < metap) & (metap < mep_max)
#meta = meta[sel]
#qs_for_eta = qs[sel]
he_ws2d = B.histo(meta, bins = 24, weights = qs, title = '$\eta$' , xlabel = 'M($\gamma\gamma$)')
he = B.histo(meta, bins = 24)
plt.figure()

he_ws2d.show_fit_list()
he_ws2d.set_fit_list(fit = ['A', 'mean', 'sigma', 'b0', 'b1', 'b2'])

he_ws2d.fit()
he_ws2d.plot_exp()

he_ws2d.plot_fit()
he_ws2d.title = '$\eta$'
he_ws2d.x_lable = '$M(\gamma\gamma)$'
b0 = he_ws2d.b0.value
b1 = he_ws2d.b1.value
b2 = he_ws2d.b2.value
#b2 = hs.b2.value

def eta_bkg(x):
    return b0 + b1*x + b2*x*x

def qeta_bkg(x):
    b = eta_bkg(x)
    t = he_ws2d.fit_func(x) 
    s = t - b
    qs = s/t
    qb = 1 - qs
    return qs, qb



qse, qbe = qeta_bkg(meta)

hse = B.histo(meta, bins = 24, weights = qs*qse, title = '$\eta$', xlabel = 'M($\gamma\gamma$)')
plt.figure();he.plot_exp(); hse.plot_exp();  he_ws2d.plot_exp() 


#%%

# get histograms (1D)

# for etaprime mass
hb_ep = B.histo(metap, range = (mep_min, mep_max),  bins = 24, weights = qb, title = "bkg $\eta'$",
               xlabel = "$M(\pi^{+}\pi^{-}\eta)$")
hs_ep = B.histo(metap, range = (mep_min, mep_max), bins = 24, weights = qs, title = "signal $\eta'$",
               xlabel = "$M(\pi^{+}\pi^{-}\eta)$")
ht_ep = B.histo(metap, range = (mep_min, mep_max), bins = 24, title = 'Non-weighted',
               xlabel = "$M(\pi^{+}\pi^{-}\eta)$")
plt.figure();
hb_ep.plot_exp();hs_ep.plot_exp();ht_ep.plot_exp()


# for pi0mass
hb_p = B.histo(mpi0, range = (mp_min, mp_max),  bins = 24, weights = qb, title = 'bkg $\pi^{0}$',
               xlabel = "$M(\gamma\gamma)$")
hs_p = B.histo(mpi0, range = (mp_min, mp_max), bins = 24, weights = qs*qse, title = 'signal $\pi^{0}$',
               xlabel = "$M(\gamma\gamma)$")
ht_p = B.histo(mpi0, range = (mp_min, mp_max), bins = 24, title = 'Non-weighted',
               xlabel = "$M(\gamma\gamma)$")
    
plt.figure();
hb_p.plot_exp();hs_p.plot_exp();ht_p.plot_exp()

#%%
#get histograms (2D) etaprime vs pi0mass
hs2 = B.histo2d(metap, mpi0, range = [[mep_min, mep_max], [mp_min, mp_max]],
                bins = (24, 24), title = 'Invariant Mass in 2D for Signal events', weights = qs, 
                xlabel = "$M(\pi^{+}\pi^{-}\eta)$", ylabel = "$M(\gamma\gamma)$")

plt.figure();hs2.plot(graph = 'surface')

hb2 = B.histo2d(metap, mpi0, range = [[mep_min, mep_max], [mp_min, mp_max]],
                bins = (24, 24), title = 'Invariant Mass in 2D for Bkg events', weights = qb,
                xlabel = "$M(\pi^{+}\pi^{-}\eta)$", ylabel = "$M(\gamma\gamma)$")

plt.figure();hb2.plot(graph = 'surface')

ht2 = B.histo2d(metap, mpi0, range = [[mep_min, mep_max], [mp_min, mp_max]], bins = (24, 24), 
                title = 'Invariant Mass in 2D ', xlabel = "$M(\pi^{+}\pi^{-}\eta)$", ylabel = "$M(\gamma\gamma)$")

plt.figure();ht2.plot(graph = 'surface')
#%%

#Angular distribution in GJ frame

# get histograms (2D)
h2S_GJ = B.histo2d(metappi0, cost_etap, range = [[0.9, 3.1], [-1, 1]],
                bins = (24, 24), title = 'Angular distribution in GJ Frame Signal Response', weights = qs, 
                xlabel = "$M(\eta'\pi^{0})$", ylabel = "$cos\\theta_{GJ}$")

plt.figure();h2S_GJ.plot()


h2B_GJ = B.histo2d(metappi0, cost_etap, range = [[0.9, 3.1], [-1, 1]],
                bins = (24, 24), title = 'Angular distribution in GJ Frame Bkg response', weights = qb, 
                xlabel = "$M(\eta'\pi^{0})$", ylabel = "$cos\\theta_{GJ}$")

plt.figure();h2B_GJ.plot()

#%%

# get histograms (1D) etaprimepi0 invariant mass
hS_GJ = B.histo(metappi0, range = [0.9, 3.1], bins = 30,  weights = qs, 
               xlabel = "$M(\eta'\pi^{0})$", title = "Invariant mass of $\eta^{'}\pi^{0}$ Signal Response")

plt.figure();hS_GJ.plot_exp()

hB_GJ = B.histo(metappi0, range = [0.9, 3.1], bins = 30,  weights = qb, 
               xlabel = "$M(\eta'\pi^{0})$", title = "Invariant mass of $\eta^{'}\pi^{0}$ Bkg Response")

plt.figure();hB_GJ.plot_exp()

#%%

# project 2d signal response in forward, middle and backward angles
hf = h2S_GJ.project_x(range = [0.5, 1])
plt.figure();hf.plot_exp()
hm = h2S_GJ.project_x(range = [-0.5, 0.5])
plt.figure();hm.plot_exp()
hb = h2S_GJ.project_x(range = [-1.0, -0.5])
plt.figure();hb.plot_exp()

#%%

# project 2d signal response in forward, middle and backward angles
hf = h2B_GJ.project_x(range = [0.5, 1])
plt.figure();hf.plot_exp()
hm = h2B_GJ.project_x(range = [-0.5, 0.5])
plt.figure();hm.plot_exp()
hb = h2B_GJ.project_x(range = [-1.0, -0.5])
plt.figure();hb.plot_exp()

#%%


#qs.astype(float32)
#np.savez('/Users/rupeshdotel/analysis/work/pi0pippimeta/data/qfactor_data/weights.npz', weights = qs)

