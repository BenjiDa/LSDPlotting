# -*- coding: utf-8 -*-
"""
Created on Tue Nov 03 20:53:44 2015

@author: smudd
"""

# This contains the CRNResults object, used for interpreting and plotting
# CRN data

import LSDOSystemTools as LSDOst
import os
import numpy as np

class CRNResults(object):

    # The constructor: it needs a filename to read    
    def __init__(self,FileName):
        
        # This gets the filename without the .csv
        file_prefix = LSDOst.GetFilePrefix(FileName)
        
        print "Loading a file, the file prefix is: " + file_prefix
        
        if file_prefix.endswith('_CRNResults'):
            file_prefix = file_prefix[:-11]           
            self.FilePrefix = file_prefix
        else:
            self.FilePrefix = 'NULL'

        print "The object file prefix is: " + self.FilePrefix
        
        #See if the parameter files exist
        if os.access(FileName,os.F_OK):
            this_file = open(FileName, 'r')
            lines = this_file.readlines()
            
            # get rid of the header
            del lines[0:3]

            # get rid of the control characters
            this_line = LSDOst.RemoveEscapeCharacters(lines[0])
            
            # Now get a list with the names of the parameters                        
            self.VariableList = this_line.split(',')
            
            #print "Variable list is: "
            #print self.VariableList
            
            # get rid of the names
            del lines[0]             
            
            # now you need to make a dict that contains a vist for each varaible name
            DataDict = {}  
            for name in self.VariableList:
                DataDict[name] = []
                
            # now get the data into the dict
            for line in lines:
                this_line = LSDOst.RemoveEscapeCharacters(line)
                split_line = this_line.split(',')
                
                for index,name in enumerate(self.VariableList):
                    if name == 'sample_name':
                        DataDict[name].append(split_line[index])
                    elif name == 'nuclide':
                        DataDict[name].append(split_line[index])
                    else:
                        DataDict[name].append(float(split_line[index]))
                    
                    #if name == 'basin_relief':
                    #    print "getting relief of: " +str(float(split_line[index]))
                    
                #print "Finished assimilating Data Dict"
          
            self.CRNData = DataDict
        else:
            print "Uh oh I could not open that file"
            self.VariableList = []
            self.CRNData = {}
        
        # add a bool to let other modules know if you've got the data from CRONUS
        self.HaveCRONUSData = False

    # This reads data from the CRONUS calculator
    # It is not intellegent: it assumes that you have converted to csv
    # And that you have put the samples in the same order they appear
    # in the CRNRuslts.csv file
    def ReadCRONUSData(self,FileName):

        #See if the parameter files exist
        if os.access(FileName,os.F_OK):
            this_file = open(FileName, 'r')
            lines = this_file.readlines()
            
            CRONUS_eff_erate = []
            CRONUS_erate = []
            CRONUS_ext_uncert = [] 
            CRONUS_in_uncert = [] 
            
            # now get the data into the dict
            for line in lines:
                this_line = LSDOst.RemoveEscapeCharacters(line)
                split_line = this_line.split(',')
 
                CRONUS_eff_erate.append(float(split_line[4]))
                CRONUS_erate.append(float(split_line[5]))
                CRONUS_ext_uncert.append(float(split_line[6]))
                CRONUS_in_uncert.append(float(split_line[3])) 
                
            #print "I got the erate from CRONUS, here is the data: " 
            #print CRONUS_eff_erate
                
            # check to see if number of data elements are the same
            ERate = self.CRNData['erate_g_percm2_peryr']
            if (len(ERate) != len(CRONUS_eff_erate)):
                print "CRONUS data doens't seem to be same length as other data"
            else:
                self.CRNData['CRONUS_erate_g_percm2_peryr'] = CRONUS_eff_erate
                self.CRNData['CRONUS_erate_mm_peryr'] = CRONUS_erate
                self.CRNData['CRONUS_int_uncert_mm_peryr'] = CRONUS_ext_uncert
                self.CRNData['CRONUS_ext_uncert_mm_peryr'] = CRONUS_in_uncert
                self.CRNData['CRONUS_total_uncert'] = np.add(CRONUS_in_uncert,CRONUS_ext_uncert)
                
                self.CRNData['CRONUS_total_uncert'] = np.multiply(self.CRNData['CRONUS_total_uncert'],(2.65/10000))
                
                self.HaveCRONUSData = True
                
                
        else:
            print "Can't open CRONUS file."
        

    # This gets errors between the code and the CRONUS data. 
    # THIS DOES NOT CHECK IF THE CRONUS DATA EXISTS
    def GetErrorsBetweenCRONUS(self):
        ErateLSD = self.CRNData['erate_g_percm2_peryr']
        ErateCRONUS = self.CRNData['CRONUS_erate_g_percm2_peryr']
        
        # get the errors (as a fraction of the erosion rate)
        diffCR = np.subtract(ErateCRONUS,ErateLSD)
        #diffCC = np.abs(diffCC)
        ErrorCR = np.divide(diffCR,ErateLSD)
        
        # add it to the data dictionary
        self.CRNData['Error_CR'] = ErrorCR        
        
        return ErrorCR


    # This gets errors between the various outputs
    def GetErrorsBetweenMethods(self):
        ErateLSD = self.CRNData['erate_g_percm2_peryr']
        ErateCOSMOCALC = self.CRNData['eff_erate_COSMOCALC'] 
        ErateCRONUSlike = self.CRNData['eff_erate_COSMOCALC_emulating_CRONUS']
        
        # get the errors (as a fraction of the erosion rate)
        diffCC = np.subtract(ErateCOSMOCALC,ErateLSD)
        #diffCC = np.abs(diffCC)
        ErrorCC = np.divide(diffCC,ErateLSD)
        
        diffCR = np.subtract(ErateCRONUSlike,ErateLSD)
        ErrorCR = np.divide(diffCR,ErateLSD)
        
        self.CRNData['Error_CC'] = ErrorCC
        self.CRNData['Error_CR_em'] = ErrorCR
        
        return ErrorCC, ErrorCR

            
            
    def PlotERateErrorsGridSpec(self,CRONUSFileName):
 
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        from matplotlib.gridspec import GridSpec
        #from scipy.stats import gaussian_kde

        label_size = 18
        axis_size = 26

        # Set up fonts for plots
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['arial']
        rcParams['font.size'] = label_size
    
        #safi = 1      # Save figures as png (1 to save, otherwise 0):
        #zoom = 1  # zoom in plots activated if value is 1
       
        # Check if you've got the CONUS data: don't read the file if you've already got it        
        if(self.HaveCRONUSData != True):
            self.ReadCRONUSData(CRONUSFileName)
    
        # now get the errors
        self.GetErrorsBetweenMethods()
        self.GetErrorsBetweenCRONUS()
        
        # FIGURE 1 = ERATE COMPARED TO ERATE
        Fig1 = plt.figure(1, facecolor='white',figsize=(12,14))  

        
        # generate a 120,90 grid. 
        gs = GridSpec(140,120,bottom=0.1,left=0.1,right=0.95,top=0.95)

 
        Error_string_CR_BERC = '($\epsilon_{CR}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$ g cm$^{-2}$ yr$^{-1}$'
        Error_string_CC_BERC = '($\epsilon_{CC}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$ g cm$^{-2}$ yr$^{-1}$'
        
        # get the lengths
        #print "The lengths are: "
        #print len(self.CRNData['AvgProdScaling'])
        #print len(self.CRNData['Error_CR'])
        #print len(self.CRNData['basin_relief'])

        ##########################################        
        # Plot 1 = comparison new_code / cosmocalc
        ############################################
        ##       
                
        ax = Fig1.add_subplot(gs[0:40,0:50])
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],"o", markersize=8     )
        plt.scatter(self.CRNData['erate_g_percm2_peryr'],self.CRNData['Error_CR'],
                    c=self.CRNData['basin_relief'], s=50, edgecolor='', 
                    cmap=plt.get_cmap("autumn_r"))

        cbar = plt.colorbar()
        cbar.set_label('Basin Relief (m)')         
        # the basin relief data is in self.CRNData['basin_relief']       
        
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],color=cmap(self.CRNData['basin_relief']),"o", markersize=8     )
        #plt.errorbar(datazz['erate_cosmocalc']*10, datazz['erate_cmperkyr']*10, xerr=datazz['error_cosmocalc'], yerr=datazz['error_newcode'], fmt='o',color = cmap(colo))  
        ax.spines['top'].set_linewidth(2.5)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['right'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5) 
        
        # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
        ax.tick_params(axis='both', width=2.5, pad = 2)
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)
     

        plt.xlabel('Erosion rate in g cm$^{-2}$ yr$^{-1}$', fontsize = axis_size-2, verticalalignment = 'bottom')
        plt.ylabel('($\epsilon_{CR}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$', fontsize = axis_size-4)
        
        # this aligns the labels. 
        # The transform=ax.transAxes means that the coordinate system is the axis coordinate system
        # where x = 0.5 is the centre of the x axis
        ax.xaxis.set_label_coords(0.5, -0.22,transform=ax.transAxes)   


       
        ##########################################        
        # Plot 2 = comparison new_code / cosmocalc
        ############################################
        ##  
        ax = Fig1.add_subplot(gs[0:40,70:120])
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],"o", markersize=8     )
        plt.scatter(self.CRNData['AverageCombinedScaling'],self.CRNData['Error_CR_em'],
                    c=self.CRNData['basin_relief'], s=50, edgecolor='', 
                    cmap=plt.get_cmap("autumn_r"))

        cbar = plt.colorbar()
        cbar.set_label('Basin Relief (m)')         
        # the basin relief data is in self.CRNData['basin_relief']       
        
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],color=cmap(self.CRNData['basin_relief']),"o", markersize=8     )
        #plt.errorbar(datazz['erate_cosmocalc']*10, datazz['erate_cmperkyr']*10, xerr=datazz['error_cosmocalc'], yerr=datazz['error_newcode'], fmt='o',color = cmap(colo))  
        ax.spines['top'].set_linewidth(2.5)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['right'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5) 
        
        # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
        ax.tick_params(axis='both', width=2.5, pad = 2)
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)   
        plt.xlabel('Average combined scaling', fontsize = axis_size-2,verticalalignment = 'bottom')
        plt.ylabel('($\epsilon_{CC}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$', fontsize = axis_size-4)
        
        # this aligns the labels. 
        # The transform=ax.transAxes means that the coordinate system is the axis coordinate system
        # where x = 0.5 is the centre of the x axis
        ax.xaxis.set_label_coords(0.5, -0.22,transform=ax.transAxes)        
        #x = -0.2, y -0.2, 
        #if zoom ==1:
        #    plt.axis([0, 500, 0, 500])
        #plt.title('Comparison between CRNaptious and CRONUS erosion rates',fontsize = label_size+6)
        

        ##########################################        
        # Plot 3 = comparison new_code / cosmocalc
        ############################################
        ##  
        ax = Fig1.add_subplot(gs[50:90, 0:50])
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],"o", markersize=8     )
        plt.scatter(self.CRNData['AverageCombinedScaling'],self.CRNData['Error_CR'],
                    c=self.CRNData['basin_relief'], s=50, edgecolor='', 
                    cmap=plt.get_cmap("autumn_r"))

        cbar = plt.colorbar()
        cbar.set_label('Basin Relief (m)')         
        # the basin relief data is in self.CRNData['basin_relief']       
        
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],color=cmap(self.CRNData['basin_relief']),"o", markersize=8     )
        #plt.errorbar(datazz['erate_cosmocalc']*10, datazz['erate_cmperkyr']*10, xerr=datazz['error_cosmocalc'], yerr=datazz['error_newcode'], fmt='o',color = cmap(colo))  
        ax.spines['top'].set_linewidth(2.5)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['right'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5) 
        
        # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
        ax.tick_params(axis='both', width=2.5, pad = 2)
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)
            
        plt.xlabel('Average combined scaling', fontsize = axis_size-2)
        plt.ylabel('($\epsilon_{CR}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$', fontsize = axis_size-4)
        #if zoom ==1:
        #    plt.axis([0, 500, 0, 500])
        #plt.title('Comparison between CRNaptious and CRONUS erosion rates',fontsize = label_size+6)

        ##########################################        
        # Plot 4 = comparison new_code / cosmocalc
        ############################################
        ##  
        ax = Fig1.add_subplot(gs[50:90,70:120])
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],"o", markersize=8     )
        plt.scatter(self.CRNData['AverageShielding'],self.CRNData['Error_CR'],
                    c=self.CRNData['basin_relief'], s=50, edgecolor='', 
                    cmap=plt.get_cmap("autumn_r"))

        cbar = plt.colorbar()
        cbar.set_label('Basin Relief (m)')         
        # the basin relief data is in self.CRNData['basin_relief']       
        
        # This makes all the spines thick so you can see them         
        ax.spines['top'].set_linewidth(2.5)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['right'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5)
        
        # This gets all the ticks, and pads them away from the axis so that the corners don't overlap
        ax.tick_params(axis='both', width=2.5, pad = 2)
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)
            
        plt.xlabel('Average shielding', fontsize = axis_size-2)
        plt.ylabel('($\epsilon_{CR}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$', fontsize = axis_size-4)



        linetest = np.arange(0,np.max(self.CRNData['erate_g_percm2_peryr']+np.max(self.CRNData['total_uncert'])),0.1)

        CRONUS_err = self.CRNData['CRONUS_total_uncert']
        BERC_err = self.CRNData['total_uncert']          
        
        print "CRONUS error is: "
        print CRONUS_err
        
        print "BERC_err is: "
        print BERC_err

        ##########################################        
        # Plot 5 = comparison new_code / cosmocalc
        ############################################
        ##  
        ax = Fig1.add_subplot(gs[100:140,70:120])
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],"o", markersize=8     )

        #ax.errorbar(self.CRNData['erate_g_percm2_peryr'],self.CRNData['CRONUS_erate_g_percm2_peryr'], 
        #             yerr=[CRONUS_err, np.multiply(CRONUS_err,2)], xerr=[BERC_err, np.multiply(BERC_err,2)],fmt='.',zorder=1)
        ax.errorbar(self.CRNData['erate_g_percm2_peryr'],self.CRNData['CRONUS_erate_g_percm2_peryr'], 
                     yerr=CRONUS_err, xerr=BERC_err,fmt='.',zorder=1)
        cax = ax.scatter(self.CRNData['erate_g_percm2_peryr'],self.CRNData['CRONUS_erate_g_percm2_peryr'],
                   c=self.CRNData['AverageCombinedScaling'], s = 50, edgecolor='', 
                   cmap=plt.get_cmap("cool_r"),zorder=10)
        ax.plot(linetest,linetest,'-k',linewidth=2,zorder=5)        

        cbar = plt.colorbar(cax)
        cbar.set_label('Combined Scaling')         
        # the basin relief data is in self.CRNData['basin_relief']   
        
        axlims = ax.get_xlim()
        ax.set_xlim(0,axlims[1])
        
        
        # This makes all the spines thick so you can see them         
        ax.spines['top'].set_linewidth(2.5)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['right'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5)
        
        # This gets all the ticks, and pads them away from the axis so that the corners don't overlap
        ax.tick_params(axis='both', width=2.5, pad = 2)
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)
            
        plt.xlabel('$\epsilon_{BERC}$ g cm$^{-2}$ yr$^{-1}$', fontsize = axis_size-2)
        plt.ylabel('$\epsilon_{CR}$ g cm$^{-2}$ yr$^{-1}$', fontsize = axis_size-4)

        plt.savefig('yo.png', format='png')
        #plt.show()        
    
    # read here about colourmaps: http://matplotlib.org/users/colormaps.html         
    def PlotERateErrorsRefined(self,CRONUSFileName):
 
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        from matplotlib.gridspec import GridSpec
        #from scipy.stats import gaussian_kde

        label_size = 18
        axis_size = 26

        # Set up fonts for plots
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['arial']
        rcParams['font.size'] = label_size
    
        #safi = 1      # Save figures as png (1 to save, otherwise 0):
        #zoom = 1  # zoom in plots activated if value is 1
       
        # Check if you've got the CONUS data: don't read the file if you've already got it        
        if(self.HaveCRONUSData != True):
            self.ReadCRONUSData(CRONUSFileName)
    
        # now get the errors
        self.GetErrorsBetweenMethods()
        self.GetErrorsBetweenCRONUS()
        
        # FIGURE 1 = ERATE COMPARED TO ERATE
        Fig1 = plt.figure(1, facecolor='white',figsize=(12,9))  

        
        # generate a 120,90 grid. 
        gs = GridSpec(90,120,bottom=0.1,left=0.1,right=0.95,top=0.95)

 
        Error_string_CR_BERC = '($\epsilon_{CR}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$ g cm$^{-2}$ yr$^{-1}$'
        Error_string_CC_BERC = '($\epsilon_{CC}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$ g cm$^{-2}$ yr$^{-1}$'
        
        # get the lengths
        #print "The lengths are: "
        #print len(self.CRNData['AvgProdScaling'])
        #print len(self.CRNData['Error_CR'])
        #print len(self.CRNData['basin_relief'])

        ##########################################        
        # Plot 1 = comparison new_code / cosmocalc
        ############################################
        ##       
                
        ax = Fig1.add_subplot(gs[0:40,0:50])
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],"o", markersize=8     )
        cax = plt.scatter(self.CRNData['erate_g_percm2_peryr'],self.CRNData['Error_CR'],
                    c=self.CRNData['AverageCombinedScaling'], s=50, edgecolor='', 
                    cmap=plt.get_cmap("summer"))

        cbar = plt.colorbar(cax)
        cbar.set_label('Combined Scaling')         
        # the basin relief data is in self.CRNData['basin_relief']       
        
        #plt.plot(self.CRNData['AvgProdScaling'],self.CRNData['Error_CR'],color=cmap(self.CRNData['basin_relief']),"o", markersize=8     )
        #plt.errorbar(datazz['erate_cosmocalc']*10, datazz['erate_cmperkyr']*10, xerr=datazz['error_cosmocalc'], yerr=datazz['error_newcode'], fmt='o',color = cmap(colo))  
        ax.spines['top'].set_linewidth(2.5)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['right'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5) 
        
        # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
        ax.tick_params(axis='both', width=2.5, pad = 2)
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)
     

        plt.xlabel('Erosion rate in g cm$^{-2}$ yr$^{-1}$', fontsize = axis_size-2, verticalalignment = 'bottom')
        plt.ylabel('($\epsilon_{CR}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$', fontsize = axis_size-4)
        
        # this aligns the labels. 
        # The transform=ax.transAxes means that the coordinate system is the axis coordinate system
        # where x = 0.5 is the centre of the x axis
        ax.xaxis.set_label_coords(0.5, -0.22,transform=ax.transAxes)   


       
        ##########################################        
        # Plot 2 = comparison new_code / cosmocalc
        ############################################
        ##  
        ax = Fig1.add_subplot(gs[0:40,70:120])
        cax = plt.scatter(self.CRNData['AverageCombinedScaling'],self.CRNData['Error_CR'],
                    c=self.CRNData['AverageShielding'], s=50, edgecolor='', 
                    cmap=plt.get_cmap("hot"))

        cbar = plt.colorbar(cax)
        cbar.set_label('Average shielding')         
        
        ax.spines['top'].set_linewidth(2.5)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['right'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5) 
        
        # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
        ax.tick_params(axis='both', width=2.5, pad = 2)
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)
            
        plt.xlabel('Average shielding', fontsize = axis_size-2)
        plt.ylabel('($\epsilon_{CR}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$', fontsize = axis_size-4)


        ##########################################        
        # Plot 3 = comparison new_code / cosmocalc
        ############################################
        ##  
        ax = Fig1.add_subplot(gs[50:90, 0:50])
 
        cax = plt.scatter(self.CRNData['AverageCombinedScaling'],self.CRNData['Error_CR_em'],
                    c=self.CRNData['erate_g_percm2_peryr'], s=50, edgecolor='', 
                    cmap=plt.get_cmap("YlGnBu"))

        cbar = plt.colorbar(cax)
        cbar.set_label('Erosion rate (g cm$^{-2}$ yr$^{-1}$)')         
        ax.spines['top'].set_linewidth(2.5)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['right'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5) 
        
        # This gets all the ticks, and pads them away from the axis so that the corners don't overlap        
        ax.tick_params(axis='both', width=2.5, pad = 2)
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)   
        plt.xlabel('Average combined scaling', fontsize = axis_size-2,verticalalignment = 'bottom')
        plt.ylabel('($\epsilon_{CC}$-$\epsilon_{BERC}$)/$\epsilon_{BERC}$', fontsize = axis_size-4)
        
        # this aligns the labels. 
        # The transform=ax.transAxes means that the coordinate system is the axis coordinate system
        # where x = 0.5 is the centre of the x axis
        ax.xaxis.set_label_coords(0.5, -0.22,transform=ax.transAxes)       

        ##########################################        
        # Plot 4 = comparison new_code / cosmocalc
        ############################################
        ##  
        ax = Fig1.add_subplot(gs[50:90,70:120])

        linetest = np.arange(0,np.max(self.CRNData['erate_g_percm2_peryr']+np.max(self.CRNData['total_uncert'])),0.01)
        
        print "Here is the line"
        print linetest
        
        print "max: "
        print np.max(self.CRNData['erate_g_percm2_peryr']+np.max(self.CRNData['total_uncert']))
        
        #print "err: "
        #print 

        CRONUS_err = self.CRNData['CRONUS_total_uncert']
        BERC_err = self.CRNData['total_uncert']      
        

        ax.errorbar(self.CRNData['erate_g_percm2_peryr'],self.CRNData['CRONUS_erate_g_percm2_peryr'], 
                     yerr=CRONUS_err, xerr=BERC_err,fmt='.',zorder=1)
        cax = ax.scatter(self.CRNData['erate_g_percm2_peryr'],self.CRNData['CRONUS_erate_g_percm2_peryr'],
                   c=self.CRNData['AverageCombinedScaling'], s = 50, edgecolor='', 
                   cmap=plt.get_cmap("summer"),zorder=10)
        ax.plot(linetest,linetest,'-k',linewidth=2,zorder=5)        

        cbar = plt.colorbar(cax)
        cbar.set_label('Combined Scaling')         
        # the basin relief data is in self.CRNData['basin_relief']   
        
        axlims = ax.get_xlim()
        ax.set_xlim(0,axlims[1])
        
        
        # This makes all the spines thick so you can see them         
        ax.spines['top'].set_linewidth(2.5)
        ax.spines['left'].set_linewidth(2.5)
        ax.spines['right'].set_linewidth(2.5)
        ax.spines['bottom'].set_linewidth(2.5)
        
        # This gets all the ticks, and pads them away from the axis so that the corners don't overlap
        ax.tick_params(axis='both', width=2.5, pad = 2)
        for tick in ax.xaxis.get_major_ticks():
            tick.set_pad(10)
            
        plt.xlabel('$\epsilon_{BERC}$ g cm$^{-2}$ yr$^{-1}$', fontsize = axis_size-2)
        plt.ylabel('$\epsilon_{CR}$ g cm$^{-2}$ yr$^{-1}$', fontsize = axis_size-4)

        figname = LSDOst.GetPath(CRONUSFileName)+'Erate_comparison.pdf'
        plt.savefig(figname, format='pdf')
        #plt.show()       
    
    #==========================================================================    
    #==========================================================================
    # Get data elements
    def GetParameterNames(self,PrintToScreen = False):
        
        if PrintToScreen:        
            print self.VariableList
            
        return self.VariableList 

    def GetErosionRates(self,PrintToScreen = False):
        ERate = self.CRNData['erate_g_percm2_peryr']
        
        if PrintToScreen:
            print ERate
        return ERate

    def GetErosionRates_mmperkyr_rho2650(self,PrintToScreen = False):
        ERate = self.CRNData['erate_mmperkyr_rho2650']
        
        if PrintToScreen:
            print ERate
        return ERate

    def GetErosionRatesUncert(self,PrintToScreen = False):
        ERateU = self.CRNData['total_uncert']
        
        if PrintToScreen:
            print ERateU
        return ERateU

    def GetCRONUSErosionRates(self,PrintToScreen = False):
        ERate = self.CRNData['CRONUS_erate_g_percm2_peryr']
        
        if PrintToScreen:
            print ERate
        return ERate

    def GetCRONUSErosionRatesUncert(self,PrintToScreen = False):
        ERateU = self.CRNData['CRONUS_total_uncert']
        
        if PrintToScreen:
            print ERateU
        return ERateU


    def GetSampleName(self,PrintToScreen = False):
        SampleName = self.CRNData['sample_name']
        
        if PrintToScreen:
            print SampleName
        return SampleName

    def GetNuclide(self,PrintToScreen = False):
        Nuclide = self.CRNData['nuclide']
        
        if PrintToScreen:
            print Nuclide
        return Nuclide

    def GetLatitude(self,PrintToScreen = False):
        Latitude = self.CRNData['latitude'] 
        
        if PrintToScreen:
            print Latitude
        return Latitude

    def GetLongitude(self,PrintToScreen = False):
        Longitude = self.CRNData['longitude'] 
        
        if PrintToScreen:
            print Longitude
        return Longitude

    def GetError_CR(self,PrintToScreen = False):
        ErrorCR = self.CRNData['Error_CR'] 
        
        if PrintToScreen:
            print ErrorCR
        return ErrorCR        

    def GetError_CC(self,PrintToScreen = False):
        ErrorCC = self.CRNData['Error_CC'] 
        
        if PrintToScreen:
            print ErrorCC
        return ErrorCC  

    def GetError_CR_em(self,PrintToScreen = False):
        ErrorCR_em = self.CRNData['Error_CR_em'] 
        
        if PrintToScreen:
            print ErrorCR_em
        return ErrorCR_em       

    def GetAverageCombinedScaling(self,PrintToScreen = False):
        Scale = self.CRNData['AverageCombinedScaling'] 
        
        if PrintToScreen:
            print Scale
        return Scale   
        
    #==========================================================================
    #==========================================================================        



    # This translates the CRNData object to an Esri shapefile
    def TranslateToReducedShapefile(self,FileName):
        # Parse a delimited text file of volcano data and create a shapefile

        import osgeo.ogr as ogr
        import osgeo.osr as osr


        #  set up the shapefile driver
        driver = ogr.GetDriverByName("ESRI Shapefile")

        # Get the path to the file
        this_path = LSDOst.GetPath(FileName)
        DataName = self.FilePrefix
        
        FileOut = this_path+DataName+".shp"
        
        #print "The filename will be: " + FileOut

        # delete the existing file
        if os.path.exists(FileOut):
            driver.DeleteDataSource(FileOut)

        # create the data source
        data_source = driver.CreateDataSource(FileOut)
        
        # create the spatial reference, in this case WGS84 (which is ESPG 4326)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)

        print "Creating the layer"

        # create the layer
        layer = data_source.CreateLayer("CRNData", srs, ogr.wkbPoint)

        print "Adding the field names"

        # Add the fields we're interested in
        field_name = ogr.FieldDefn("SampleName", ogr.OFTString)
        field_name.SetWidth(24)
        layer.CreateField(field_name)
        field_region = ogr.FieldDefn("Nuclide", ogr.OFTString)
        field_region.SetWidth(24)
        layer.CreateField(field_region)
        layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("EffERate", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("EffERateU", ogr.OFTReal))

        sample_name = self.GetSampleName()
        nuclide = self.GetNuclide()
        Latitude = self.GetLatitude()
        Longitude = self.GetLongitude()
        ERateU = self.GetErosionRatesUncert()
        ERate = self.GetErosionRates()
        
        #print "lengths are: "
        #print "SN: " + str(len(sample_name))
        #print "N: " + str(len(Latitude))
        #print "Lat: " + str(len(nuclide))
        #print "Long: " + str(len(Longitude))
        #print "Erate: " + str(len(ERate))
        #print "ErateU: " + str(len(ERateU))
        
        # Process the text file and add the attributes and features to the shapefile
        for index,name in enumerate(sample_name):
            
            # create the feature
            feature = ogr.Feature(layer.GetLayerDefn())
            
            # Set the attributes using the values from the delimited text file
            feature.SetField("SampleName", name)
            feature.SetField("Nuclide", nuclide[index])
            feature.SetField("Latitude", Latitude[index])
            feature.SetField("Longitude", Longitude[index])
            feature.SetField("EffERate", ERate[index])
            feature.SetField("EffERateU", ERateU[index])

            # create the WKT for the feature using Python string formatting
            wkt = "POINT(%f %f)" %  (float(Longitude[index]), float(Latitude[index]))

            # Create the point from the Well Known Txt
            point = ogr.CreateGeometryFromWkt(wkt)

            # Set the feature geometry using the point
            feature.SetGeometry(point)
            # Create the feature in the layer (shapefile)
            layer.CreateFeature(feature)
            # Destroy the feature to free resources
            feature.Destroy()

        # Destroy the data source to free resources
        data_source.Destroy()


    # This translates the CRNData object to an GeoJSON
    def TranslateToReducedGeoJSON(self,FileName):
        # Parse a delimited text file of volcano data and create a shapefile

        import osgeo.ogr as ogr
        import osgeo.osr as osr


        #  set up the shapefile driver
        driver = ogr.GetDriverByName("GeoJSON")

        # Get the path to the file
        this_path = LSDOst.GetPath(FileName)
        DataName = self.FilePrefix
        
        FileOut = this_path+DataName+".geojson"
        
        print "The filename will be: " + FileOut

        # delete the existing file
        if os.path.exists(FileOut):
            driver.DeleteDataSource(FileOut)

        # create the data source
        data_source = driver.CreateDataSource(FileOut)
        
        # create the spatial reference,  in this case WGS84 (which is ESPG 4326)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)

        print "Creating the layer"

        # create the layer
        layer = data_source.CreateLayer("CRNData", srs, ogr.wkbPoint)

        #print "Adding the field names"

        # Add the fields we're interested in
        field_name = ogr.FieldDefn("SampleName", ogr.OFTString)
        field_name.SetWidth(48)
        layer.CreateField(field_name)
        field_region = ogr.FieldDefn("Nuclide", ogr.OFTString)
        field_region.SetWidth(48)
        layer.CreateField(field_region)
        layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("EffERate", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("EffERateU", ogr.OFTReal))

        sample_name = self.GetSampleName()
        nuclide = self.GetNuclide()
        Latitude = self.GetLatitude()
        Longitude = self.GetLongitude()
        ERateU = self.GetErosionRatesUncert()
        ERate = self.GetErosionRates()
        
        #print "lengths are: "
        #print "SN: " + str(len(sample_name))
        #print "N: " + str(len(Latitude))
        #print "Lat: " + str(len(nuclide))
        #print "Long: " + str(len(Longitude))
        #print "Erate: " + str(len(ERate))
        #print "ErateU: " + str(len(ERateU))
        
        # Process the text file and add the attributes and features to the shapefile
        for index,name in enumerate(sample_name):
            
            # create the feature
            feature = ogr.Feature(layer.GetLayerDefn())
            
            # Set the attributes using the values from the delimited text file
            feature.SetField("SampleName", name)
            feature.SetField("Nuclide", nuclide[index])
            feature.SetField("Latitude", Latitude[index])
            feature.SetField("Longitude", Longitude[index])
            feature.SetField("EffERate", ERate[index])
            feature.SetField("EffERateU", ERateU[index])

            # create the WKT for the feature using Python string formatting
            wkt = "POINT(%f %f)" %  (float(Longitude[index]), float(Latitude[index]))

            # Create the point from the Well Known Txt
            point = ogr.CreateGeometryFromWkt(wkt)

            # Set the feature geometry using the point
            feature.SetGeometry(point)
            # Create the feature in the layer (shapefile)
            layer.CreateFeature(feature)
            # Destroy the feature to free resources
            feature.Destroy()

        # Destroy the data source to free resources
        data_source.Destroy()

                