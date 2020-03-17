path = '/seismo/seisan/'
db_name = 'IMGG_'
save_dir = '/home/chernykh/WAV'
wav_path = 'WAV/'
rea_path = 'REA/'

readings_path = path + rea_path
waveforms_path = path + wav_path
full_readings_path = readings_path + db_name
full_waveforms_path = waveforms_path + db_name

output_level = 5  # 0 - minimal output, 5 - maximum output

help_message = """Usage: seismo-phase-picker [options]
Options: 
-h, --help \t\t : print this help message and exit
-s, --save \t arg : directory to save picks traces
-r, --rea \t arg : s-files database main directory
-w. --wav \t arg : waveforms database main directory"""

