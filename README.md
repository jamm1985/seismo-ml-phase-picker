# seismo-ml-phase-picker
**seismo-ml-phase-picker** is a series of scripts for analysing seisan database and forming 
a set of waveform picks of events and noise picks 

### seismo-phase-picker
**seismo-phase-picker** is a script for forming a archive of picks waveforms from
a seisan database. It reads S-files info and slices picks from according waveform files.

Usage:

*python seismo-phase-picker [options]*

Options: 
```
-h, --help     : print this help message and exit
-s, --save arg : directory to save picks traces
-r, --rea  arg : s-files database main directory
-w. --wav  arg : waveforms database main directory
```

### stations-picker
**stations-picker** is a script which forms a list of stations which registered atleast one pick in selected database.
This list later might be used by **noise-picker** to reduce an execution time.
Use ***noise-picker -l \<path\>*** to specify path to stations list. Providing no ***-l*** argument will force script
to form stations list during execution.


Usage:

*python noise-picker [options]*

Options:
```
-h, --help     : print this help message and exit
-s, --save arg : full path for generated stations list file
-r, --rea  arg : s-files database main directory
```

### noise-picker
**noise-picker** is a script which forms a set of noise picks which passed STA/LTA but are not
actual recorded events

Usage:

*python noise-picker [options]*

Options:
```
-h, --help          : print this help message and exit
-s, --save      arg : directory to save noise picks
-r, --rea       arg : s-files database main directory
-l, --load      arg : path to stations from which to pick noise (leave empty if want to generate stations list during this script execution)
-d, --def       arg : full path to SEISAN.DEF (including filename)
-s, --start     arg : start date in format DD.MM.YYYY
-e, --end       arg : end date in format DD.MM.YYYY
-m, --max_picks arg : maximum number of noise picks
-a, --archives  arg : path to continious archives files directory
--output_level  arg : logging level from 1 to 5
--offset        arg : maximum picks offset 
--duration      arg : pick duration
```

### hdf5-creator
**hdf5-creator** is a script designed to compose hdf5 set compatible with [generalized seismic phase 
detection](https://github.com/interseismic/generalized-phase-detection) model. 

In order to use this script you might set following vars.py parameters:
```
hdf5_file_name - path to resulting hdf5 set
p_picks_path - path to p-phase picks
s_picks_path - path to s-phase picks
noise_picks_hdf5_path - path to noise picks 
```
Usage:

*python hdf5-creator*