import numpy as np
import struct
from pytimbre.audio import Waveform
from pytimbre.audio_files.wavefile import WaveFile
import os.path
from datetime import datetime, timedelta
from dateutil import parser
import warnings


class StandardBinaryFile(Waveform):
    """
    This class holds the data for the standard ANSI Standard S12.75 formatted binary files.  The class will permit
    access to the data, the header, and specific elements of the header that are required for various analyses that
    may be required.

    @author: frank mobley

    """

    def __init__(self, filename: str = None, wfm: Waveform = None, header_element_count: int = None,
                 sample_rate_key: str = 'SAMPLE RATE (HZ)', start_time_key: str = 'TIME (UTC ZULU)',
                 sample_format_key: str = 'SAMPLE FORMAT', data_format_key: str = 'DATA FORMAT',
                 sample_count_key: str = 'SAMPLES TOTAL', header_only: bool = False, s0=None, s1=None):
        """
        This function is the default constructor that loads the data from the filename that is provided in the argument
        list.  This will load the header and the acoustic data into a series of arrays and DataFrames.

        Parameters
        ----------
        filename : STRING, default = None
            This is the full path to the location of the file that we want to load into the class
        wfm: Waveform, default = None
            This is a Waveform object that we want to store in the standard binary file format
        header_element_count: int, default = None
            The number of elements within the header to read. This is typically the first line of the file,
            but it may or may not include the first line in the count. This provides a method to override the
            internal determination of the line count. The default is none, in which case the constructor assumes that
            information in the file is correct.
        sample_rate_key: str, default = "SAMPLE RATE (HZ)"
            This is the key to use in searching the header dictionary to define the number of samples per second the
            digital data was sampled during the measurement.
        start_time_key: str, default = "TIME (UTC ZULU)"
            This is the key to use in searching the header dictionary to define the start time of the
            measurement.
        sample_format_key: str, default = "SAMPLE FORMAT"
            This is the key to use in searching the header dictionary to define sample format for the binary data
        data_format_key: str, default = "DATA FORMAT"
            This is the key to use in searching the header dictionary to define the format of the sample stored in
            the binary data.
        sample_count_key: str, default = "SAMPLES TOTAL"
            The number of samples within the binary section of the file.
        header_only: bool, default = False
            A flag to determine whether this constructor will only read the header information
        s0: int, default = 0 - the starting sample of the output waveform
        s1: int, default = None - the ending sample of the output waveform

        Returns
        -------
        None.

        Remarks
        _______
        20230201 - FSM - Updated the methods to read the header information so that a variety of formatted
        information can be used in definition of the StandardBinaryFile object.
        """
        warnings.warn(f"{self.__class__.__name__} is obsolete and will be removed in version 1.0.2")

        self._header = None

        if filename is not None:
            self._read_file(filename, header_element_count, sample_rate_key, start_time_key, sample_format_key,
                            data_format_key, sample_count_key, header_only, s0, s1)
            if header_only == False:
                super().__init__(self.samples, self.sample_rate, self.start_time, remove_dc_offset=False)

        elif wfm is not None:
            super().__init__(wfm.samples, wfm.sample_rate, wfm.start_time, remove_dc_offset=False)
            self._header = None
        else:
            self._samples = None
            self.fs = None
            self.time0 = None
            self._header = None

    def _read_sample_rate(self, key):
        if key not in self.header.keys():
            raise ValueError("The name of the sample rate element of the waveform is not located within the "
                             "header dictionary. Please provide the correct name of the sample rate property")
        else:
            self.fs = float(self.header[key])

    def _read_start_time(self, key):
        if key not in self.header.keys() and "TIME (TPM)" not in self.header.keys():
            raise ValueError(
                "The name of the start time element of the waveform is not located within the "
                "header dictionary. Please provide the correct name of the start time property")
        elif "TIME (TPM)" in self.header.keys():
            self.time0 = float(self.header['TIME (TPM)'])
        else:
            self.time0 = parser.parse(self.header[key])

    def _read_sample_count(self, key):
        if key not in self.header.keys():
            raise ValueError("The number of samples must be provided, and the expected header element is not "
                             "found within the list of objects in the header.")
        else:
            self.sample_count = int(self.header[key])

    def _read_format(self, sample_format_key, data_format_key):
        if sample_format_key not in self.header.keys():
            raise ValueError(
                "The name of the sample format element of the waveform is not located within the "
                "header dictionary. Please provide the correct name of the sample format property")
        else:
            if self.header[sample_format_key].upper() != "LITTLE ENDIAN":
                raise ValueError("The expected format is not present in the header.")

        if data_format_key not in self.header.keys():
            raise ValueError(
                "The name of the data format element of the waveform is not located within the "
                "header dictionary. Please provide the correct name of the data format property")
        else:
            if self.header[data_format_key].upper() != "REAL*4":
                raise ValueError("The required sample formate is not present in the header.")

    def _define_samples_to_read(self, s0, s1):
        samples_to_read = self.sample_count

        if s0 is not None and s1 is None:
            samples_to_read -= s0
            if isinstance(self.start_time, datetime):
                self.start_time += timedelta(seconds=s0 / self.sample_rate)
            elif isinstance(self.start_time, float):
                self.start_time += s0 / self.sample_rate
        elif s0 is None and s1 is not None:
            samples_to_read = s1
        elif s0 is not None and s1 is not None:
            samples_to_read = s1 - s0
            if isinstance(self.start_time, datetime):
                self.start_time += timedelta(seconds=s0 / self.sample_rate)
            elif isinstance(self.start_time, float):
                self.start_time += s0 / self.sample_rate

        return samples_to_read

    def _read_file(self, filename, header_element_count: int = None,
                   sample_rate_key: str = 'SAMPLE RATE (HZ)', start_time_key: str = 'TIME (UTC ZULU)',
                   sample_format_key: str = 'SAMPLE FORMAT', data_format_key: str = 'DATA FORMAT',
                   sample_count_key: str = 'SAMPLES TOTAL', header_only: bool = False, s0=None, s1=None):
    #   Get the header and the location of the binary data
        f_in, header = StandardBinaryFile.read_header(filename, header_element_count)
        self._header = header

        if header_only:
            self._samples = None
            return

        #   Now to effectively understand how to read the data from the binary portion, we must determine
        #   where specific data within the header exist. So look for the elements that were defined within
        #   the function prototype.
        #
        #   The sample rate
        self._read_sample_rate(sample_rate_key)

        #   The start time of the audio file
        self._read_start_time(start_time_key)

        #   The number of samples in the waveform
        self._read_sample_count(sample_count_key)

        #   At this point there should be no reason for the data to be stored as anything other than REAL*4
        #   Little Endian, but we do not account for any other formats, so we must now examine what is in the
        #   header and exit if it is not what we expect.
        self._read_format(sample_format_key, data_format_key)

        self._data_offset = f_in.tell()

        if s0 is not None and s0 > 0:
            # At this point we should interrogate the header to determine the size of the data sample,
            # but we are only supporting floating point values, so we can just increment the current location
            # by four times the desired start sample. So let's move the counter from the current position.
            f_in.seek(s0 * 4, 1)

        #   Now we need to determine how many sample to read
        samples_to_read = self._define_samples_to_read(s0, s1)

        #   Read the data - At this point we only support 32-bit/4-byte data samples
        data = f_in.read(4 * samples_to_read)

        #   Now unpack the data from the array of bytes into an array of floating point data
        samples = np.asarray(struct.unpack('f' * samples_to_read, data))
        super().__init__(samples, self.sample_rate, self.start_time, remove_dc_offset=False)

        if samples_to_read < self.sample_count:
            self.sample_count = samples_to_read
            self._samples -= np.mean(self.samples)

        #   close the file
        f_in.close()

    @staticmethod
    def convert_stdbin_header(header_line):
        """
        This function will take the information within the header line and remove
        the semicolon in the front and all ellipsoid markers to determine the name
        of the property.  It also splits based on the colon to determine the value

        @author: Frank Mobley

        Parameters
        ----------
        header_line : STRING
            The line of text from the header of the file

        Returns
        -------
        name : STRING
            The name of the property or attribute

        value : STRING
            The value of the property

        """

        #   Split the string based on the colon

        elements = header_line.split(':')

        if len(elements) > 2:
            value = ':'.join(elements[1:])
        else:
            value = elements[1].strip()
        name = elements[0][1:].split('.')[0]

        return name, value

    @staticmethod
    def read_stdbin_header_line(binary_file):
        """
        Python does not provide the ability to read a line of text from a
        binary file.  This function will read from the current position in the
        file to the new line character.  The set of bytes is then converted to
        a string and returned to the calling function.

        @author: frank Mobley

        Parameters
        ----------
        binary_file : FILE
            The file pointer that will be read from

        Returns
        -------
        The string representing a line of ASCII characters from the file.

        """

        #   Get the current position within the file so that we can return here
        #   after determining where the end of the file is.

        current_position = binary_file.tell()

        #   Find the end of the file

        binary_file.seek(-1, 2)

        eof = binary_file.tell()

        #   Return to the point we were within the file

        binary_file.seek(current_position, 0)

        #   Read until the last character is a new line or we have reached the
        #   end of the file.

        characters = ''
        char = ' '
        while ord(char) != 10 or binary_file.tell() == eof - 1:
            char = binary_file.read(1)
            if ord(char) != 10:
                characters += char.decode()

        return characters

    @staticmethod
    def write_std_binary_file(wfm, orig_header, output_filename):
        """
        Static method that given a generic_time_waveform object and a header dict writes a standard binary file
        according to ANSI S12.75
        Parameters
        ----------
        wfm : generic_time_waveform object
            Waveform of measured data.

        orig_header : dict
            Header info.

        output_filename : str
            Output file path with full name of file and extension.
        """
        # Check that correct data type were given as inputs
        if not (isinstance(wfm, Waveform)) or not (isinstance(orig_header, dict)) or \
                not (isinstance(output_filename, str)):
            raise ValueError("Incorrect inputs, check that wfm is a generic time waveform object, header is a dict and "
                             "output_filename is a str that's a full file path to the output directory")

        header = orig_header.copy()

        # Append sample format and encoding method if they don't exist to the header dict

        header['SAMPLE RATE (HZ)'] = int(np.floor(wfm.sample_rate))
        header['SAMPLES TOTAL'] = len(wfm.samples)
        if isinstance(wfm.start_time, datetime):
            header['TIME (UTC ZULU)'] = wfm.start_time.strftime('%Y/%m/%d %H:%M:%S.%f')
        else:
            header['TIME (TPM)'] = wfm.start_time

        header['SAMPLE FORMAT'] = "LITTLE ENDIAN"
        header['DATA FORMAT'] = 'REAL*4'

        # Check to see if output path exist and open file if it doesn't exist

        if not os.path.exists(output_filename):
            f = open(output_filename, 'wb')

            # Write header info from dict

            header_line = ';{}'.format("HEADER SIZE").ljust(41, '.') + ': {}\n'.format(len(header.keys()) + 1)
            f.write(header_line.encode('utf-8'))

            for key in header.keys():
                header_line = ';{}'.format(key.upper()).ljust(41, '.') + ': {}\n'.format(header[key])
                f.write(header_line.encode('utf-8'))

            # Write pressure data to end of file

            for i in range(len(wfm.samples)):
                f.write(struct.pack('<f', wfm.samples[i]))
            f.close()

    @staticmethod
    def audio_info(path: str = None):
        """
        This function will parse out the header of the StandardBinaryFile and return it to the user. This header
        information provide the details required to read in only parts of the data to ensure large files are do not
        have to be read entirely before extracting the information

        Parameters
        ----------
        path: string - default = None - This is the location of the file to be examined

        Returns
        -------
        A dictionary with the header information parsed out.
        """

        f_in, header = StandardBinaryFile.read_header(path)
        f_in.close()

        return header

    @staticmethod
    def read_header(filename: str, header_element_count: int = None):
        """
        This function will parse out the header of the file and return the binary file object for the continued reading
        of the data from the file.

        Parameters
        ----------
        filename: string - the location of the file that we want to read
        header_element_count: int, default = None
            The number of elements within the header to read. This is typically the first line of the file,
            but it may or may not include the first line in the count. This provides a method to override the
            internal determination of the line count. The default is none, in which case the constructor assumes that
            information in the file is correct.

        Returns
        -------
        tuple - binary file pointer, header dictionary
        """

        try:
            #   Open the file for reading in binary format
            f_in = open(filename, 'rb')

            #   Read the lines of header information
            name, value = StandardBinaryFile.convert_stdbin_header(StandardBinaryFile.read_stdbin_header_line(f_in))

            #   This is the header line, so now we can determine how many total lines of header information is
            #   present in the file
            if header_element_count is None:
                header_line_count = int(value)
            elif header_element_count is not None:
                header_line_count = header_element_count

            #   Read through the lines and extract the data as command and values that are inserted into a
            #   dictionary.
            header = dict()
            for i in range(header_line_count - 1):
                #   Split the data in the header line
                name, value = StandardBinaryFile.convert_stdbin_header(StandardBinaryFile.read_stdbin_header_line(f_in))

                #   In effort to make the CSV representation of the data from the TimeHistory functions we need
                #   to ensure that the commas and extra carriage return/line feeds are removed.
                while ',' in name:
                    name = name.replace(',', ';')
                while ',' in value:
                    value = value.replace(',', ';')

                while '\r' in name:
                    name = name.replace('\r', '')
                while '\r' in value:
                    value = value.replace('\r', '')

                while '\n' in name:
                    name = name.replace('\n', '')

                #   Assign the key and value within the dictionary
                header[name] = value

            return f_in, header

        except IndexError:
            f_in.close()

            raise ValueError()
        except ValueError:
            f_in.close()

            raise ValueError()

    @property
    def header(self):
        return self._header

    @property
    def header_line_count(self):
        if self.header is None:
            return None
        else:
            return len(self.header) + 1

    @property
    def data_offset(self):
        """
        This is the number of bytes within the file that you must read before obtaining the data
        """

        return self._data_offset

    def make_wav_file(self, wav_path, archival_location=None, artist=None, commissioning_organization=None,
                      copyright=None, cropping_information=None, originating_object_dimensions=None, engineer_name=None,
                      subject_genre=None, key_words=None, originating_object_medium=None, title=None, subject_name=None,
                      description=None, data_source=None, original_form=None, digitizing_engineer=None,
                      track_number=None):
        """
        The data within the header can be created with the LIST chunk that is common with audio files.  This requires
        the generation of a set of information within the meta_data element of the id3_wave_file that forms the
        information, which is typically at the end of the audio file.  This function converts the data within the
        StandardBinaryFile into a scaled version of the wave file with a LIST tag dataset.
        :param wav_path: str - the output of path for the file
        :param archival_location: str - the location of the original and all additional copies of the data
        :param artist: str - the person who is making the recording
        :param commissioning_organization: str - the organization that requested the measurement
        :param copyright: str - any description of the copyright and classification of the data within the file
        :param cropping_information: str - was the data cropped, is so what was the start and stop sample
        :param originating_object_dimensions: str - any information regarding the dimensions of the object that was
            recorded
        :param engineer_name : str - the name of the engineer that recorded the data
        :param subject_genre : str - the genre of the data
        :param key_words: str - a comma delimited collection of key words that describes this data
        :param originating_object_medium: str - what was the original medium that contained this data
        :param title: str - the title of the file
        :param subject_name: str - a name for the subject of the file
        :param description: str - further descriptions of the data within this file
        :param data_source: str - the name of the source of the data, which is different from the commissioned
            organization in that we want to know where the digital file came from
        :param original_form: str - a description of the original form that this data existed in before the wav file
            was created
        :param digitizing_engineer: str - the name/identifier of the individual who is creating this file - if not
            supplied the username of the individual logged into the computer running this code is used
        :param track_number: int - the track number for this wav file
        """

        #   get the username of the person running this code

        import getpass
        username = getpass.getuser()

        #   Create the wave_file

        wav = WaveFile()

        #   Add the header information to the class

        for key in self._header.keys():
            wav.header[key] = self._header[key]

        #   Now we need to put the generic_time_waveform information into the class object

        wav.samples = self.samples
        wav.start_time = self.time0
        wav.sample_rate = self.sample_rate

        #   Now we can create the specific tags within the common LIST chunk with information from the header

        if archival_location is not None:
            wav.archival_location = archival_location
        if artist is not None:
            wav.artist = artist
        if commissioning_organization is not None:
            wav.commissioning_organization = commissioning_organization
        if copyright is not None:
            wav.copyright = copyright

        wav.creation_date = datetime.now()

        if cropping_information is not None:
            wav.cropping_information = cropping_information
        if originating_object_dimensions is not None:
            wav.originating_object_dimensions = originating_object_dimensions
        if engineer_name is not None:
            wav.engineer_name = engineer_name
        else:
            wav.engineer_name = username
        if subject_genre is not None:
            wav.subject_genre = subject_genre
        if key_words is not None:
            wav.key_words = key_words
        if originating_object_medium is not None:
            wav.originating_object_medium = originating_object_medium
        if title is not None:
            wav.title = title
        else:
            wav.title = os.path.basename(wav_path)
        if subject_name is not None:
            wav.subject_name = subject_name
        if description is not None:
            wav.description = description

        wav.creation_software = "Python, PyTimbre "

        if data_source is not None:
            wav.data_source = data_source
        if original_form is not None:
            wav.original_form = original_form
        if digitizing_engineer is not None:
            wav.digitizing_engineer = digitizing_engineer
        else:
            wav.digitizing_engineer = username

        if track_number is not None:
            wav.track_number = track_number

        #   Save the data to the file

        if not (os.path.exists(os.path.dirname(wav_path))):
            os.makedirs(os.path.dirname(wav_path))

        wav.normalized = True
        wav.save(wav_path)
