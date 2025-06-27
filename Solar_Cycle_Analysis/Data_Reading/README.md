Description of data reading directory:

This folder contains the python scripts used to convert the raw data from 
NASA into individual unbinned .hf files. Description of files is below.

- The file "reading_msc.py" works for any spacecraft that possesed a 
  COHO 1hr merged dataset. This includes psp, solo, pioneer 10 and 11,
  helios 1 and 2, Ulysses, and Voyager 1 and 2.
- For the Ulysses data truncation, I just didn't use the files after the Jovian 
  encounter (using the date in Maruca et al. 2023). The other data is located in the
  HIGH_LAT_DATA folder.
- I did psp separately since it was easiest to start with only one spacecraft
- Mariner 2 and 10 are different since they came from OMNIWeb Plus
  - Mariner 2 was evil and I could not find any of the data, so currently I am using Ramiz's file
- New Horizons for some reason does not have a COHO Merged 1hr dataset
  (because why be like everyone else)
- Cassini only had a 1min averaged dataset, so its file is modified slightly