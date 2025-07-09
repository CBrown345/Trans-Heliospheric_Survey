from spacepy.pycdf import CDF as cdf
import numpy as np
import pandas as pd
import datetime
from glob import glob
import h5py as hf
import time
start = time.time()

sc = "cassini"
data_dir = f"Data_Raw/COHO1HR_Merged_Individual/{sc}/"
save_dir = f"Data_Processed/Individual/{sc}/"
fnames = np.sort(glob(data_dir + f"*/*.cdf", recursive = True)) #recursively grab all files for psp
#print(fnames)
print(f"A total of {len(fnames)} related files found")

df = None
df_arr = []
count = 0

for fname in fnames:
    #print(fname[-16:-8])
    #create a dictionary with the cdf files
    d = {}
    dat = cdf(fname)
    d["Epoch"] = dat["Epoch"][:]
    d["bm"] = dat["B_mag"][:]
    d["np"] = np.full_like(dat["B_mag"][:], np.nan, dtype=float)
    d["vp_m"] = np.full_like(dat["B_mag"][:], np.nan, dtype=float)
    d["Tp"] = np.full_like(dat["B_mag"][:], np.nan, dtype=float)
    d["sc_r"] = dat["sc_r"][:]
    d['heliographicLatitude'] = dat["sc_lat"][:]
    d['heliographicLongitude'] = dat["sc_long"][:]
    #resample everything to exactly 1hr, to avoid any weirdness if the timestamps are slightly off
    df = pd.DataFrame(d, index=d["Epoch"])
    for col in df.select_dtypes(include=[np.number]).columns:# filter out bad data
        df[col] = df[col].apply(
        lambda x: np.nan if pd.api.types.is_number(x) and np.isclose(x, -1.0e31) else x
        )   
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
compiled_file = f"{save_dir}{sc}_unbinned_{fnames[0][-16:-8]}_{fnames[-1][-16:-8]}.hf"
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