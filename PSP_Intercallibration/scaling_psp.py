import numpy as np
import pandas as pd
import h5py as hf
from glob import glob
import pytz
from scipy.interpolate import interp1d as spl

df = pd.read_hdf("Data_Processed/Individual/psp/psp_unbinned_20180101_20241201.hf")

df_esa = pd.read_hdf("Data_Processed/Individual/psp_esa_data/psp_esa_data_unbinned_20181002_20241031.hf")

df.set_index("Epoch", inplace=True)
df_esa.set_index("Epoch", inplace=True)
if df.index.tz is None:
    df.index = df.index.tz_localize(pytz.utc)
else:
    df.index = df.index.tz_convert(pytz.utc)

if df_esa.index.tz is None:
    df_esa.index = df_esa.index.tz_localize(pytz.utc)
else:
    df_esa.index = df_esa.index.tz_convert(pytz.utc)
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
vp_combined = df["vp_m"].copy()

missing_mask = vp_combined.isna()
if missing_mask.any():
    print("yes")
    df_esa = df_esa.groupby(df_esa.index).mean()
    vp_esa_interp = df_esa["vp_m"].reindex(df.index, method='nearest')
    vp_combined[missing_mask] = vp_esa_interp[missing_mask]

# Now compute t_omni_sc using the combined velocity
t_omni_sc = np.array(t_sc_unix) - np.array((df.sc_r - 1) * au / vp_combined)
df_intrp = pd.DataFrame(index=df.index)
df_intrp["sc_r"] = df.sc_r

key_list = [
                    "Tp",
                    "bm",
                    "np",
                    "vp_m",
                    "sc_r"
                ]
for key in key_list:
    intrp_func = spl(t_omni, df_omni[key], fill_value="extrapolate")
    data_new = intrp_func(t_omni_sc)
    df_intrp[key] = df[key] / data_new
    print("Scaling done for %s" % (key))
r_min = -1.4
r_max = 2
n_bin = 85
r_bin = np.logspace(r_min, r_max, n_bin)
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
scs = [
    "solo",
    "helios1",
    "helios2",
    "mariner10",
    "ulysses",
    "cassini",
    "pioneer10",
    "pioneer11",
    "newhorizons",
    "voyager1",
    "voyager2"
]
df_ind = []
df_ind.append(df_intrp)
df_intrp.to_hdf(f"Data_Processed/Individual/psp/psp_scaled_unbinned", key="df", mode="w")
for sc in scs:
    fname = glob(f"Data_Processed/Individual/{sc}/{sc}_scaled_unbinned*")
    print(fname)
    df_sc = pd.read_hdf(fname[0])

    df_ind.append(df_sc)

df_all = pd.concat(df_ind)
bin_data(df_all, "Data_Processed/msc/all_spacecraft_binned_scaled", n_bin=n_bin, key_list = key_list)
