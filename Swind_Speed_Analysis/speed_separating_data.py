import pandas as pd
import numpy as np
from glob import glob
def speed_separate(df):
    """Function used to separate data based on speed type (fast, medium, slow).
    Separates it based on the 30th, 70th, and 100th percentiles.

    Args:
        df (pandas datafram): Dataframe to be separated
    """
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
    df_slow = pd.DataFrame(index = range(n_bin))
    df_med = pd.DataFrame(index = range(n_bin))
    df_fast = pd.DataFrame(index = range(n_bin))
    for key in n_key_list:
        for dfn in [df_slow, df_med, df_fast]:
            dfn[key + "_high"] = np.nan
            dfn[key + "_med"] = np.nan
            dfn[key + "_low"] = np.nan
            dfn[key + "_num"] = np.nan
    for ind in range(len(r_bin) - 1):
        bin_mask = (df["sc_r"] > r_bin[ind]) & (df["sc_r"] <= r_bin[ind + 1])
        df_bin = df[bin_mask].copy()
        df_bin.loc[df_bin["vp_m"] < -1e-12, "vp_m"] = np.nan
        df_bin = df_bin.dropna(subset=["vp_m"])
        # if df_bin.empty:
        #     continue
        v_30 = df_bin["vp_m"].quantile(.3)
        v_70 = df_bin["vp_m"].quantile(.7)
        
        slow_mask = df_bin["vp_m"] <= v_30
        med_mask = (df_bin["vp_m"] > v_30) & (df_bin["vp_m"] <= v_70)
        fast_mask = df_bin["vp_m"] > v_70
        
        group_masks = [slow_mask, med_mask, fast_mask]
        result_dfs  = [df_slow, df_med, df_fast]
        
        for mask, dfn in zip(group_masks, result_dfs):
            df_group = df_bin[mask]
            
            for key in n_key_list:
                data = df_group[key]
                data = data[data > -1e-12]  

                if data.empty:
                    continue

                dfn.loc[ind, key + "_high"] = data.quantile(0.9)
                dfn.loc[ind, key + "_med"]  = data.quantile(0.5)
                dfn.loc[ind, key + "_low"]  = data.quantile(0.1)
                dfn.loc[ind, key + "_num"]  = len(data)
    return df_slow, df_med, df_fast
scs = [
"psp",
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
speed_types = ["slow", "med", "fast"]
dfs = []
for sc in scs:
    fname = glob(f"Data_Processed/Individual/{sc}/{sc}_unbinned*.hf")
    df_sc = pd.read_hdf(fname[0])
    dfs.append(df_sc)
    df_slow, df_med, df_fast = speed_separate(df_sc)
    df_slow.to_hdf(f"Data_Processed/Individual/{sc}/{sc}_slow_binned.hf", key="df", mode="w")
    df_med.to_hdf(f"Data_Processed/Individual/{sc}/{sc}_med_binned.hf", key="df", mode="w")
    df_fast.to_hdf(f"Data_Processed/Individual/{sc}/{sc}_fast_binned.hf", key="df", mode="w")
df_all = pd.concat(dfs)
df_slow, df_med, df_fast = speed_separate(df_all)
df_slow.to_hdf(f"Data_Processed/msc/msc_slow_binned.hf", key="df", mode="w")
df_med.to_hdf(f"Data_Processed/msc/msc_med_binned.hf", key="df", mode="w")
df_fast.to_hdf(f"Data_Processed/msc/msc_fast_binned.hf", key="df", mode="w")
