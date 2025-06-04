Description of data reading directory:

This folder contains the python scripts used to convert the raw data from 
NASA into individual unbinned .hf files. Description of files is below.

- The file "reading_msc.py" works for any spacecraft that possesed a 
  COHO 1hr merged dataset. This includes psp, solo, pioneer 10 and 11, 
  and helios 1 and 2.
- I did psp separately since it was easiest to start with only one spacecraft
- Though Ulysses and Voyager 1 and 2 possesed a COHO 1hr merged dataset, 
  because of their data truncation they were handled separately
- Mariner 2 and 10 are different since they came from OMNIWeb Plus
- New Horizons for some reason does not have a COHO Merged 1hr dataset
  (because why be like everyone else)
- Cassini only had a 1min averaged dataset