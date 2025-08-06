# -*- coding: utf-8 -*-
#
# This program uses the Welch method of scipy to compute the power spectral 
# density (one-sided).
#
# This file is part of HectorP 0.1.12.
#
#  HectorP is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  HectorP is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with HectorP. If not, see <http://www.gnu.org/licenses/>
#
# 6/2/2022 Machiel Bos, Santa Clara
#===============================================================================

import os
import math
import time
import json
import sys
import numpy as np
from matplotlib import pyplot as plt
from hectorp.control import Control
from hectorp.observations import Observations
from scipy import signal
import argparse
from pathlib import Path

#===============================================================================
# Subroutines
#===============================================================================

def compute_G_White(f):
    """ compute PSD for white noise

    Args:
        f (float) : normalised frequency (0 - pi)
  
    Returns:
        G, which is one sided PSD, at frequency f
    """

    return 2.0



def compute_G_Powerlaw(f,d):
    """ compute PSD for Powerlaw noise

    Args:
        f (float) : normalised frequency (0 - pi)
        d (float) : -kappa/2
  
    Returns:
        G, which is one sided PSD, at frequency f
    """

    return 2.0/math.pow(2.0*math.sin(0.5*f),2.0*d)



def compute_G_GGM(f,d,phi):
    """ compute PSD for GGM noise

    Args:
        f (float) : normalised frequency (0 - pi)
        d (float) : -kappa/2
        phi (float) : Actually, this is 1-phi ...
  
    Returns:
        G, which is one sided PSD, at frequency f
    """

    return 2.0/math.pow(4.0*(1-phi)*math.pow(math.sin(0.5*f),2.0) + 
                                                math.pow(phi,2.0),d)



def compute_G_AR1(f,phi):
    """ compute PSD for AR1 noise

    Args:
        f (float) : normalised frequency (0 - pi)
        phi (float) : phi
  
    Returns:
        G, which is one sided PSD, at frequency f
    """

    return 2.0/(1-2*phi*math.cos(f)+phi*phi)



def compute_G_VA(f,fs,phi):
    """ compute PSD for VaryingAnnual noise

    Args:
        f (float) : real frequency  (Hz)
        fs (float) : real sampling frequency (Hz)
        phi (float) : phi

    Returns:
        G, which is one sided PSD, at frequency f
    """

    f0 = 1.0/(86400.0*365.25)
    tpi = 2*math.pi

    return 2.0/math.pi * (1.0/(1-2*phi*math.cos(tpi*(f+f0)/fs)+phi*phi) + \
                          1.0/(1-2*phi*math.cos(tpi*(f-f0)/fs)+phi*phi))



def compute_G_Matern(f,d,lamba):
    """ compute PSD for VaryingAnnual noise

    Args:
        f (float) : real frequency  (Hz)
        d (float) : -0.5*kappa spectral index
        lamba (float) : similar to funcion of phi in GGM

    Returns:
        G, which is one sided PSD, at frequency f
    """

    tpi = 2.0*math.pi
    alpha = 2.0*d
    c_alpha = math.gamma(0.5)*math.gamma(alpha-0.5)/(tpi*math.gamma(alpha))

    return 2.0*pow(lamba,2.0*alpha-1.0)/c_alpha * \
                                1.0/pow(pow(f,2.0) + pow(lamba,2.0),alpha)

#===============================================================================
# Main program
#===============================================================================

def main():

    #--- Constants
    tpi = math.pi*2.0

    #--- Parse command line arguments in a bit more professional way
    parser = argparse.ArgumentParser(description= 'Estimate power spectrum')

    #--- List arguments that can be given 
    parser.add_argument('-graph', action='store_true', required=False,
       					help='No graph is shown on screen')
    parser.add_argument('-eps', action='store_true',required=False,
       					help='Save graph to an eps-file')
    parser.add_argument('-png', action='store_true',required=False,
       					help='Save graph to an png-file')
    parser.add_argument('-model', action='store_true',required=False,
       					help='add noise model spectrum to graph')
    parser.add_argument('-i', required=False, default='estimatespectrum.ctl', \
                                      dest='fname', help='Name of control file')

    args = parser.parse_args()

    #--- parse command-line arguments
    graph = args.graph
    save_eps = args.eps
    save_png = args.png
    plot_noisemodels = args.model
    fname = args.fname

    #--- Read control parameters into dictionary (singleton class)
    control = Control(fname)

    #--- Get basename of filename
    datafile = control.params['DataFile']
    phys_unit = control.params['PhysicalUnit']
    try:
        time_unit = control.params['TimeUnit']
    except:
        time_unit = 'unkown'

    try:
        plotname = control.params['PlotName']
    except:
        cols = datafile.split('.')
        plotname = cols[0]
    try:
        verbose = control.params['Verbose']
    except:
        verbose = True

    if verbose==True:
        print("\n***************************************")
        print("    estimatespectrum, version 0.1.12.")
        print("***************************************")

    #--- Get Classes
    observations = Observations()

    #--- Sampling frequency (change daily period into number of seconds)
    DeltaT = observations.sampling_period
    print('DeltaT = {0:f}'.format(DeltaT))
    if observations.ts_format=='mom':
        fs = 1.0/(86400.0*DeltaT)
        T  = DeltaT/365.25 # T in yr
    elif observations.ts_format=='msf':
        fs = 1.0/observations.sampling_period
        T  = DeltaT/3600.0 # T in hours
    else:
        fs = 1.0/observations.sampling_period
        T  = DeltaT        # just T 


    #--- Which noise models 
    if plot_noisemodels==True:
        #--- parse output
        if os.path.exists('estimatetrend.json')==False:
            print('There is no estimatetrend.json')
            sys.exit()
        try:
            fp_dummy = open('estimatetrend.json','r')
            results = json.load(fp_dummy)
            fp_dummy.close()
        except:
            print('Could not read estimatetrend.json')
            sys.exit()

        #--- Get list of noise model names
        noisemodels = results['NoiseModel']

        #--- extract parameter values
        if 'White' in noisemodels:
            sigma_w = noisemodels['White']['sigma']
        if 'Powerlaw' in noisemodels:
            sigma_pl = noisemodels['Powerlaw']['sigma']
            kappa = noisemodels['Powerlaw']['kappa']
            d_pl = -kappa/2.0
            sigma_pl *= math.pow(T,0.5*d_pl)
        if 'FlickerGGM' in noisemodels:
            sigma_fn = noisemodels['FlickerGGM']['sigma']
            sigma_fn *= math.pow(T,0.5*0.5)
        if 'RandomWalkGGM' in noisemodels:
            sigma_rw = noisemodels['RandomWalkGGM']['sigma']
            sigma_rw *= math.pow(T,0.5*1.0)
        if 'GGM' in noisemodels:
            sigma_ggm = noisemodels['GGM']['sigma']
            kappa = noisemodels['GGM']['kappa']
            d_ggm = -kappa/2.0
            phi_ggm = noisemodels['GGM']['1-phi']
            sigma_ggm *= math.pow(T,0.5*d_ggm)
            print('sigma_eta = {0:f}'.format(sigma_ggm))
        if 'VaryingAnnual' in noisemodels:
            sigma_va = noisemodels['VaryingAnnual']['sigma']
            phi_va = noisemodels['VaryingAnnual']['phi']
        if 'AR1' in noisemodels:
            sigma_ar1 = noisemodels['AR1']['sigma']
            phi_ar1 = noisemodels['AR1']['phi']
        if 'Matern' in noisemodels:
            sigma_mt = noisemodels['Matern']['sigma']
            kappa = noisemodels['Matern']['kappa']
            d_mt = -kappa/2.0
            lamba_mt = noisemodels['Matern']['lambda']
   
        #--- create string with noise model names
        noisemodel_names = ''
        for noisemodel in list(noisemodels):
            if len(noisemodel_names)>0:
               noisemodel_names += ' + '
            if noisemodel=='White':
                noisemodel_names += 'WN'
            elif noisemodel=='Powerlaw':
                noisemodel_names += 'PL'
            elif noisemodel=='GGM':
                if phi_ggm<1.0e-5:
                    noisemodel_names += 'PL'
                else:
                    noisemodel_names += 'GGM'
            elif noisemodel=='FlickerGGM':
                noisemodel_names += 'FN'
            elif noisemodel=='RandomwalkGGM':
                noisemodel_names += 'RW'
            elif noisemodel=='VaryingAnnual':
                noisemodel_names += 'VA'
            elif noisemodel=='AR1':
                noisemodel_names += 'AR1'
            elif noisemodel=='Matern':
                noisemodel_names += 'MT'

    #--- Get data
    if 'mod' in observations.data.columns:
        x = observations.data['obs'].to_numpy() - \
					observations.data['mod'].to_numpy()
    else:
        x = observations.data['obs'].to_numpy()

    #--- Replace NaN's to zero's
    x_clean = np.nan_to_num(x)
    n       = len(x)

    print(x_clean[0:5])

    #--- Compute PSD with Welch method
    f, Pxx_den = signal.welch(x_clean, fs, window='hann', return_onesided=True,\
					             noverlap=n//8,nperseg=n//4)

    #--- Add PSD of noise models?
    if plot_noisemodels==True:
        m = len(f)
        N = 1000
        freq0 = math.log(f[1]);
        freq1 = math.log(f[m-1]);
        fm = [0.0]*N
        G  = [0.0]*N
        for i in range(0,N):
            s    = i/float(N);
            fm[i] = math.exp((1.0-s)*freq0 + s*freq1)
            for noisemodel in noisemodels:
                if noisemodel=='White':
                    scale = math.pow(sigma_w,2.0)/fs #--- no negative f (2x)
                    G[i] += scale*compute_G_White(tpi*fm[i]/fs)
                elif noisemodel=='Powerlaw':
                    scale = math.pow(sigma_pl,2.0)/fs 
                    G[i] += scale*compute_G_Powerlaw(tpi*fm[i]/fs,d_pl)
                elif noisemodel=='FlickerGGM':
                    scale = math.pow(sigma_fn,2.0)/fs 
                    G[i] += scale*compute_G_Powerlaw(tpi*fm[i]/fs,0.5)
                elif noisemodel=='RandomWalkGGM':
                    scale = math.pow(sigma_rw,2.0)/fs
                    G[i] += scale*compute_G_Powerlaw(tpi*fm[i]/fs,1.0)
                elif noisemodel=='GGM':
                    scale = math.pow(sigma_ggm,2.0)/fs
                    G[i] += scale*compute_G_GGM(tpi*fm[i]/fs,d_ggm,phi_ggm)
                elif noisemodel=='AR1':
                    scale = math.pow(sigma_ar1,2.0)/fs
                    G[i] += scale*compute_G_AR1(tpi*fm[i]/fs,phi_ar1)
                elif noisemodel=='VaryingAnnual':
                    scale = math.pow(sigma_va,2.0)/fs
                    G[i] += scale*compute_G_VA(fm[i],fs,phi_va)
                elif noisemodel=='Matern':
                    scale = math.pow(sigma_mt,2.0)/fs
                    G[i] += scale*compute_G_Matern(tpi*fm[i]/fs,d_mt,lamba_mt)
                else:
                    print('Unknown noisemodel: {0:s}'.format(noisemodel))
                    sys.exit()
 
    if graph==True or save_eps==True or save_png==True:
        fig = plt.figure(figsize=(5, 4), dpi=150)
        plt.loglog(f, Pxx_den, label='observed')
        if plot_noisemodels==True:
            plt.loglog(fm, G, label=noisemodel_names)
        if observations.ts_format=='mom' or observations.ts_format=='msf':
            plt.xlabel('frequency [Hz]')
            plt.ylabel('PSD [{0:s}**2/Hz]'.format(phys_unit))
        else:
            plt.xlabel('frequency [1/{0:s}]'.format(time_unit))
            plt.ylabel('PSD [{0:s}**2 * {1:s}]'.format(phys_unit,time_unit))
        plt.legend()
        if graph==True:
            plt.show()

        if save_eps==True or save_png==True:

            #--- Does the psd_figures directory exists?
            if not os.path.exists('psd_figures'):
                os.mkdir('psd_figures')
 
            directory = Path('psd_figures') 
            if save_eps==True: 
                fname = directory / '{0:s}.eps'.format(plotname) 
                fig.savefig(fname, format='eps', bbox_inches='tight')
            if save_png==True: 
                fname = directory / '{0:s}.png'.format(plotname) 
                fig.savefig(fname, format='png', bbox_inches='tight')


    #--- Write PSD to file
    fp = open('estimatespectrum.out','w')
    for i in range(0,len(f)):
        fp.write('{0:e}  {1:e}\n'.format(f[i],Pxx_den[i]))
    fp.close()
    if plot_noisemodels==True:
        fp = open('modelspectrum.out','w')
        for i in range(0,len(fm)):
            fp.write('{0:e}  {1:e}\n'.format(fm[i],G[i]))
        fp.close()
