#!/bin/env python
"""
Author: Pin-Ching Li
This script is created on 04/29/2020
This script aims to visualize annual and monthly statsitical metrics 
Also, return period is calculated and visualized
"""

import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from datetime import datetime, timedelta
import numpy as np

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    # find the index of negative discharge data
    Negative_index= DataDF[DataDF["Discharge"]<0].index
    # drop those data as a gross error
    DataDF.drop(Negative_index, inplace=True)
    
    return( DataDF, MissingValues )

def ReadMetrics( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    the metrics from the assignment on descriptive statistics and 
    environmental metrics.  Works for both annual and monthly metrics. 
    Date column should be used as the index for the new dataframe.  Function 
    returns the completed DataFrame."""
    
    # define column names
    Metrics = pd.read_csv(fileName,header=0,parse_dates=['Date'])
    return( Metrics )

def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    # transfer start date and end date into datetime format
    D_start =datetime.strptime(startDate, '%Y-%m-%d')
    D_end   =datetime.strptime(endDate,'%Y-%m-%d')
    # find the index of negative discharge data
    less_index  = DataDF[DataDF.index<D_start].index
    larger_index= DataDF[DataDF.index>D_end].index
    # drop the data points with date before startdate
    DataDF.drop(less_index, inplace=True)
    DataDF.drop(larger_index,inplace=True)
    # report missing values
    MissingValues = DataDF['Discharge'].isna().sum()
    return( DataDF, MissingValues )
    
def GetMonthlyAverages(MoDataDF):
    """This function calculates annual average monthly values for all 
    statistics and metrics.  The routine returns an array of mean values 
    for each metric in the original dataframe."""
    Mon_avg = []
    for i in range(12):
        Mon_avg.append(MoDataDF.iloc[i:600:12].mean())
    MonthlyAverages = pd.DataFrame(Mon_avg,index=[10,11,12,1,2,3,4,5,6,7,8,9])
    MonthlyAverages = MonthlyAverages.sort_index()
    return( MonthlyAverages )


# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define full river names as a dictionary so that abbreviations are not used in figures
    riverName = { "Wildcat": "Wildcat Creek",
                  "Tippe": "Tippecanoe River" }
    
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }
    
    MetricsName={"Annual":"Annual_Metrics.csv",
                 "Monthly":"Monthly_Metrics.csv"}
    # define blank dictionaries (these will use the same keys as fileName)
    DataDF = {}
    Metrics= {}
    MissingValues = {}
    WYDataDF = {}
    MoDataDF = {}
    AnnualAverages = {}
    MonthlyAverages = {}
    for file in fileName.keys():
        
        print( "\n", "="*50, "\n  Working on {} \n".format(file), "="*50, "\n" )
        
        # read the file
        DataDF[file], MissingValues[file] = ReadData(fileName[file])
        print( "-"*50, "\n\nRaw data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))
        
        # clip to consistent period
        DataDF[file], MissingValues[file] = ClipData( DataDF[file], '2014-10-01', '2019-09-30' )
        print( "-"*50, "\n\nSelected period data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))


    label = ['Wildcat','Tippe']
    # Read Metrics
    AM = ReadMetrics(MetricsName['Annual'])   
    MM = ReadMetrics(MetricsName['Monthly'])
    
    AM_WC = AM.loc[AM['Station']==label[0]]
    AM_TP = AM.loc[AM['Station']==label[1]]
    MM_WC = MM.loc[MM['Station']==label[0]]
    MM_TP = MM.loc[MM['Station']==label[1]]
    AM_WC.Date = pd.to_datetime(AM_WC.Date)
    AM_TP.Date = pd.to_datetime(AM_TP.Date)
    MM_WC.Date = pd.to_datetime(MM_WC.Date)
    MM_TP.Date = pd.to_datetime(MM_TP.Date)
    # plot daily flow for both streams for the last 5 years
    plt.plot(DataDF[label[0]].index,DataDF[label[0]].Discharge,
             label=riverName[label[0]],color ='k')
    plt.plot(DataDF[label[1]].index,DataDF[label[1]].Discharge,
             label=riverName[label[1]], color ='r')
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Discharge (cfs)')
    plt.title('Fig.1 Daily Streamflow for last 5 years of the record')
    plt.savefig('Daily_Flow_5y.png',dpi=96)   
    plt.show()
    plt.close()
    # plot annual coefficient of variation, TQmean, and R-B index
    # Coeff Var
    AM_WC['Coeff Var'] = pd.to_numeric(AM_WC['Coeff Var'], errors='coerce')
    AM_TP['Coeff Var'] = pd.to_numeric(AM_TP['Coeff Var'], errors='coerce')
    plt.plot(AM_WC.Date,AM_WC['Coeff Var'],
             label=riverName[label[0]],color ='k')
    plt.plot(AM_TP.Date,AM_TP['Coeff Var'],
             label=riverName[label[1]], color ='r')
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Coefficient of Variation')
    plt.yticks(np.arange(0,250,step=25))
    plt.title('Fig.2 Annual Coefficient of Variation') 
    plt.savefig('Annual_coeff_Var.png',dpi=96) 
    plt.show()
    plt.close()

    # Tqmean
    AM_WC['Tqmean'] = pd.to_numeric(AM_WC['Tqmean'], errors='coerce')
    AM_TP['Tqmean'] = pd.to_numeric(AM_TP['Tqmean'], errors='coerce')
    plt.plot(AM_WC.Date,AM_WC['Tqmean'],
             label=riverName[label[0]],color ='k')
    plt.plot(AM_TP.Date,AM_TP['Tqmean'],
             label=riverName[label[1]], color ='r')
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('TQmean')
    plt.title('Fig.3 Annual TQmean')
    plt.savefig('Annual_Tqmean.png',dpi=96)
    plt.show()
    plt.close()
    # RB index
    AM_WC['R-B index'] = pd.to_numeric(AM_WC['R-B index'], errors='coerce')
    AM_TP['R-B index'] = pd.to_numeric(AM_TP['R-B index'], errors='coerce')
    plt.plot(AM_WC.Date,AM_WC['R-B index'],
             label=riverName[label[0]],color ='k')
    plt.plot(AM_TP.Date,AM_TP['R-B index'],
             label=riverName[label[1]], color ='r')
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('R-B index')
    plt.title('Fig.4 Annual R-B index')
    plt.savefig('Annual_R-B_index.png',dpi=96)
    plt.show()
    plt.close()
   
    # Average annual monthly flow
    # Mean flow from object to float
    MM_WC['Mean Flow'] = pd.to_numeric(MM_WC['Mean Flow'], errors='coerce')
    MM_TP['Mean Flow'] = pd.to_numeric(MM_TP['Mean Flow'], errors='coerce')
    # get average annual monthly flow
    AV_MM_WC = GetMonthlyAverages(MM_WC)
    AV_MM_TP = GetMonthlyAverages(MM_TP)
    plt.plot(AV_MM_WC['Mean Flow'],
             label=riverName[label[0]],color ='k')
    plt.plot(AV_MM_TP['Mean Flow'],
             label=riverName[label[1]], color ='r')
    plt.legend()
    plt.xlabel('Month')
    plt.ylabel('Average Annual Monthly Flow (cfs)')
    plt.xticks(np.arange(1,13,step=1))
    plt.title('Fig.5 Average Annual Monthly Flow')
    plt.savefig('Average_Annual_Monthly_Flow.png',dpi=96)   
    plt.show()
    plt.close()
    
    # Return Period of annua peak flow events
    AM_WC_peak = pd.to_numeric(AM_WC['Peak Flow'], errors='coerce')
    AM_TP_peak = pd.to_numeric(AM_TP['Peak Flow'], errors='coerce')
    # sort peak series
    AM_WC_peak = AM_WC_peak.sort_values(ascending=False)
    AM_TP_peak = AM_TP_peak.sort_values(ascending=False)
    exceed =[]
    for i in range(1,AM_WC_peak.size+1):
        ex_p = i/(AM_WC_peak.size+1)
        exceed.append(ex_p)
    
    plt.scatter(exceed,AM_WC_peak,
             label=riverName[label[0]],color ='k')
    plt.scatter(exceed,AM_TP_peak,
             label=riverName[label[1]], color ='r')
    plt.legend()
    plt.xlabel('Exceedence Probability')
    plt.ylabel('Peak Discharge (cfs)')
    plt.title('Fig.6 Return Period of Annual Peak Flow Events')
    plt.savefig('Return_Period_Peak_Flow.png',dpi=96)
    plt.show()
    plt.close()  
    