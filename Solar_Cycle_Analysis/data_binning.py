import numpy as np
import pandas as pd
import h5py as hf
from glob import glob

r_min = -1.4
r_max = 2
n_bin = 85
r_bin = np.logspace(r_min, r_max, n_bin)
n_key_list = [
                    "Tp",
                    "bm",
                    "np",
                    "vp_m",
                    "sc_r"
                ]
# scs = [
#     "psp",
#     "solo",
#     "helios1",
#     "helios2",
#     "mariner10",
#     "ulysses",
#     "cassini",
#     "pioneer10",
#     "pioneer11",
#     "newhorizons",
#     "voyager1",
#     "voyager2"
# ]
scs = ["omni"]
def bin_data(
    df = None,
    filename = None,
    filetype="hdf",
    n_bin=100,
    key_list = None
):
    """Function that sorts the raw hour averaged data into radial bins 

    Args:
        will fill in later once code is finalized
        df (_type_, optional): _description_. Defaults to None.
        filename (_type_, optional): _description_. Defaults to None.
        filetype (str, optional): _description_. Defaults to "pickle".
        n_bin (int, optional): _description_. Defaults to 100.
        key_list (_type_, optional): _description_. Defaults to None.
    """
    dfn = pd.DataFrame()
    for key in key_list:
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

df_ind = [] 
for sc in scs:
    fname = glob(f"Data_Processed/Individual/{sc}/{sc}_unbinned*.hf")
    print(fname)
    save_file = f"Data_Processed/Individual/{sc}/{sc}_binned"
    df_temp = pd.read_hdf(fname[0])
    df_ind.append(bin_data(df_temp, save_file, n_bin = n_bin, key_list= n_key_list))
df_all = pd.concat(df_ind)
bin_data(df_all, "Data_Processed/msc/all_spacecraft_binned", n_bin=n_bin, key_list = n_key_list)
    