import numpy as np
import pandas as pd
from datetime import datetime
import glob

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Miscellaneous.useful_functions import bin_data

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
    df_omni = pd.read_hdf("Data_Processed/Individual/omni/omni_unbinned_19630101_20250601.hf")
    # For any key in df_omni_o, if the value is smaller/larger than -/+1e-20, then set it to NaN
    for key in df_omni.keys():
        if key == "Epoch" or key == "ssepoch":
            continue
        df_omni.loc[(df_omni[key] < -1e20) | (df_omni[key] > 1e20), key] = np.nan

    for n in range(len(start_times)):
        if (sc =="mariner10" or sc == "cassini"):
            t_max = df["Epoch"].max()
            t_min = df["Epoch"].min()
            dfv = df_omni.loc[(df_omni["Epoch"] > t_min) & (df_omni["Epoch"] < t_max), "vp_m"]
            average = dfv.mean()
            print(sc, t_min, t_max, average)
            offset = (df["sc_r"] - 1) / average  # time delay in seconds
            offset = offset.replace([np.inf, -np.inf], np.nan).fillna(0)
            offset = pd.to_timedelta(offset, unit='s')
            adjusted_time = df["Epoch"] + offset  # shift timestamps forward
            mask = (adjusted_time >= start_times[n]) & (adjusted_time <= end_times[n])
            slices.append(df.loc[mask])
        else:
            offset = (df["sc_r"] - 1) / df["vp_m"]  # time delay in seconds
            offset = offset.replace([np.inf, -np.inf], np.nan).fillna(0)
            offset = pd.to_timedelta(offset, unit='s')
            adjusted_time = df["Epoch"] + offset  # shift timestamps forward
            mask = (adjusted_time >= start_times[n]) & (adjusted_time <= end_times[n])
            slices.append(df.loc[mask])
    df_out = pd.concat(slices, axis=0, )
    df_out.to_hdf(save_file,key = 'data', mode='w')

# time_separate("Data_Processed/Individual/voyager1/voyager1_unbinned_19770101_20241201.hf",
#               [datetime(1990, 2,3), datetime(2000,2,3)],
#               [datetime(1993, 2,3), datetime(2003,2,3)],
#               "Data_Processed/Individual/voyager1/test.hf")
solar_max_starts =[]
solar_max_stops =[]
solar_min_starts = []
solar_min_stops= []
ascending_starts = []
ascending_stops = []
descending_starts = []
descending_stops =[]
scs = [
    "psp",
    "solo",
    "mariner10",
    "helios1",
    "helios2",
    "ulysses",
    "cassini",
    "pioneer10",
    "pioneer11",
    "newhorizons",
    "voyager1",
    "voyager2"
]
years = [1956, 1961, 1967, 1972.5, 1978.5, 1983.5, 1988, 1993, 1998.5, 2004, 2011, 2017, 2022.5, 2024.75]
dates = [pd.to_datetime(f"{int(y)}") + pd.to_timedelta((y % 1) * 365.25, unit='D') for y in years]
#VERSION1
# #Solar Max
# for sc in scs:
#     print(sc)
#     time_separate(glob.glob(f"Data_Processed/Individual/{sc}/{sc}_unbinned_*.hf")[0], 
#                   dates[::2], dates[1::2], f"Data_Processed/Individual/{sc}/{sc}_solar_max_unbinned_v1.hf", sc)
#     bin_data(pd.read_hdf(f"Data_Processed/Individual/{sc}/{sc}_solar_max_unbinned_v1.hf"),
#                   f"Data_Processed/Individual/{sc}/{sc}_solar_max_binned_v1", n_bin = 85)
    
# #Solar Min
# for sc in scs:
#     print(sc)
#     time_separate(glob.glob(f"Data_Processed/Individual/{sc}/{sc}_unbinned_*.hf")[0], 
#                   dates[1:-1:2], dates[2::2], f"Data_Processed/Individual/{sc}/{sc}_solar_min_unbinned_v1.hf", sc)
#     bin_data(pd.read_hdf(f"Data_Processed/Individual/{sc}/{sc}_solar_min_unbinned_v1.hf"),
#                   f"Data_Processed/Individual/{sc}/{sc}_solar_min_binned_v1", n_bin = 85)

#Solar Max
smax_starts = [1956.5,1967.5,1978.5, 1989, 1999, 2011.5, 2022.75]
smax_ends = [1960.5, 1971, 1982.75, 1992.5, 2003, 2015, 2025]
smax_starts_dt  = [pd.to_datetime(f"{int(y)}") + pd.to_timedelta((y % 1) * 365.25, unit='D') for y in smax_starts]
smax_ends_dt = [pd.to_datetime(f"{int(y)}") + pd.to_timedelta((y % 1) * 365.25, unit='D') for y in smax_ends]
for sc in scs:
    print(sc)
    time_separate(glob.glob(f"Data_Processed/Individual/{sc}/{sc}_unbinned_*.hf")[0], 
                  smax_starts_dt, smax_ends_dt, f"Data_Processed/Individual/{sc}/{sc}_solar_max_unbinned_v2.hf", sc)
    bin_data(pd.read_hdf(f"Data_Processed/Individual/{sc}/{sc}_solar_max_unbinned_v2.hf"),
                  f"Data_Processed/Individual/{sc}/{sc}_solar_max_binned_v2", n_bin = 85)
    
#Solar Min
smin_starts = [1961.5,1973.35, 1984, 1994, 2005, 2017]
smin_ends = [1966.5, 1977.75, 1988, 1998, 2010.75, 2021.5]
smin_starts_dt = [pd.to_datetime(f"{int(y)}") + pd.to_timedelta((y % 1) * 365.25, unit='D') for y in smin_starts]
smin_ends_dt = [pd.to_datetime(f"{int(y)}") + pd.to_timedelta((y % 1) * 365.25, unit='D') for y in smin_ends]
for sc in scs:
    print(sc)
    time_separate(glob.glob(f"Data_Processed/Individual/{sc}/{sc}_unbinned_*.hf")[0], 
                  smin_starts_dt, smin_ends_dt, f"Data_Processed/Individual/{sc}/{sc}_solar_min_unbinned_v2.hf", sc)
    bin_data(pd.read_hdf(f"Data_Processed/Individual/{sc}/{sc}_solar_min_unbinned_v2.hf"),
                  f"Data_Processed/Individual/{sc}/{sc}_solar_min_binned_v2", n_bin = 85)