import obspy.core.utcdatetime as datetime


# Picking stats definition
class PickStats:
    last_file_parsed = None  # LastFileParsed
    file_currently_parsed = None  # FileCurrentlyParsed - None, if picking process successfully finished
    error_event_id = None  # ErrorEventID - Has value if aborted process during event parsing

    total_files_parsed = 0  # TotalFilesParsed
    total_events_parsed = 0  # TotalEventsParsed
    total_phases_parsed = 0  # TotalPhasesParsed

    last_run_files_parsed = 0  # LastRunFilesParsed
    last_run_events_parsed = 0  # LastRunEventsParsed
    last_run_phases_parsed = 0  # LastRunPhasesParsed

    finished = False  # Finished

    def __str__(self):
        """
        Custom __str__ method implementation. Resulting string is represented in .ini format
        :return: string representation of the object
        """
        lines = ['[Picking Statistics]',
                 '{}={}'.format('LastFileParsed', self.last_file_parsed),
                 '{}={}'.format('FileCurrentlyParsed', self.file_currently_parsed),
                 '{}={}'.format('ErrorEventID', self.error_event_id),

                 '{}={}'.format('TotalFilesParsed', self.total_files_parsed),
                 '{}={}'.format('TotalEventsParsed', self.total_events_parsed),
                 '{}={}'.format('TotalPhasesParsed', self.total_phases_parsed),

                 '{}={}'.format('LastRunFilesParsed', self.last_run_files_parsed),
                 '{}={}'.format('LastRunEventsParsed', self.last_run_events_parsed),
                 '{}={}'.format('LastRunPhasesParsed', self.last_run_phases_parsed),

                 '{}={}'.format('Finished', self.finished)]

        return '\n'.join(lines)

    def write(self, path):
        """
        Writes stats to a file
        :param path: path to a file
        """
        with open(path, 'w') as f:
            print(str(self), file=f)

    def read(self, path):
        """
        Reads stats from a file
        :param path: path to a file
        """
        with open(path, 'r') as f:
            for line in f:
                # Check if line is a parameter definition
                split = line.split('=', 2)
                if type(split) is list and len(split) == 2:
                    # Read parameter name
                    param_name = split[0]

                    # Remove comments and read value
                    param_list = split[1].split(';', 2)
                    if type(split) is list:
                        param_val = param_list[0]
                    else:
                        param_val = split[1]

                    # Trim strings
                    param_name = param_name.strip()
                    param_val = param_val.strip()

                    self.set_value(param_name, param_val)

    def set_value(self, name, value):
        """
        Sets parameter from it's name
        :param name: Name of parameter
        :param value: Value of parameter
        :return:
        """
        if type(name) is not str:
            raise TypeError("name must be a string")

        if name == 'LastFileParsed':
            if value is None or value == 'None':
                self.last_file_parsed = None
            else:
                self.last_file_parsed = str(value)
        elif name == 'FileCurrentlyParsed':
            if value is None or value == 'None':
                self.file_currently_parsed = None
            else:
                self.file_currently_parsed = str(value)
        elif name == 'ErrorEventID':
            if value is None or value == 'None':
                self.error_event_id = None
            else:
                self.error_event_id = str(value)

        elif name == 'TotalFilesParsed':
            self.total_files_parsed = int(value)
        elif name == 'TotalEventsParsed':
            self.total_events_parsed = int(value)
        elif name == 'TotalPhasesParsed':
            self.total_phases_parsed = int(value)

        elif name == 'LastRunFilesParsed':
            self.last_run_files_parsed = int(value)
        elif name == 'LastRunEventsParsed':
            self.last_run_events_parsed = int(value)
        elif name == 'LastRunPhasesParsed':
            self.last_run_phases_parsed = int(value)

        elif name == 'Finished':
            if value == "True":
                self.finished = True
            else:
                self.finished = False

        else:
            raise ValueError("name must correspond with actual parameter name")


# Event stats definition
class EventStats:
    event_id = None  # EventID
    s_file_path = None  # SFilePath
    magnitude = None  # Magnitude
    depth = None  # Depth

    def __str__(self):
        """
        Custom __str__ method implementation. Resulting string is represented in .ini format
        :return: string representation of the object
        """
        lines = ['[Event Description]',
                 '{}={}'.format('EventID', self.event_id),
                 '{}=\"{}\"'.format('SFilePath', self.s_file_path),
                 '{}={}'.format('Magnitude', self.magnitude),
                 '{}={}'.format('Depth', self.depth)]

        return '\n'.join(lines)

    def write(self, path):
        """
        Writes stats to a file
        :param path: path to a file
        """
        with open(path, 'w') as f:
            print(str(self), file=f)

    def read(self, path):
        """
        Reads stats from a file
        :param path: path to a file
        """
        with open(path, 'r') as f:
            for line in f:
                # Check if line is a parameter definition
                split = line.split('=', 2)
                if type(split) is list and len(split) == 2:
                    # Read parameter name
                    param_name = split[0]

                    # Remove comments and read value
                    param_list = split[1].split(';', 2)
                    if type(split) is list:
                        param_val = param_list[0]
                    else:
                        param_val = split[1]

                    # Trim strings
                    param_name = param_name.strip()
                    param_val = param_val.strip()
                    param_val = param_val.strip('\"')

                    self.set_value(param_name, param_val)

    def set_value(self, name, value):
        """
        Sets parameter from it's name
        :param name: Name of parameter
        :param value: Value of parameter
        :return:
        """
        if type(name) is not str:
            raise TypeError("name must be a string")

        if name == 'EventID':
            if value is None or value == 'None':
                self.event_id = None
            else:
                self.event_id = str(value)
        elif name == 'SFilePath':
            if value is None or value == 'None':
                self.s_file_path = None
            else:
                self.s_file_path = str(value)
        elif name == 'Magnitude':
            if value is None or value == 'None':
                self.magnitude = None
            else:
                self.magnitude = float(value)
        elif name == 'Depth':
            if value is None or value == 'None':
                self.depth = None
            else:
                self.depth = float(value)
        else:
            raise ValueError("name must correspond with actual parameter name")


# Picks stats definition
class SliceStats:
    event_id = None  # EventID
    s_file_path = None  # SFilePath

    station = None  # Station
    phase_hint = None  # PhaseHint

    magnitude = None  # Magnitude
    depth = None  # Depth
    distance = None  # Distance

    file_format = None  # FileFormat

    phase_time = None  # WavePhaseTime
    start_time = None  # WaveStartTime
    end_time = None  # WaveEndTime

    def __str__(self):
        """
        Custom __str__ method implementation. Resulting string is represented in .ini format
        :return: string representation of the object
        """
        lines = ['[Picks Description]',
                 '{}={}'.format('EventID', self.event_id),
                 '{}=\"{}\"'.format('SFilePath', self.s_file_path),

                 '{}={}'.format('Station', self.station),
                 '{}={}'.format('PhaseHint', self.phase_hint),

                 '{}={}'.format('Magnitude', self.magnitude),
                 '{}={}'.format('Depth', self.depth),
                 '{}={}'.format('Distance', self.distance),

                 '{}={}'.format('FileFormat', self.file_format),

                 '{}={}'.format('WavePhaseTime', self.phase_time),
                 '{}={}'.format('WaveStartTime', self.start_time),
                 '{}={}'.format('WaveEndTime', self.end_time)]

        return '\n'.join(lines)

    def write(self, path):
        """
        Writes stats to a file
        :param path: path to a file
        """
        with open(path, 'w') as f:
            print(str(self), file=f)

    def read(self, path):
        """
        Reads stats from a file
        :param path: path to a file
        """
        with open(path, 'r') as f:
            for line in f:
                # Check if line is a parameter definition
                split = line.split('=', 2)
                if type(split) is list and len(split) == 2:
                    # Read parameter name
                    param_name = split[0]

                    # Remove comments and read value
                    param_list = split[1].split(';', 2)
                    if type(split) is list:
                        param_val = param_list[0]
                    else:
                        param_val = split[1]

                    # Trim strings
                    param_name = param_name.strip()
                    param_val = param_val.strip()
                    param_val = param_val.strip('\"')

                    self.set_value(param_name, param_val)

    def set_value(self, name, value):
        """
        Sets parameter from it's name
        :param name: Name of parameter
        :param value: Value of parameter
        :return:
        """
        if type(name) is not str:
            raise TypeError("name must be a string")

        if name == 'EventID':
            if value is None or value == 'None':
                self.event_id = None
            else:
                self.event_id = str(value)
        elif name == 'SFilePath':
            if value is None or value == 'None':
                self.s_file_path = None
            else:
                self.s_file_path = str(value)

        elif name == 'Station':
            if value is None or value == 'None':
                self.station = None
            else:
                self.station = str(value)
        elif name == 'PhaseHint':
            if value is None or value == 'None':
                self.phase_hint = None
            else:
                self.phase_hint = str(value)

        elif name == 'Magnitude':
            if value is None or value == 'None':
                self.magnitude = None
            else:
                self.magnitude = float(value)
        elif name == 'Depth':
            if value is None or value == 'None':
                self.depth = None
            else:
                self.depth = float(value)
        elif name == 'Distance':
            if value is None or value == 'None':
                self.distance = None
            else:
                self.distance = float(value)

        elif name == 'FileFormat':
            if value is None or value == 'None':
                self.file_format = None
            else:
                self.file_format = str(value)

        elif name == 'WavePhaseTime':
            if value is None or value == 'None':
                self.phase_time = None
            else:
                split = value.split('-', 2)
                dmy_split = split[0].split('.', 3)
                hms_split = split[1].split(':', 3)

                self.phase_time = datetime.UTCDateTime(day=int(dmy_split[0]),
                                                       month=int(dmy_split[1]),
                                                       year=int(dmy_split[2]),
                                                       hour=int(hms_split[0]),
                                                       minute=int(hms_split[1]),
                                                       second=int(hms_split[2]))
        elif name == 'WaveStartTime':
            if value is None or value == 'None':
                self.start_time = None
            else:
                split = value.split('-', 2)
                dmy_split = split[0].split('.', 3)
                hms_split = split[1].split(':', 3)

                self.start_time = datetime.UTCDateTime(day=int(dmy_split[0]),
                                                       month=int(dmy_split[1]),
                                                       year=int(dmy_split[2]),
                                                       hour=int(hms_split[0]),
                                                       minute=int(hms_split[1]),
                                                       second=int(hms_split[2]))
        elif name == 'WaveEndTime':
            if value is None or value == 'None':
                self.end_time = None
            else:
                split = value.split('-', 2)
                dmy_split = split[0].split('.', 3)
                hms_split = split[1].split(':', 3)

                self.end_time = datetime.UTCDateTime(day=int(dmy_split[0]),
                                                     month=int(dmy_split[1]),
                                                     year=int(dmy_split[2]),
                                                     hour=int(hms_split[0]),
                                                     minute=int(hms_split[1]),
                                                     second=int(hms_split[2]))

        else:
            raise ValueError("name must correspond with actual parameter name")
