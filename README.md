# Trans-Heliospheric_Survey
Author: Carson Brown

Compilation of code I wrote for research on the Trans-Heliospheric Survey

Description of directories:

- Data_Processed/ contains all of the data after scaling/binning/separating. Data_Processed/Individual/ contains all individual
  data, OMNI data, and ESA/SPC data from PSP. Data_Processed/msc/ (multi spacecraft) contains combined datasets, scaled and unscaled, for 
  all spacecraft, solar cycle separated, and speed separated.
- Data_Raw/ contains the raw datasets from CDAWeb and OMNIWeb for everything in Data/Processed
- Figures/ contains all of the figures (shocking). Hopefully the directories within Figures/ are self explanatory
- Miscellaneous/ contains files that did not fit within a specific project
- Parker_Model_Fitting contains anything used to fit with the Parker Model. This folder is missing a lot of old code I wrote
  in 2024, but has the code used to generate the figures in the 2025 paper (plt_msc_special.py).
- PSP_Intercallibration/ contains the work on merging ESA data with PSP's COHO-1HR Merged dataset. To re-make the data in Data_Processed, 
  run scaling_psp.py after the files in Solar_Cycle_Analysis/.
- Solar_Cycle_Analysis/ contains all of the files used to create plots for and generate the solar cycle separated data. It also contains the files 
  used to read, bin, and scale the data (this should maybe be changed for clarity). 
- Swind_Speed_Analysis/ contains the code for creating and plotting the speed separated data.