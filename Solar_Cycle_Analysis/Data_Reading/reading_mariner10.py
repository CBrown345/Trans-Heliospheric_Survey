from spacepy.pycdf import CDF as cdf
import numpy as np
import pandas as pd
import datetime
from glob import glob
import h5py as hf
import time
start = time.time()
"""
    Data Format:

 The following write statement in M10MAGHR.for specifies the output
 formatting for the M10MAGyy.asc files:

      WRITE(20,150) IYR,IDAY,IHR,RAD,NCARR,HLON,HLAT,ESSANG,BXSEQ,
     *   BYSEQ,BZSEQ,BMAG,ELANG,AZANG
 150  FORMAT(1X,I4,1X,I3,1X,I2,1X,1PE11.3,1X,I4,1X,9(1PE11.3))

 The output parameters are defined as follows:

 IYR     YEAR OF THE DATA INTERVAL (LAST TWO DIGITS ONLY).                           
 IDAY    DAY OF THE DATA INTERVAL FROM THE FIRST DAY OF THE ABOVE                    
            YEAR; JAN. 1 = DAY 1 !                                                      
 IHR     HOUR OF THE DAY OF THE DATA INTERVAL.                                                         
 RAD     SPACECRAFT HELIOCENTRIC DISTANCE IN ASTRONOMICAL UNITS.                     
 NCARR   CARRINGTON ROTATION NUMBER AS SEEN BY AN EARTH BASED                        
            OBSERVER AT THE START OF THE DATA INTERVAL                                  
 HLON    CARRINGTON LONGITUDE OF THE SUBSPACECRAFT POINT ON THE SUN AT THE           
            START OF THE DATA INTERVAL, IN DEGREES (0-360).                             
 HLAT    HELIOGRAPHIC LATITUDE OF THE SUBSPACECRAFT POINT AT THE START               
            OF THE DATA INTERVAL IN DEGREES (+,-90).                                    
 ESSANG  EARTH-SUN-SPACECRAFT SEPARATION ANGLE IN DEGREES (0-360)                    
            MEASURED COUNTERCLOCKWISE FROM THE EARTH-SUN LINE LOOKING                   
            DOWN FROM THE NORTH.                                                        
 BXSEQ   THE COMPONENT OF THE INTERPLANETARY MAGNETIC FIELD ALONG             
            THE X AXIS IN THE SOLAR EQUATORIAL SYSTEM, POSITIVE                         
            TOWARD THE SUN (IN NANOTESLAS). (BEHANNON AND OTTENS,1976).                 
 BYSEQ   SAME AS WORD 12 FOR THE Y AXIS COMPONENT.                             
 BZSEQ   SAME AS WORD 12 FOR THE Z AXIS COMPONENT.                            
 BMAG    THE TOTAL MAGNITUDE OF THE MAGNETIC FIELD VECTOR (IN NANO-                  
            TESLAS).                                                                    
 ELANG   THE ELEVATION ANGLE ,THETA, OF THE MAGNETIC FIELD VECTOR IN THE             
            SOLAR EQUATORIAL COORDINATE SYSTEM.                                         
 AZANG   THE AZIMUTH ANGLE, PHI, OF THE MAGNETIC FIELD VECTOR IN THE SOLAR           
            EQUATORIAL COORDINATE SYSTEM. 
"""

sc = "mariner10"
data_dir1 = f"Data_Raw/COHO1HR_Merged_Individual/mariner10/m10mag73.asc.txt"
data_dir2 = f"Data_Raw/COHO1HR_Merged_Individual/mariner10/m10mag74.asc.txt"
save_dir = f"Data_Processed/Individual/{sc}/"
#print(fnames)
df = None
df_arr = []
count = 0

for data_dir in [data_dir1, data_dir2]:
    d = {}
    dat = pd.read_csv(data_dir, delim_whitespace=True, header = None)
    d["Epoch"] = pd.to_datetime(dat[0].astype(str) + dat[1].astype(str).str.zfill(3), format="%Y%j") + pd.to_timedelta(dat[2], unit="h")
    epoch = d["Epoch"]
    epoch.name = None
    #print(d["Epoch"])
    d["bm"] = dat[11]#new horizons didnt measure magnetic field :(
    # d["np"] = dat["n"]
    # d["vp_m"] = dat["v"][:]
    # d["Tp"] = dat["t"][:]
    d["sc_r"] = dat[3]
    d['heliographicLatitude'] = dat[6]
    d['heliographicLongitude'] = dat[5]
    df = pd.DataFrame(d)
    df.index = epoch
    for col in df.select_dtypes(include=[np.number]).columns:# filter out bad data
         df[col] = df[col].apply(lambda x: np.nan if np.isclose(x, -1.0e31) else x)
    print(d)
    print(df)
    #resample everything to exactly 1hr, to avoid any weirdness if the timestamps are slightly off
    dfr = df.resample('3600s').mean()
    dfr.index=dfr.index.tz_localize('UTC')
    dfr.insert(0,'ssepoch',pd.Series(dfr.index,index=dfr.index).apply(datetime.datetime.timestamp))
    
    df_arr.append(dfr)
    #Alternative code to create individual .hf files for the different months
    # save_file = f"{save_dir}{sc}_unbinned_{fname[-16:-8]}.hf"
    # hdf = hf.File(save_file, 'w')
    # hdf.create_dataset('datetime', data=(pd.Series(dfr.index) - pd.Timestamp('1970-01-01T00:00:00Z')).dt.total_seconds())
    # for i in dfr.columns[1:]:
    #     hdf.create_dataset(i, data=np.array(dfr[i]))
    # hdf.close()

df_t = pd.concat(df_arr)
compiled_file = f"{save_dir}{sc}_unbinned_20080101_20241201.hf"
# Ramiz's version of compiling the individual dataframes, alternative method I used lets me read them with pandas. 
# I don't completely understand why, but it works
# hdf = hf.File(compiled_file, 'w')
# hdf.create_dataset('datetime', data=(pd.Series(df_t.index) - pd.Timestamp('1970-01-01T00:00:00Z')).dt.total_seconds())
# for i in df_t.select_dtypes(exclude=['datetime64[ns]']).columns:
#     hdf.create_dataset(i, data=np.array(df_t[i]))
# hdf.close()
df_t = df_t.copy()
df_t['ssepoch'] =  df_t.index.tz_localize(None).astype('datetime64[s]').astype('int')
df_t = df_t.reset_index(drop=True)
df_t.to_hdf(compiled_file, key='data', mode='w')
print(f"Data saved to file {compiled_file}")
print( f"It took {np.round(time.time() - start, 2)} seconds to run the code")