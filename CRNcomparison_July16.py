# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 06:38:37 2015

@author: smudd
"""

    
import numpy as np
import CRNResults as CRNR
import LSDOSystemTools as LSDost
from glob import glob
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.gridspec import GridSpec
        #from scipy.stats import gaussian_kde



def CollateCRNData():
    
    #Directory = "C://basin_data//CosmoPaper//Results//Compiled//"
    Directory = "T://Papers_LaTeX//crn_basinwide_paper//Compiled_results//"
    Dirname = LSDost.ReformatSeperators(Directory)
    Dirname = LSDost.AppendSepToDirectoryPath(Dirname)
    
    Fileformat = 'svg'
    
    # This list will store the crn data
    CRNDataList = []  
    CRNprefixes = []
    PaperNames = []
    PaperColours = []
    
    label_size = 8
    axis_size = 12

    # Set up fonts for plots
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size
    rcParams['xtick.major.size'] = 4    
    rcParams['ytick.major.size'] = 4
    rcParams['legend.fontsize'] = label_size
    rcParams['legend.handletextpad'] = 0.05
    rcParams['legend.labelspacing'] =0.1
    rcParams['legend.columnspacing'] =0.1
    
       
    # loop through the directory, getting the results from the data    
    for fname in glob(Dirname+"*_CRNResults.csv"):
        
        # get only the file without the data directory
        NoDirFname = LSDost.GetFileNameNoPath(fname)
        
        # Now get the prefix of the file
        splitfname = NoDirFname.split('_CRNResults.csv')
        fprefix = splitfname[0]
        
        # now produce the cronus name from this prefix
        CRONUS_name = Dirname+fprefix+"_CRONUSEmulator.csv"
        
        print "File prefix is: " + fprefix 
        print "Cronus_name is: " + CRONUS_name
        
        # now read in the data
        thisCRNData = CRNR.CRNResults(fname)        

        # read in the Cronus data and get the errors
        thisCRNData.ReadCRONUSData(CRONUS_name)
        thisCRNData.GetErrorsBetweenMethods()
        thisCRNData.GetErrorsBetweenCRONUS()
        
        CRNDataList.append(thisCRNData)
        CRNprefixes.append(fprefix)
        
        # now get the prefixes
        if fprefix == "Bierman":
            PaperNames.append("Bierman et al., 2005")
            PaperColours.append("blue")
        elif fprefix == "Dethier":
            PaperNames.append("Dethier et al., 2014")
            PaperColours.append("lawngreen")
        elif fprefix == "Kirchner":
            PaperNames.append("Kirchner et al., 2001") 
            PaperColours.append("yellow")               
        elif fprefix == "Munack":
            PaperNames.append("Munack et al., 2014")
            PaperColours.append("orange")
        elif fprefix == "Scherler":
            PaperNames.append("Scherler et al., 2014")
            PaperColours.append("black")
        elif fprefix == "Safran":
            PaperNames.append("Safran et al., 2005")
            PaperColours.append("powderblue")
        elif fprefix == "Palumbo":
            PaperNames.append("Palumbo et al., 2010")
            PaperColours.append("maroon")             
            
    #===========================================================================    
    # now make plots based on these data
    # 3.26 inches = 83 mm, the size of a 1 column figure
    Fig1 = plt.figure(1, facecolor='white',figsize=(3.26,6.25))  

    # generate a 120,90 grid. 
    # gendepth a grid. 
    gs = GridSpec(100,100,bottom=0.06,left=0.1,right=1.0,top=1.0) 
    ax = Fig1.add_subplot(gs[2:41,10:95])  
    
    # this gets the colors to map to specific sites
    #cmap = plt.cm.jet    
    #colo = 0       
    
    
    for index,CRNObj in enumerate( CRNDataList):
        #colo = colo + (1.000/len(CRNprefixes))
        ax.plot(CRNObj.GetAverageCombinedScaling(),CRNObj.GetError_CR(), "o",
                markersize=4, color=PaperColours[index], label = PaperNames[index],markeredgewidth=1)

    ax.spines['top'].set_linewidth(1)
    ax.spines['left'].set_linewidth(1)
    ax.spines['right'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1) 
    ax.tick_params(axis='both', width=1) 
       
    plt.xlabel('Production factor ($S_{tot}$)', fontsize = axis_size)
    plt.ylabel('($\epsilon_{CR2.2}$-$\epsilon_{CAIRN}$)/$\epsilon_{CAIRN}$', fontsize = axis_size)
    #plt.title('Cosmocalc / New_code',fontsize = label_size+6)
    #handles, labels = ax.get_legend_handles_labels()
    #plt.legend()
    #plt.legend(handles, labels, numpoints = 1, bbox_to_anchor=(0., 1.02, 1., .102), 
    #           loc=3, ncol=2, mode="expand", borderaxespad=0.)

    # generate a 120,90 grid. 
    ax2 = Fig1.add_subplot(gs[58:97,10:95])    

    plt.rcParams['xtick.major.size'] = 4    
    plt.rcParams['xtick.minor.size'] = 3
    plt.rcParams['ytick.major.size'] = 4
    
    # this gets the colors to map to specific sites
    #cmap = plt.cm.jet    
    #colo = 0       

    for index,CRNObj in enumerate( CRNDataList):
        #colo = colo + (1.000/len(CRNprefixes))
        ax2.plot(CRNObj.GetErosionRates(),CRNObj.GetError_CR(), "o", markersize=4, 
                color=PaperColours[index], label = PaperNames[index], markeredgewidth=1)

    ax2.spines['top'].set_linewidth(1)
    ax2.spines['left'].set_linewidth(1)
    ax2.spines['right'].set_linewidth(1)
    ax2.spines['bottom'].set_linewidth(1) 
    #ax.tick_params(axis='both', width=2.5)
    ax2.set_xscale('log') 
    
    # This gets all the ticks, and pads them away from the axis so that the corners don't overlap
    # the which command tells the program to get major and minor ticks 
    ax2.tick_params(axis='both', width=1, pad = 1, which = 'both')
    for tick in ax2.xaxis.get_major_ticks():
        tick.set_pad(3)   

    for tick in ax2.yaxis.get_major_ticks():
        tick.set_pad(3)  

    #for tick in ax.xaxis.get_minor_ticks():
    #    tick.tick_params(width = 2.5)  
        
        
    plt.xlabel('$\epsilon_{CAIRN}$ (g cm$^{-2}$ yr$^{-1}$)', fontsize = axis_size)
    plt.ylabel('($\epsilon_{CR2.2}$-$\epsilon_{CAIRN}$)/$\epsilon_{CAIRN}$', fontsize = axis_size)
    #plt.title('Cosmocalc / New_code',fontsize = label_size+6)
    handles, labels = ax.get_legend_handles_labels()
    plt.legend()
    plt.legend(handles, labels, numpoints = 1, bbox_to_anchor=(0., 1.02, 1., .102), 
               loc=3, ncol=2, mode="expand", borderaxespad=0.)    
    #plt.show()    
    plt.savefig(Dirname+"Production_and_erosion_vs_error.svg",format = Fileformat)  
    
    Fig1.clf()    












 #=========================================================================== 
 #===========================================================================         
    #===========================================================================   
    # now make plots based on these data
    Fig3 = plt.figure(1, facecolor='white',figsize=(3.26,6.25))  

    # generate a 120,90 grid. 
    gs = GridSpec(100,100,bottom=0.06,left=0.1,right=1.0,top=1.0) 
    ax3 = Fig3.add_subplot(gs[2:41,10:95])  

    plt.rcParams['xtick.major.size'] = 4    
    plt.rcParams['ytick.major.size'] = 4
    
    # this gets the colors to map to specific sites
    #cmap = plt.cm.jet    
    #colo = 0       

    for index,CRNObj in enumerate( CRNDataList):
        #colo = colo + (1.000/len(CRNprefixes))
        ax3.plot(CRNObj.GetAverageCombinedScaling(),CRNObj.GetError_CC(), "o",
                markersize=4, color=PaperColours[index], label = PaperNames[index],markeredgewidth=1)

    ax3.spines['top'].set_linewidth(1)
    ax3.spines['left'].set_linewidth(1)
    ax3.spines['right'].set_linewidth(1)
    ax3.spines['bottom'].set_linewidth(1) 
    #ax.tick_params(axis='both', width=2.5)
    
    # This gets all the ticks, and pads them away from the axis so that the corners don't overlap
    # the which command tells the program to get major and minor ticks 
    ax3.tick_params(axis='both', width=1, pad = 1, which = 'both')
    for tick in ax3.xaxis.get_major_ticks():
        tick.set_pad(3)   

    for tick in ax3.yaxis.get_major_ticks():
        tick.set_pad(3)  

    #for tick in ax.xaxis.get_minor_ticks():
    #    tick.tick_params(width = 2.5)  
        
        
    plt.xlabel('Production factor ($S_{CCtot}$)', fontsize = axis_size)
    plt.ylabel('($\epsilon_{CC}$-$\epsilon_{CAIRN}$)/$\epsilon_{CAIRN}$', fontsize = axis_size)
    #plt.title('Cosmocalc / New_code',fontsize = label_size+6)
    #handles, labels = ax.get_legend_handles_labels()
    #plt.legend(handles, labels, numpoints = 1, bbox_to_anchor=(0., 1.02, 1., .102), 
    #           loc=3, ncol=2, mode="expand", borderaxespad=0.)    
        
    plt.rcParams['xtick.major.size'] = 4   
    
    # this gets the colors to map to specific sites
    #cmap = plt.cm.jet    
    #colo = 0       


    ax4 = Fig1.add_subplot(gs[58:97,10:95])   

    for index,CRNObj in enumerate( CRNDataList):
        #colo = colo + (1.000/len(CRNprefixes))
        ax4.plot(CRNObj.GetAverageCombinedScaling(),CRNObj.GetError_CR_em(), "o",
                markersize=4, color=PaperColours[index], label = PaperNames[index],markeredgewidth=1)

    ax4.spines['top'].set_linewidth(1)
    ax4.spines['left'].set_linewidth(1)
    ax4.spines['right'].set_linewidth(1)
    ax4.spines['bottom'].set_linewidth(1) 
    #ax.tick_params(axis='both', width=2.5)
    
    # This gets all the ticks, and pads them away from the axis so that the corners don't overlap
    # the which command tells the program to get major and minor ticks 
    ax4.tick_params(axis='both', width=1, pad = 1, which = 'both')
    for tick in ax4.xaxis.get_major_ticks():
        tick.set_pad(3)   

    for tick in ax4.yaxis.get_major_ticks():
        tick.set_pad(3)  

    #for tick in ax.xaxis.get_minor_ticks():
    #    tick.tick_params(width = 2.5)  
        
        
    plt.xlabel('Production factor ($S_{CRShield}$*$S_{effp}$)', fontsize = axis_size)
    plt.ylabel('($\epsilon_{CC-CR}$-$\epsilon_{CAIRN}$)/$\epsilon_{CAIRN}$', fontsize = axis_size)
    #plt.title('Cosmocalc / New_code',fontsize = label_size+6)
    handles, labels = ax4.get_legend_handles_labels()
    plt.legend(handles, labels, numpoints = 1, bbox_to_anchor=(0., 1.02, 1., .102), 
               loc=3, ncol=2, mode="expand", borderaxespad=0.)    
        
    #plt.show()    
    plt.savefig(Dirname+"COSMOCALC_and_spatial_differences.svg",format = Fileformat)           
    Fig3.clf()         

if __name__ == "__main__":
    CollateCRNData() 