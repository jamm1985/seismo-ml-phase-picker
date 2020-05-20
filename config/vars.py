# PATH VARIABLES
path = '/seismo/seisan/'  # Seisan root
db_name = 'IMGG_'  # Database name
save_dir = '/home/chernykh/WAV5'  # Where to save picks
wav_path = 'WAV/'  # WAV files subdir name
rea_path = 'REA/'  # S-files subdir name
seisan_definitions_path = '/seismo/seisan/DAT/SEISAN.DEF'  # Path to def file (used for finding stations definitions)
archives_path = '/seismo/archive'                    # Path to archives
stations_save_path = '/home/chernykh/WAV5/stations'  # Where to save stations list (station-picker)
stations_load_path = ''  # Leave empty if want to generate stations list in process

# CALCULATED PATH VARIABLES
readings_path = path + rea_path  # Partial path to S-files
waveforms_path = path + wav_path  # Partial path to WAV files
full_readings_path = readings_path + db_name  # Full path to S-files
full_waveforms_path = waveforms_path + db_name  # Full path to WAV files

# OUTPUT PARAMETERS
output_level = 5  # 0 - minimal output, 5 - maximum output

# SLICING PARAMETERS
slice_duration = 4  # Slice duration in seconds
slice_offset = 5    # Max value of random slice offset in seconds (negatively shifts start of waveform
#                      ..slicing from 1 to slice_offset seconds)

archive_channels_order = ['N', 'E', 'Z']  # Specifies channels to pick

# NOISE PICKING
max_noise_picks = 100  # Max amount of noise examples to pick per script run

start_date = [2014, 1, 1]  # Starting date for noise picker
end_date = [2015, 1, 1]    # End date for noise picker

tolerate_events_in_same_day = False  # If False - noise picker will ignore days when actual recorded events happend
event_tolerance = 15  # Number of seconds around noise trace which should not contain any events

# TO-DO: move month length to utils/ as function
month_length = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# HDF5 PARAMETERS
required_df = 100  # Required frequency of hdf5 traces for GPD
required_sample_length = 400  # Required amount of samples (basically length*frequency)

# MESSAGES
picks_help_message = """Usage: python seismo-phase-picker.py [options]
Options: 
-h, --help \t\t : print this help message and exit
-s, --save \t arg : directory to save picks traces
-r, --rea \t arg : s-files database main directory
-w. --wav \t arg : waveforms database main directory
This script slices a list of events picks waveforms, according to picks in s-files. 
It tries to get picks from continious archives if avaliable, rather than from WAV database."""

noise_help_message = """Usage: python noise-picker.py [options]
Options: 
-h, --help \t\t : print this help message and exit
-s, --save \t arg : directory to save noise picks
-r, --rea \t arg : s-files database main directory
-l, --load \t arg : path to stations from which to pick noise (leave empty if want to generate stations list during this script execution)
-d, --def \t arg : full path to SEISAN.DEF (including filename)
-s, --start \t arg : start date in format DD.MM.YYYY
-e, --end \t arg : end date in format DD.MM.YYYY
-m, --max_picks \t arg : maximum number of noise picks
-a, --archives \t arg : path to continious archives files directory
--output_level \t arg : logging level from 1 to 5
--offset \t arg : maximum picks offset 
--duration \t arg : pick duration
This script slices a list of noise picks wich passed STA/LTA trigger but not described in any of s-files."""

stations_help_message = """Usage: python stations-picker.py [options]
Options: 
-h, --help \t\t : print this help message and exit
-s, --save \t arg : full path for generated stations list file
-r, --rea \t arg : s-files database main directory
This script generates list of all stations, which registered atleast one event in current database."""

