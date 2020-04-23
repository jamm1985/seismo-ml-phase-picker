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
-h, --help \t\t : print this help message and exit
-s, --save \t arg : directory to save picks traces
-r, --rea \t arg : s-files database main directory
-w. --wav \t arg : waveforms database main directory
```

### noise-picker
**noise-picker** is a script which forms a set of noise picks which passed STA/LTA but are not
actual recorded events

Usage:

*python noise-picker [options]*

Options:
```
-h, --help \t\t : print this help message and exit
-s, --save \t arg : directory to save noise picks
```