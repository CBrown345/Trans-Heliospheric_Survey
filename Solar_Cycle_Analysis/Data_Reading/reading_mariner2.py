import h5py
import pandas as pd

input_path = 'Data_Raw/COHO1HR_Merged_Individual/mariner2/mariner2_binned.hf'
output_path = 'Data_Processed/Individual/mariner2/mariner2_binned.hf'


with h5py.File(input_path, 'r') as f:
    data = {}
    for key in f.keys():
        data[key] = f[key][:]
        
df = pd.DataFrame(data)

df.to_hdf(output_path, key='df', mode='w')
print(f'Data saved in pandas HDF format at: {output_path}')