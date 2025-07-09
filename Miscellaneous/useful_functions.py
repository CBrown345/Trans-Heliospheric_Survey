import numpy as np
import pandas as pd
import h5py as hf
from glob import glob
import pytz
from scipy.interpolate import interp1d as spl
def bin_data(
    df = None,
    filename = None,
    filetype="hdf",
    n_bin=85,
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
def scale_data(df = None, key_list = None):
    """_summary_

    Args:
        df (Pandas Dataframe, optional): Dataframe of unbinned spacecraft data. Defaults to None.
        key_list (array of str, optional): List of Keys in spacecraft data. Defaults to None.

    Returns:
        pandas dataframe: scaled, unbinned dataframe 
    """
    df.set_index("Epoch", inplace=True)
    if df.index.tz is None:
        df.index = df.index.tz_localize(pytz.utc)
    else:
        df.index = df.index.tz_convert(pytz.utc)
    au = 1.496e8
    df_omni_o = pd.read_hdf("Data_Processed/Individual/omni/omni_unbinned_19630101_20250601.hf")
    df_omni_o["Epoch"] = pd.to_datetime(df_omni_o["Epoch"], utc=True)
    df_omni_o.set_index("Epoch", inplace=True)
    for key in df_omni_o.keys():
        if key == "Epoch" or key == "ssepoch":
            continue
        df_omni_o.loc[(df_omni_o[key] < -1e20) | (df_omni_o[key] > 1e20), key] = np.nan
    df_omni = df_omni_o.rolling(window="28D", min_periods=100).median()
    df_omni["sc_r"] = 1
    t_omni = (
    pd.Series(df_omni.index) - pd.to_datetime("1970-01-01 00:00:00", utc=True)
    ).dt.total_seconds()
    try:
        t_sc_unix = (df.index - pd.to_datetime("1970-01-01 00:00:00", utc=True)).total_seconds()
        print("Computing time done")
    except Exception:
        pass
     # Compute the time at Omni corresponding to time at the spacecraft
    if(np.isnan(df.vp_m).all()) :
    #for somethingh in range(1):
       # If all the velocity values in the data is NaN, then we fall back to
       # using the velocity from OMNI data. We compute the minimum and maximum
       # time values for the spacecraft observation, and using that, we find
       # out the average solar wind speed during that time at 1 AU. We use that
       # solar wind speed to find the approximate time. A better method would
       # be to find the approximate time at 1 AU instead of just using the
       # time of spacecraft. Will have to implement that part in a later
       # version
       t_max = df.index.max()
       t_min = df.index.min()
       dfv = df_omni.vp_m[ (df_omni.index > t_min) & (df_omni.index < t_max) ]
       vg = dfv.groupby(pd.Grouper(freq='4W')).apply(lambda x: np.nanmedian(x))
    
       new_v = np.zeros_like(df.Tp)
       new_v[:] = np.nan
       ind1 = 0
    
       for i in range(len(vg)) :
           ind2 = max(np.where(df.index < vg.index[i])[0])
           new_v[ind1:ind2] = vg[i]
           ind1 = ind2
       t_omni_sc = np.array(t_sc_unix) - np.array((df.sc_r - 1)*au/new_v)
    else :
        t_omni_sc = np.array(t_sc_unix) - np.array((df.sc_r - 1) * au / df.vp_m)

    df_intrp = pd.DataFrame(index=df.index)
    df_intrp["sc_r"] = df.sc_r

    for key in key_list:
        intrp_func = spl(t_omni, df_omni[key], fill_value="extrapolate")
        data_new = intrp_func(t_omni_sc)
        df_intrp[key] = df[key] / data_new
        print("Scaling done for %s" % (key))

    return df_intrp