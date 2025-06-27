import numpy as np
import pandas as pd
import h5py as hf
from glob import glob

def bin_data(
    df = None,
    filename = None,
    filetype="hdf",
    n_bin=100,
    key_list = None
):
    """Function that sorts the raw hour averaged data into radial bins 

    Args:
        df (_type_, optional): Datafram to bin. Defaults to None.
        filename (_type_, optional): File being saved to. Defaults to None.
        filetype (str, optional): File type of binned file, hdf is the only option right now. Defaults to "pickle".
        n_bin (int, optional): Number of bins. Defaults to 100.
        key_list (_type_, optional): _description_. Defaults to None.
    """
    r_min = -1.4
    r_max = 2
    #n_bin = 85
    r_bin = np.logspace(r_min, r_max, n_bin)
    n_key_list = [
                    "Tp",
                    "bm",
                    "np",
                    "vp_m",
                    "sc_r"
                ]
    dfn = pd.DataFrame()
    for key in n_key_list:
        dfn[key + "_median"] = np.full(n_bin, np.nan)
        dfn[key + "_iqr_10"] = np.full(n_bin, np.nan)
        dfn[key + "_iqr_25"] = np.full(n_bin, np.nan)
        dfn[key + "_iqr_50"] = np.full(n_bin, np.nan)
        dfn[key + "_iqr_75"] = np.full(n_bin, np.nan)
        dfn[key + "_iqr_90"] = np.full(n_bin, np.nan)
        dfn[key + "_num"] = np.full(n_bin, np.nan)
        
        for ind in range(len(r_bin) - 1):
            try:
                df.loc[df[key] < -1e-10, key] = np.nan
                dat = df[key][
                    (df.sc_r > r_bin[ind]) & (df.sc_r <= r_bin[ind + 1]) & (~np.isnan(df[key]))
                ]

                # dfn[key+'_mean'][ind] = dat.mean()
                dfn.loc[ind, key + "_median"] = dat.median()
                dfn.loc[ind, key + "_iqr_10"] = dat.quantile(0.1)
                dfn.loc[ind, key + "_iqr_25"] = dat.quantile(0.25)
                dfn.loc[ind, key + "_iqr_50"] = dat.quantile(0.50)
                dfn.loc[ind, key + "_iqr_75"] = dat.quantile(0.75)
                dfn.loc[ind, key + "_iqr_90"] = dat.quantile(0.90)
                dfn.loc[ind, key + "_num"] = len(dat)
            except:
                # print(key+'_mean values set to NaN')
                pass
    
    if "hdf" in filetype:
        fn = f"{filename}.hf"
        dfn.to_hdf(fn, key="df", mode="w")
        print("Data written for HDF file")
        
    return dfn

def time_separate(fname, start_times, end_times, save_file, sc):
    """Function to separate individual spacecraft binned data into 
    files 

    Args:
        fname (string): file name for the data to be pulled from
        start_times (Array of datetime objects): Array of start times
        end_times (Array of datetime objects): Array of end times
    """
    df = pd.read_hdf(fname)
    slices = []
    for n in range(len(start_times)):
        if (sc =="mariner10" or sc == "cassini"):
            pass
        else:
            offset = (df["sc_r"] - 1) / df["vp_m"]  # time delay in seconds
            offset = offset.replace([np.inf, -np.inf], np.nan).fillna(0)
            offset = pd.to_timedelta(offset, unit='s')
            adjusted_time = df["Epoch"] + offset  # shift timestamps forward
            mask = (adjusted_time >= start_times[n]) & (adjusted_time <= end_times[n])
            slices.append(df.loc[mask])
    df_out = pd.concat(slices, axis=0, )
    df_out.to_hdf(save_file,key = 'data', mode='w')