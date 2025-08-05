import os, os.path
from io import FileIO
import dateutil.parser
import numpy as np
from datetime import datetime, timedelta
from pytimbre.audio import Waveform
import struct
import scipy.signal
import warnings


class ChunkScanner:
    """
    This class will scan the Wav file, assuming that there is a correctly formatted file, and collect all the various
    chunks that are available within the file.
    """

    def __init__(self, file_path: str):
        """
        This constructor will search through the file and determine the collection of data chunks that exist within the
        correctly formed audio file.
        """

        #   Open the file for reading

        file = open(file_path, 'rb')

        #   Since this is to be canonical, the RIFF size must be the file size minus 8, so let's determine what the file
        #   size actually is so that we can check this as we read the data

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0, 0)

        #   The canonical wave format possesses some very specific structure, but we can examine the data as a series
        #   of data chunks that can be parsed in a similar manner.

        #   The first chunk is required to be the RIFF chunk, with the file size minus 8.

        name = ChunkScanner.read_chunk_name(file)

        if name != "RIFF":
            raise ValueError(
                "A canonical file begins with the RIFF chunk.  This file does not, please provide a "
                "canonical file"
            )

        size = ChunkScanner.read_chunk_size(file)

        # if size + 8 != file_size:
        #     raise ValueError("The RIFF chunk size does not match the file size.  Please provide a canonical file")

        if ChunkScanner.read_chunk_name(file) != "WAVE":
            raise ValueError("Expected canonical wave format with WAVE as the next element, which was not found")

        #   The RIFF chunk is the beginning of the file.  Now we begin to parse the chunks

        current_location = file.tell()
        assert current_location == 12, "The file is not at the correct location"

        self.chunks = list()

        while file.tell() < file_size:
            #   Read the name and size of the chunk

            name = ChunkScanner.read_chunk_name(file)
            if name is None:
                break
            size = ChunkScanner.read_chunk_size(file)
            offset = file.tell()

            #   Add the chunk to the list

            self.chunks.append(ChunkInformation(name, size, offset))

            #   skip the chunk

            file.seek(size, 1)

        file.close()

    @staticmethod
    def read_chunk_size(file):
        """
        This function reads four bytes and formats them as an integer
        :param file: File - the binary file that is to be read
        :return: int - the size of the chunk
        """

        return struct.unpack("<I", file.read(4))[0]

    @staticmethod
    def read_chunk_name(file):
        """
        This function reads the next four bytes from the file and returns the chunk name

        :param file: FILE - the binary file that contains the information
        :return: str - the name of the next chunk
        """

        b_name = file.read(4)
        try:
            name = b_name.decode()
            return name
        except:
            return None

    @property
    def available_chunks(self):
        return self.chunks

    @property
    def format_chunk(self):
        #   Now, every wav file will contain a format chunk so let's find that.

        fmt_chunk_info = None
        for chunk in self.chunks:
            if chunk.chunk_name == "fmt ":
                fmt_chunk_info = chunk
                break
        if fmt_chunk_info is None:
            raise ValueError("There is no format chunk with the description of the file")

        return fmt_chunk_info

    @property
    def peak_chunk(self):

        #   The peak chunk may not be present within the file, but if it is then we will also find that chunk

        peak_chunk_info = None
        for chunk in self.chunks:
            if chunk.chunk_name == "PEAK":
                peak_chunk_info = chunk
                break

        return peak_chunk_info

    @property
    def data_chunk(self):
        chunk_info = None
        for chunk in self.chunks:
            if chunk.chunk_name == "data":
                chunk_info = chunk
                break

        return chunk_info

    @property
    def list_chunk(self):
        chunk_info = None

        for chunk in self.chunks:
            if chunk.chunk_name == "LIST":
                chunk_info = chunk
                break

        return chunk_info

    @property
    def xml_chunk(self):
        chunk_info = None

        for chunk in self.chunks:
            if chunk.chunk_name == "iXML":
                chunk_info = chunk
                break

        return chunk_info

    @property
    def fact_chunk(self):
        chunk_info = None

        for chunk in self.chunks:
            if chunk.chunk_name == "fact":
                chunk_info = chunk
                break

        return chunk_info


class ChunkInformation:
    """
    This class contains simple information about the location of the various chunks within the wav file.
    """

    def __init__(self, name, size, offset=0):
        """
        Default constructor that inserts the information into the correct object so that the chunk can be discovered
        at a later time
        :param name: str - the name of the chunk
        :param size: int - the size in bytes of the chunk
        :param offset: int - the offset within the file of the first byte of this chunk - this is past the name and size
            elements of the chunk (i.e. the chunk start is actually offset - 16)
        """

        if not isinstance(name, str):
            raise ValueError("No valid name provided")
        if not isinstance(size, int):
            raise ValueError("No valid size provided")
        if not isinstance(offset, int):
            raise ValueError("The offset must be an integer")

        self._name = name
        self._size = size
        self._offset = offset

    @property
    def chunk_name(self):
        return self._name

    @property
    def chunk_size(self):
        return self._size

    @property
    def chunk_offset(self):
        return self._offset


class FactChunk(ChunkInformation):
    def __init__(self, reader: FileIO = None, chunk_offset: int = None, chunk_size: int = None, chunk_name: str = None):
        """
        The constructor for the format chunk.  This will contain the ability to read the 16 and 40 byte formatted
        header
        :param reader: File - The binary reader that will represent the data file that we are reading
        :param chunk_offset: int - offset from the beginning of the file where the format chunk data begins
        :param chunk_size: int - the number of bytes to read that contain the data
        """

        if reader is None:
            self._sample_count = 0

            return

        super().__init__(chunk_name, chunk_size, chunk_offset)

        reader.seek(chunk_offset, 0)

        self._sample_count = struct.unpack('<I', reader.read(4))[0]

    @property
    def sample_count(self):
        return self._sample_count


class FormatChunk(ChunkInformation):
    """
    The format chunk is a specialized data chunk found within the wav formatted files.
    """

    def __init__(self, reader: FileIO = None, chunk_offset: int = None, chunk_size: int = None, chunk_name: str = None):
        """
        The constructor for the format chunk.  This will contain the ability to read the 16 and 40 byte formatted
        header
        :param reader: File - The binary reader that will represent the data file that we are reading
        :param chunk_offset: int - offset from the beginning of the file where the format chunk data begins
        :param chunk_size: int - the number of bytes to read that contain the data
        """

        if reader is None:
            self.audio_format = 3
            self.num_channels = 1
            self.fs = 44100
            self.byte_rate = 0
            self.block_align = 0
            self.bits_per_sample = 32

            return

        super().__init__(chunk_name, chunk_size, chunk_offset)

        #   Seek the beginning of the format chunk's data, skipping the name and size

        reader.seek(chunk_offset, 0)

        #   Now read the collection of bytes and determine the elements that we need to represent within the format
        #   chunk class.

        if self.chunk_size == 16:
            #   Now we can parse the information from the format chunk

            self.audio_format = struct.unpack('<H', reader.read(2))[0]

            self.num_channels = struct.unpack('<H', reader.read(2))[0]

            self.fs = struct.unpack('<I', reader.read(4))[0]

            self.byte_rate = struct.unpack('<I', reader.read(4))[0]

            self.block_align = struct.unpack('<H', reader.read(2))[0]

            self.bits_per_sample = struct.unpack('<H', reader.read(2))[0]
        elif self.chunk_size == 40:
            self.audio_format = struct.unpack('<H', reader.read(2))[0]
            self.num_channels = struct.unpack('<H', reader.read(2))[0]
            self.fs = struct.unpack('<I', reader.read(4))[0]
            self.byte_rate = struct.unpack('<I', reader.read(4))[0]
            self.block_align = struct.unpack('<H', reader.read(2))[0]
            self.bits_per_sample = struct.unpack('<H', reader.read(2))[0]
        else:
            try:
                self.audio_format = struct.unpack('<H', reader.read(2))[0]
                self.num_channels = struct.unpack('<H', reader.read(2))[0]
                self.fs = struct.unpack('<I', reader.read(4))[0]
                self.byte_rate = struct.unpack('<I', reader.read(4))[0]
                self.block_align = struct.unpack('<H', reader.read(2))[0]
                self.bits_per_sample = struct.unpack('<H', reader.read(2))[0]
            except Exception as e:
                raise e

    @property
    def waveform_format(self):
        if self.audio_format == 1:
            return "PCM - Uncompressed"
        elif self.audio_format == 3:
            return "IEEE Floating Point"

    @property
    def channel_count(self):
        return self.num_channels

    @channel_count.setter
    def channel_count(self, value):
        self.num_channels = value

    @property
    def sample_rate(self):
        return self.fs

    @sample_rate.setter
    def sample_rate(self, value):
        self.fs = value

    @property
    def sample_bit_size(self):
        return self.bits_per_sample

    @sample_bit_size.setter
    def sample_bit_size(self, value):
        self.bits_per_sample = value

    @staticmethod
    def write_chunk(writer: FileIO, sample_rate: int, bits_per_sample: int = 32, channel_count: int = 1):
        """
        This function writes the contents of the chunk to the output file in the correct format for a canonical wav file
        :param writer: FileIO - the writer for the data - it is assumed that the data will be written to the current
            location of the writer
        :param sample_rate: int - the number of samples per seconds
        :param bits_per_sample: int - the number of bytes per sample
        :param channel_count: int - the number of channels
        """

        block_align = int(np.floor(channel_count * (bits_per_sample / 8)))

        writer.write("fmt ".encode('utf-8'))
        writer.write(struct.pack("<i", 16))  # Format header size
        writer.write(struct.pack("<h", 3))  # format tag 1 = PCM, 3 = IEEE Float
        writer.write(struct.pack("<h", channel_count))  # channel count
        writer.write(struct.pack("<i", int(np.floor(sample_rate))))
        writer.write(struct.pack("<i", int(np.floor(sample_rate)) * block_align))
        writer.write(struct.pack("<h", block_align))
        writer.write(struct.pack("<h", bits_per_sample))


class PeakChunk(ChunkInformation):
    """
    This class contains the information about the peaks within each channel of the wave file
    """

    def __init__(
            self, reader: FileIO = None, offset: int = None, size: int = None, name: str = None,
            channel_count: int = 1
    ):
        """
        Constructor for the peak chunk.  This will read the peak from multiple channels
        :param reader: FileIO - the reader for the chunk data
        :param offset: int - the offset within the file of the actual data of the chunk
        :param size: int - the number of bytes within the chunk
        :param name: str - the name of the chunk
        :param channel_count: int - the number of channels within the wav file
        """

        if reader is None:
            self.peak_value = 1.0
            return

        super().__init__(name, size, offset)

        #   Seek to the beginning of the data within the format chunk

        reader.seek(self.chunk_offset, 0)

        #   Read all the data from the file

        bytes = reader.read(size)

        #   Now we can parse the information from the format chunk

        self.version = struct.unpack("<i", bytes[:4])[0]  # struct.unpack("<i", reader.read(4))
        self.timestamp = struct.unpack("<i", bytes[4:8])[0]
        values = list()
        locations = list()

        s0 = 8
        for i in range(channel_count):
            values.append(struct.unpack("<f", bytes[s0:s0 + 4])[0])
            s0 += 4
            locations.append(struct.unpack("<i", bytes[s0:s0 + 4])[0])
            s0 += 4

        self.peak_value = np.asarray(values, dtype='float')
        self.peak_location = np.asarray(locations, dtype='int')

    @property
    def peak_amplitude(self):
        return self.peak_value

    @peak_amplitude.setter
    def peak_amplitude(self, value):
        self.peak_value = value

    @property
    def peak_sample(self):
        return self.peak_location

    @peak_sample.setter
    def peak_sample(self, values):
        self.peak_location = values

    def write_chunk(self, writer: FileIO):
        """
        This function writes the contents of the chunk into the file at the current position of the FileIO object
        :param writer: FileIO - the writer that will put the data into the correct format at the current position
        """

        writer.write("PEAK".encode('utf-8'))
        size_offset = writer.tell()
        writer.write(struct.pack("<i", 0))  # Size
        start_byte = writer.tell()
        writer.write(struct.pack("<i", 1))  # Version
        writer.write(struct.pack("<i", 0))  # Timestamp

        #   Now write the value and location of all the channel's peak values
        if isinstance(self.peak_value, float):
            writer.write(struct.pack("<f", self.peak_amplitude))
            writer.write(struct.pack("<i", self.peak_sample))
        else:
            if isinstance(self.peak_value, list):
                l = len(self.peak_value)
            elif isinstance(self.peak_value, np.ndarray):
                l = self.peak_value.shape[0]
            else:
                raise Exception("Error, unhandled peak type: {}".format(type(self.peak_value)))
            for i in range(l):
                if isinstance(self.peak_value[i], float):
                    writer.write(struct.pack("<f", self.peak_amplitude[i]))
                    writer.write(struct.pack("<i", self.peak_sample[i]))
                else:
                    for i in range(len(self.peak_value[i])):
                        writer.write(struct.pack("<f", self.peak_amplitude[i]))
                        writer.write(struct.pack("<i", self.peak_sample[i]))

        #   Update the size of the chunk

        chunk_size = writer.tell() - start_byte

        #   Go back and update the size of the chunk

        writer.seek(size_offset, 0)
        writer.write(struct.pack("<i", chunk_size))

        #   Return to the end of the chunk

        writer.seek(chunk_size, 1)


class DataChunk(ChunkInformation):
    """
    This class understand the various types of data formats that exist within wav files
    """

    def __init__(
            self, reader: FileIO, offset: int, size: int, name: str, fmt: FormatChunk, peak: PeakChunk,
            s0: int = None, s1: int = None, normalized: bool = False
    ):
        """
        This constructor employs the Format_Chunk object to understand how to read the data from the wav file.
        :param reader: FileIO - The file object to read the data
        :param offset: int - the offset of the beginning of the data chunk's data
        :param size: int - the overall size of the data chunk's data
        :param name: str - the name of the chunk
        :param fmt: Format_Chunk - the object that understands how to format the waveform
        :param s0: int - the starting sample
        :param s1: int - the ending sample
        :param normalized: bool - a flag determining whether the contents of the data files were normalized to the peak
            values
        """

        super().__init__(name, size, offset)

        if peak is None:
            peak = PeakChunk()

        #   Move to the beginning of the data chunk and read the number of bytes that this chunk contains
        reader.seek(self.chunk_offset, 0)

        #   Now we need to unpack the bytes using the correct format and the struct.unpack command.  The number of
        #   samples is the total size, in bytes, divided by the bytes per sample, divided by the number of channels.
        sample_count = int(np.floor(self.chunk_size / (fmt.bits_per_sample / 8) / fmt.channel_count))
        read_size = self.chunk_size

        #   Before we move through the reading of the samples, we need to enable the removal of data through the use of
        #   the s0 and s1 values.  This means that we want to remove the first s0 samples from all channels, and then
        #   we move the cursor this many bits past the current location.
        start_bits = 0
        if s0 is not None:
            #   First determine the number of bits to move if there is only a single channel
            start_bits = int(np.floor(s0 * fmt.sample_bit_size / 8))

            #   Now multiply by the number of channels
            start_bits *= fmt.channel_count
            reader.seek(start_bits, 1)

            #   Remove the beginning samples that we have moved over
            sample_count -= s0
            read_size -= start_bits

        if s1 is not None:
            if s0 is not None:
                #   Determine the number of samples to read
                sample_count = s1 - s0
            else:
                #   This is if there is no s0 but an s1
                sample_count = s1

            #   Now use this size to fix the number of bytes to read
            read_size = int(np.floor(sample_count * (fmt.sample_bit_size / 8) * fmt.channel_count))

        #   The size of the chunk includes all data, regardless of the number of channels within the file.  So we can
        #   just read all the bytes into an array that we will parse through sequentially.
        byte_array = reader.read(read_size)

        #   Now create the sample array, which is the number of samples in the first index, and the number of channels
        #   in the second index.  The format is floating point, so we will need to perform the conversion for each
        #   sample regardless of the type within the file.
        sample_count = int(np.floor(sample_count))
        samples = np.zeros((sample_count, fmt.channel_count), dtype='float')

        #   The order of the samples is channel 0 sample 0, channel 1 sample 0, ... channel N sample 0, channel 0
        #   sample 1...So we first loop through the samples, then the channels.  However, to keep track of where we are
        #   within the array that was read from the data there will be an index outside the loops.
        #
        #   Start by moving through the samples
        idx = 0
        sample_size = int(np.floor(fmt.bits_per_sample / 8))

        #   Now that we know the sample size, we have to compare that to the type of audio stored in the DataChunk.
        #   This is specified by the audio_format flag in the FormatChunk. If the flag is three, then the values are
        #   floating point and the sample_size better be 4. If not then there is an error that is raised.
        if sample_size == 4 and fmt.audio_format == 3:
            #   This is the IEEE Float and 32-bit, which is required for the floating point value
            samples = np.asarray(
                struct.unpack(
                    "<{}f".format(int(np.floor(sample_count * fmt.channel_count))),
                    byte_array
                ),
                dtype='float'
            )
        elif sample_size != 4 and fmt.audio_format == 3:
            raise ValueError("There is a missmatch between the bit size of the samples and the sample representation. "
                             "You must use a 32-bit floating point value for PCM = 3 files.")

        #   If the sample size is 3, this means that there is a slight compression in the representation and the
        #   sample must be read as a three element byte array, then shifted to account for the remaining bit. Once
        #   the bit has been shifted, we convert the 4 byte value to a floating point and divide by the maximum
        #   value of a 32-bit integer.
        elif sample_size == 3:
            tmp = list([0, 0, 0, 0])

            samples = np.zeros((int(len(byte_array) / 3),), dtype=float)
            n = 0
            for i in range(0, len(byte_array), 3):
                tmp[1] = byte_array[i]
                tmp[2] = byte_array[i + 1]
                tmp[3] = byte_array[i + 2]

                samples[n] = struct.unpack("<i", bytearray(tmp))[0]
                n += 1

            samples = np.asarray(samples, dtype=float)
            samples /= np.iinfo(np.int32).max
        #   If the audio_format flag is one, then the values in the file are represented as integers. However,
        #   there are multiple flavors of integers, so we need additional logic to determine how to read the integer
        #   values and convert them to floating point. We do this because we want to use floating point values to
        #   represent the pressure within the waveform.
        elif fmt.audio_format == 1:
            #   This is all the integer formatted data.
            if sample_size == 1: # Character integer values
                data = struct.unpack("<{}B".format(int(np.floor(sample_count * fmt.channel_count))), byte_array)
                np_array = np.array(data, dtype=np.float64) - 127
                samples = (np_array/np.iinfo(np.uint8).max) * 2
            elif sample_size == 2: # short integer values
                data = struct.unpack("<{}h".format(int(np.floor(sample_count * fmt.channel_count))), byte_array)
                samples = np.asarray(data, dtype='float') / np.iinfo(np.int16).max
            elif sample_size == 4: # integer values
                data = struct.unpack("<{}i".format(int(np.floor(sample_count * fmt.channel_count))), byte_array)
                samples = np.asarray(data, dtype='float') / np.iinfo(np.int32).max

        elif fmt.audio_format > 500:
            samples = np.asarray(
                struct.unpack(
                    "<{}i".format(int(np.floor(sample_count * fmt.channel_count))),
                    byte_array
                ),
                dtype='float'
            ) / 2 ** 31

        #   Scale the samples by the peak levels

        #   Assign the data to the class's sample object

        self.samples = samples.reshape((sample_count, fmt.channel_count))

        if normalized:
            for i in range(fmt.channel_count):
                self.samples[:, i] *= peak.peak_value[i]

        if fmt.channel_count == 1:
            self.samples = self.samples.reshape((-1,))

    @property
    def waveform(self):
        return self.samples


class ListChunk(ChunkInformation):
    """
    This is an extra chunk that can provide metadata to the user through customizable fields.
    """

    def __init__(self, reader: FileIO = None, size: int = None, offset: int = None, name: str = None):
        """
        This will construct the information within the class and read the contents of the LIST chunk
        :param reader: FileIO - the binary reader that will be able to extract the information from the file
        :param size: int - the size of the data chunk
        :param offset: int - the offset of the chunk's data
        :param name: str - the name of the chunk

        https://www.recordingblogs.com/wiki/list-chunk-of-a-wave-file#:~:text=List%20chunk%20%28of%20a%20RIFF%20file
        %29%20%20,%20Depends%20on%20the%20list%20type%20ID%20
        """

        import json

        if reader is None:
            #   Create the dictionaries that will be used for the creation of the data

            self.time0 = datetime.fromtimestamp(0)
            self.meta_data = {
                'creation_date': self.time0
            }
            self.header = dict()
            return

        super().__init__(name, size, offset)

        self.meta_data = dict()
        self.header = dict()

        #   Move to the offset within the file where the LIST chunk starts and read the data
        reader.seek(self.chunk_offset, 0)
        bytes = reader.read(self.chunk_size)

        #   The expected keyword should contain INFO for the description
        if bytes[:4] == b"INFO":
            #   Now we can begin parsing this information into elements that are important for the understanding
            #   of the audio file.

            offset = 4

            while offset < len(bytes):
                #   Get the command
                cmd = bytes[offset:offset + 4].decode()

                #   Get the size of the string
                size = int.from_bytes(bytes[offset + 4:offset + 8], 'little')

                #   Read the string
                data = bytes[offset + 8:offset + 8 + size].decode()

                #   Remove the null characters that exist at the end of the data
                if '\0' in data:
                    while data[-1] == '\0' and len(data) > 0:
                        data = data[:-1]
                        if len(data) <= 0:
                            break

                offset += 8 + size

                #   Determine what the information represents
                if cmd == "IARL":
                    self.meta_data["archival_location"] = data
                elif cmd == "IART":
                    self.meta_data["artist"] = data
                elif cmd == "ICMS":
                    self.meta_data["commissioned_organization"] = data
                elif cmd == "ICMT":
                    self.meta_data["general_comments"] = data

                    # Now we understand that the majority of the header does not actually fall within the
                    # standard LIST elements.  So we created a comma delimited arrangement of header name and
                    # we can now separate apart.
                    if len(data) > 0:
                        if "|" in data:
                            sub_elements = data.split("|")

                            for header_element in sub_elements:
                                cmd = header_element.split('=')[0]
                                data = header_element.split('=')[1]

                                self.header[cmd] = data
                        if "{" in data and "}" in data:
                            #   This is likely a JSON formatted string, so we will attempt to use the JSON decoder to
                            #   actually read the data from the string
                            self.header[cmd] = json.loads(data)
                            for key in self.header[cmd].keys():
                                if key == 'sens_l':
                                    self.meta_data['left_channel_sensor_sensitivity'] = self.header[cmd][key]
                                elif key == 'sens_r':
                                    self.meta_data['right_channel_sensor_sensitivity'] = self.header[cmd][key]
                                elif key == 'gain_l':
                                    self.meta_data['left_channel_gain'] = self.header[cmd][key]
                                elif key == 'gain_r':
                                    self.meta_data['right_channel_gain'] = self.header[cmd][key]
                                elif key == 'v_scale':
                                    self.meta_data['vertical_scale'] = self.header[cmd][key]
                                elif key == 'gps_lat':
                                    self.meta_data['latitude'] = self.header[cmd][key]
                                elif key == 'gps_lon':
                                    self.meta_data['longitude'] = self.header[cmd][key]
                                elif key == 'gpx_fix':
                                    self.meta_data['gps_fix_quality'] = self.header[cmd][key]
                                elif key == 'gps_sat':
                                    self.meta_data['gps_satellite_count'] = self.header[cmd][key]
                                elif key == 'gps_alt':
                                    self.meta_data['gps_altitude'] = self.header[cmd][key]
                                elif key == 'gps_spd':
                                    self.meta_data['gps_ground_speed'] = self.header[cmd][key]
                                elif key == 'gps_trk_ang':
                                    self.meta_data['gps_track_heading_angle'] = self.header[cmd][key]
                                elif key == 'gps_hor_dil':
                                    self.meta_data['gps_horizontal_dilution'] = self.header[cmd][key]
                                elif key == 'gps_ht_gd':
                                    self.meta_data['gps_height_above_ground'] = self.header[cmd][key]
                                elif key == 'gps_ts':
                                    self.meta_data['gps_time_stamp'] = self.header[cmd][key]
                                elif key == 'gps_ts_sub':
                                    self.meta_data['gps_time_stamp'] = self.header[cmd][key]
                                    self.time0 = dateutil.parser.parse(self.meta_data['gps_time_stamp'])
                elif cmd == "ICOP":
                    self.meta_data['copyright'] = data
                elif cmd == "ICRD":
                    self.meta_data['creation_date'] = data
                elif cmd == "ICRP":
                    self.meta_data['cropping_information'] = data
                elif cmd == "IDIM":
                    self.meta_data['originating_object_dimensions'] = data
                elif cmd == "IDPI":
                    self.meta_data['dots_per_inch'] = data
                elif cmd == "IENG":
                    self.meta_data['engineer_name'] = data
                elif cmd == "IGNR":
                    self.meta_data['subject_genre'] = data
                elif cmd == "IKEY":
                    self.meta_data['key_words'] = data
                elif cmd == "ILGT":
                    self.meta_data['lightness_settings'] = data
                elif cmd == "IMED":
                    self.meta_data['originating_object_medium'] = data
                elif cmd == "INAM":
                    self.meta_data['title'] = data
                elif cmd == "IPLT":
                    self.meta_data['color_palette_count'] = data
                elif cmd == "IPRD":
                    self.meta_data['subject_name'] = data
                elif cmd == "ISBJ":
                    self.meta_data['description'] = data
                elif cmd == "ISFT":
                    self.meta_data['creation_software'] = data
                elif cmd == "ISRC":
                    self.meta_data['data_source'] = data
                elif cmd == "ISRF":
                    self.meta_data['original_form'] = data
                elif cmd == "ITCH":
                    self.meta_data['digitizing_engineer'] = data
                elif cmd == "ITRK":
                    try:
                        self.meta_data['track_no'] = int(data)
                    except ValueError as err:
                        self.meta_data['track_no'] = data

    @property
    def file_start_time(self) -> datetime:
        return self.time0

    @property
    def archival_location(self):
        if "archival_location" in self.meta_data.keys():
            return self.meta_data["archival_location"]
        else:
            return None

    @property
    def artist(self):
        if "artist" in self.meta_data.keys():
            return self.meta_data["artist"]
        else:
            return None

    @property
    def commissioned_organization(self):
        if "commissioned_organization" in self.meta_data.keys():
            return self.meta_data["commissioned_organization"]
        else:
            return None

    @property
    def general_comments(self):
        if "general_comments" in self.meta_data.keys():
            return self.meta_data["general_comments"]
        else:
            return None

    @property
    def copyright(self):
        if "copyright" in self.meta_data.keys():
            return self.meta_data["copyright"]
        else:
            return None

    @property
    def creation_date(self):
        if "creation_date" in self.meta_data.keys():
            return self.meta_data["creation_date"]
        else:
            return None

    @property
    def cropping_information(self):
        if "cropping_information" in self.meta_data.keys():
            return self.meta_data["cropping_information"]
        else:
            return None

    @property
    def originating_object_dimensions(self):
        if "originating_object_dimensions" in self.meta_data.keys():
            return self.meta_data["originating_object_dimensions"]
        else:
            return None

    @property
    def dots_per_inch(self):
        if "dots_per_inch" in self.meta_data.keys():
            return self.meta_data["dots_per_inch"]
        else:
            return None

    @property
    def engineer_name(self):
        if "engineer_name" in self.meta_data.keys():
            return self.meta_data["engineer_name"]
        else:
            return None

    @property
    def subject_genre(self):
        if "subject_genre" in self.meta_data.keys():
            return self.meta_data["subject_genre"]
        else:
            return None

    @property
    def key_words(self):
        if "key_words" in self.meta_data.keys():
            return self.meta_data["key_words"]
        else:
            return None

    @property
    def lightness_settings(self):
        if "lightness_settings" in self.meta_data.keys():
            return self.meta_data["lightness_settings"]
        else:
            return None

    @property
    def originating_object_medium(self):
        if "originating_object_medium" in self.meta_data.keys():
            return self.meta_data["originating_object_medium"]
        else:
            return None

    @property
    def title(self):
        if "title" in self.meta_data.keys():
            return self.meta_data["title"]
        else:
            return None

    @property
    def color_palette_count(self):
        if "color_palette_count" in self.meta_data.keys():
            return self.meta_data["color_palette_count"]
        else:
            return None

    @property
    def subject_name(self):
        if "subject_name" in self.meta_data.keys():
            return self.meta_data["subject_name"]
        else:
            return None

    @property
    def description(self):
        if "description" in self.meta_data.keys():
            return self.meta_data["description"]
        else:
            return None

    @property
    def creation_software(self):
        if "creation_software" in self.meta_data.keys():
            return self.meta_data["creation_software"]
        else:
            return None

    @property
    def data_source(self):
        if "data_source" in self.meta_data.keys():
            return self.meta_data["data_source"]
        else:
            return None

    @property
    def original_form(self):
        if "original_form" in self.meta_data.keys():
            return self.meta_data["original_form"]
        else:
            return None

    @property
    def digitizing_engineer(self):
        if "digitizing_engineer" in self.meta_data.keys():
            return self.meta_data["digitizing_engineer"]
        else:
            return None

    @property
    def track_number(self):
        if "track_no" in self.meta_data.keys():
            return self.meta_data["track_no"]
        else:
            return -1

    def write_chunk(self, writer: FileIO):
        """
        This function writes the contents of this LIST chunk to the file at the current cursor location
        :param writer: FileIO - The object controlling how the data is written to the file
        """

        #   Write the header command
        writer.write("LIST".encode('utf-8'))

        #   Get the position so that we know where to write the size of the chunk
        size_offset = writer.tell()

        #   At this point we do not know how big the chunk will be, so we will write a zero 4 byte value
        writer.write(struct.pack("<i", 0))

        #   Now store the location within the file so that we can calculate how big the chunk is
        start_byte = writer.tell()
        writer.write("INFO".encode('utf-8'))

        #   Specify the names that we want to use in the creation of the contents of the list chunk. This dictionary
        #   will contain the names of the objects in the metadata dictionary, and the data in the dictionary will be
        #   the LIST chunk command. This is in effort to simplify the structure of this function.
        list_commands = {"archival_location": "IARL",
                         "artist": "IART",
                         "commissioned_organization": "ICMS",
                         "general_comments": "ICMT",
                         "copyright": "ICOP",
                         "creation_date": "ICRD",
                         "cropping_information": "ICRP",
                         "originating_object_dimensions": "IDIM",
                         "dots_per_inch": "IDPI",
                         "engineer_name": "IENG",
                         "subject_genre": "IGNR",
                         "key_words": "IKEY",
                         "lightness_settings": "ILGT",
                         "originating_object_medium": "IMED",
                         "title": "INAM",
                         "color_palette_count": "IPLT",
                         "subject_name": "IPRD",
                         "description": "ISBJ",
                         "creation_software": "ISFT",
                         "data_source": "ISRC",
                         "original_form": "ISRF",
                         "digitizing_engineer": "ITCH",
                         "track_no": "ITRK"}

        for key in list_commands.keys():
            if key in self.meta_data.keys():
                ListChunk._write_list_chunk(writer, list_commands[key], self.meta_data[key])

        if self.header is not None:
            if isinstance(self.header, dict):
                elements = list()
                for key in self.header.keys():
                    elements.append("{}={}".format(key, self.header[key]))

                ListChunk._write_list_chunk(writer, "ICMT", "|".join(elements))
            else:
                ListChunk._write_list_chunk(writer, "ICMT", self.meta_data["general_comments"])

        # #   Work through each of the potential elements that may exist within the metadata and write it to the output
        # #   file if it exists within the dictionary
        # if "archival_location" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IARL", self.meta_data["archival_location"])
        #
        # if "artist" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IART", self.meta_data["artist"])
        #
        # if "commissioned_organization" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ICMS", self.meta_data['commissioned_organization'])
        #
        # if "general_comments" in self.meta_data.keys() or self.header is not None:
        #     if self.header is not None:
        #         if isinstance(self.header, dict):
        #             elements = list()
        #             for key in self.header.keys():
        #                 elements.append("{}={}".format(key, self.header[key]))
        #
        #         self._write_list_chunk(writer, "ICMT", "|".join(elements))
        #     else:
        #         self._write_list_chunk(writer, "ICMT", self.meta_data["general_comments"])
        #
        # if "copyright" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ICOP", self.meta_data['copyright'])
        #
        # #   To provide the start time inside the wave files we will ensure that the WaveFile class always creates a
        # #   list chunk, and that the chunk will always contain a creation date object. Thus we do not check to see if
        # #   it exists within the dictionary.
        # self._write_list_chunk(writer, "ICRD", datetime.strftime(self.time0, "%Y-%m-%d %H:%M:%S.%f"))
        #
        # if "cropping_information" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ICRP", self.meta_data['cropping_information'])
        #
        # if "originating_object_dimensions" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IDIM", self.meta_data['originating_object_dimensions'])
        #
        # if "dots_per_inch" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IDPI", self.meta_data['dots_per_inch'])
        #
        # if "engineer_name" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IENG", self.meta_data['engineer_name'])
        #
        # if "subject_genre" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IGNR", self.meta_data['subject_genre'])
        #
        # if "key_words" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IKEY", self.meta_data['key_words'])
        #
        # if "lightness_settings" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ILGT", self.meta_data['lightness_settings'])
        #
        # if "originating_object_medium" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IMED", self.meta_data['originating_object_medium'])
        #
        # if "title" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "INAM", self.meta_data['title'])
        #
        # if "color_palette_count" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IPLT", self.meta_data['color_palette_count'])
        #
        # if "subject_name" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "IPRD", self.meta_data['subject_name'])
        #
        # if "description" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ISBJ", self.meta_data['description'])
        #
        # if "creation_software" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ISFT", self.meta_data['creation_software'])
        #
        # if "data_source" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ISRC", self.meta_data['data_source'])
        #
        # if "original_form" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ISRF", self.meta_data['original_form'])
        #
        # if "digitizing_engineer" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ITCH", self.meta_data['digitizing_engineer'])
        #
        # if "track_no" in self.meta_data.keys():
        #     self._write_list_chunk(writer, "ITRK", self.meta_data['track_no'])

        #   Now that we have walked through each of the potential elements of the LIST chunk, we need to determine the
        #   size of the chunk
        chunk_size = writer.tell() - start_byte

        #   Update the size
        writer.seek(size_offset, 0)
        writer.write(struct.pack("<i", chunk_size))

        #   Now move back to the end of the file
        writer.seek(0, 2)

    @staticmethod
    def _write_list_chunk(writer: FileIO, id: str, contents):
        """
        This is a private helper function that assists in writing the data to the LIST chunk.
        :param writer: FileIO - the writer object
        :param id: str - the string identifier for the chunk that is within the accepted LIST commands
        :param contents: str - the data to write to the file
        """

        if not isinstance(contents, str):
            contents = "{}".format(contents)

        byte_count = 0

        #   write the command
        writer.write(id.encode('utf-8'))

        #   post-pend the null character
        contents += '\0'

        #   Ensure that there is an even number of bytes
        if len(contents) % 2 != 0:
            contents += '\0'

        #   Write the length of the string in bytes
        writer.write(struct.pack("<i", len(contents)))
        byte_count += 8
        writer.write(contents.encode('utf-8'))
        byte_count += len(contents)

        return byte_count


class XMLChunk(ChunkInformation):
    """
    The SITH files are formatted in the broadcast wave file format.  This means there is a portion of the file that is
    formatted with an XML structure.  Within this structure is the start time of the audio file.  This will be used to
    override the start time that comes from anywhere else.

    see also: http://www.gallery.co.uk/ixml/
    """

    def __init__(self, reader: FileIO = None, size: int = None, offset: int = None, name: str = None):
        """
        This constructor will obtain the information from the file and insert it into the class
        """

        import xml.etree.ElementTree

        self.version = None
        self.scene = None
        self.take = None
        self.user_bits = None
        self.file_uid = None
        self.note = None
        self.speed_note = None
        self.speed_master_speed = None
        self.speed_current_speed = None
        self.speed_timecode_flag = None
        self.speed_timecode_rate = None
        self.speed_file_sample_rate = None
        self.speed_audio_bit_depth = None
        self.speed_digitizer_sample_rate = None
        self.speed_timestamp_sample_rate = None
        self.speed_timestamp_samples_since_midnight_hi = None
        self.speed_timestamp_samples_since_midnight_lo = None
        self.history = None
        self.file_set = None
        self.track_list = None
        self.bwf_originator = None
        self.bwf_date = None
        self.bwf_time = None
        self.bwf_time_ref_lo = None
        self.bwf_time_ref_hi = None
        self.bwf_verion = None
        self.bwf_id = None

        month = None
        day = None
        year = None

        #   Call the parent constructor
        super().__init__(name, size, offset)

        #   Move to the offset point within the file reader and read the data from the file
        if (reader is not None) and (offset is not None) and (size is not None):
            reader.seek(offset, 0)

            self.xml_string = reader.read(size).decode()

            #   Now use the built-in xml parser to extract information about the iXML data
            tree = xml.etree.ElementTree.fromstring(self.xml_string)

            #   Now loop through the child nodes of this root
            for child in tree:
                if child.tag == "IXML_VERSION":
                    self.version = float(child.text)
                elif child.tag == "PROJECT":
                    self.project = child.text
                elif child.tag == "SCENE":
                    self.scene = child.text
                elif child.tag == "TAKE":
                    self.take = child.text
                elif child.tag == "UBITS":
                    self.user_bits = child.text

                    #   Now use the user bits and timestamp values to build the start time
                    month = int(self.user_bits[:2])
                    day = int(self.user_bits[2:4])
                    year = int(self.user_bits[4:6]) + 2000
                elif child.tag == "FILE_UID":
                    self.file_uid = child.text
                elif child.tag == "NOTE":
                    self.note = child.text
                elif child.tag == "SPEED":
                    for node in child:
                        if node.tag == "NOTE":
                            self.speed_note = node.text
                        elif node.tag == "MASTER_SPEED":
                            self.speed_master_speed = node.text
                        elif node.tag == "CURRENT_SPEED":
                            self.speed_current_speed = node.text
                        elif node.tag == "TIMECODE_FLAG":
                            self.speed_timecode_flag = node.text
                        elif node.tag == "TIMECODE_RATE":
                            self.speed_timecode_rate = node.text
                        elif node.tag == "FILE_SAMPLE_RATE":
                            self.speed_file_sample_rate = float(node.text)
                        elif node.tag == "AUDIO_BIT_DEPTH":
                            self.speed_audio_bit_depth = float(node.text)
                        elif node.tag == "DIGITIZER_SAMPLE_RATE":
                            self.speed_digitizer_sample_rate = float(node.text)
                        elif node.tag == "TIMESTAMP_SAMPLE_RATE":
                            self.speed_timestamp_sample_rate = node.text
                        elif node.tag == "TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI":
                            self.speed_timestamp_samples_since_midnight_hi = int(node.text)
                        elif node.tag == "TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO":
                            self.speed_timestamp_samples_since_midnight_lo = int(node.text)
                elif child.tag == "HISTORY":
                    self.history = child.text
                elif child.tag == "FILE_SET":
                    self.file_set = child.text
                elif child.tag == "TRACK_LIST":
                    self.track_list = child.text
                elif child.tag == "BEXT":
                    for node in child:
                        if node.tag == "BWF_ORIGINATION_DATE":
                            dt = dateutil.parser.parse(node.text)
                            month = dt.month
                            day = dt.day
                            year = dt.year
                        elif node.tag == "BWF_ORIGINATOR":
                            self.bwf_originator = node.text
                        elif node.tag == "BWF_ORIGINATION_TIME":
                            self.bwf_time = node.text
                        elif node.tag == "BWF_TIME_REFERENCE_LOW":
                            self.bwf_time_ref_lo = int(node.text)
                        elif node.tag == "BWF_TIME_REFERENCE_HIGH":
                            self.bwf_time_ref_hi = int(node.text)
                        elif node.tag == "BWF_VERSION":
                            self.version = int(node.text)
                        elif node.tag == "BWF_ID":
                            self.bwf.id = node.text

            if month is None or day is None or year is None:
                raise ValueError("The iXML chunk was not formatted in a manner that is recognized by PyTimbre")

            if self.speed_timestamp_samples_since_midnight_hi is not None and \
                self.speed_timestamp_samples_since_midnight_lo is not None and \
                self.speed_file_sample_rate is not None:
                hi_bits = float(self.speed_timestamp_samples_since_midnight_hi) * 2 ** 32
                time_past_midnight = ((hi_bits + float(self.speed_timestamp_samples_since_midnight_lo)) /
                                      self.speed_file_sample_rate)

                self.start_time = datetime(year, month, day) + timedelta(seconds=time_past_midnight)
            elif self.bwf_time is not None:
                dt = dateutil.parser.parse(self.bwf_time)
                self.start_time = datetime(year, month, day, dt.hour, dt.minute, dt.second)


class WaveFile(Waveform):
    """
    This class mimics information within the NAudio interface and will read a wave file, however it will only process
    the canonical chunks: RIFF, WAVE, fmt, and data.

    http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html

    In favor of using the LIST chunk within the WaveFile rather than using the Waveform.start_time, properties were
    created within this class to expose the creation date property within the list chunk to hold and expose the start
    time of the waveform.
    """

    @staticmethod
    def audio_info(path: str):
        """
        Sometimes it is important to obtain information about the audio within the wave file without actually reading
        the audio data.  This will scan the chunks and extract the information about the audio from that info.

        :param path: str - the path to the audio file
        :returns: dict

        Remarks
        -------
        20230120 - FSM - changed from tuple to dictionary to provide some context for the values within the returned
            object.
        20240417 - FSM - Updated this function to return values from the RAAS system developed by AFRL for acoustic
            recordings
        """

        #   Open the file and list the chunks that exist within the object
        scanner = ChunkScanner(path)

        #   open the path to extract the information from the file without having to read all the contents of the file
        with (open(path, 'rb') as file):

            #   The format chunk is required by all wav files
            format_chunk = FormatChunk(
                file, scanner.format_chunk.chunk_offset, scanner.format_chunk.chunk_size,
                scanner.format_chunk.chunk_name
            )

            #   If there is a peak chunk, read it

            if scanner.peak_chunk is not None:
                peak_chunk = PeakChunk(
                    file, scanner.peak_chunk.chunk_offset, scanner.peak_chunk.chunk_size,
                    scanner.peak_chunk.chunk_name, format_chunk.channel_count
                )
            else:
                peak_chunk = None

            #   If there is a list chunk, read it

            if scanner.list_chunk is not None:
                list_chunk = ListChunk(
                    file, scanner.list_chunk.chunk_size, scanner.list_chunk.chunk_offset,
                    scanner.list_chunk.chunk_name
                )

                if list_chunk.cropping_information is not None:
                    if list_chunk.cropping_information == "normalized":
                        normalized = True
                    else:
                        normlized = False
                else:
                    normalized = False

                if list_chunk.file_start_time is not None:
                    time0 = list_chunk.file_start_time
            else:
                list_chunk = None
                time0 = 0
                normalized = False

            samples_per_channel = scanner.data_chunk.chunk_size / ((format_chunk.bits_per_sample / 8) /
                                                                   format_chunk.channel_count)
            duration = samples_per_channel / format_chunk.sample_rate

            information = {'sample_rate': format_chunk.sample_rate,
                           "channel_count": format_chunk.channel_count,
                           'byte_size': format_chunk.bits_per_sample / 8,
                           'is_normalized': normalized,
                           'start_time': time0,
                           'has_peak_chunk': scanner.peak_chunk is not None,
                           'has_list_chunk': scanner.list_chunk is not None,
                           'has_xml_chunk': scanner.xml_chunk is not None,
                           'data_chunk_size': scanner.data_chunk.chunk_size}
            if list_chunk is not None:
                for key in list_chunk.meta_data.keys():
                    information[key] = list_chunk.meta_data[key]

            if peak_chunk is not None:
                information['peak_count'] = len(peak_chunk.peak_sample)
                for i in range(len(peak_chunk.peak_sample)):
                    information['peak {} sample'.format(i)] = peak_chunk.peak_sample[i]
                    information['peak {} level'.format(i)] = peak_chunk.peak_amplitude[i]
                    if list_chunk is not None:

                        information['left_channel_gain (dB)'] = list_chunk.meta_data['left_channel_gain'],
                        information['right_channel_gain (dB)'] = list_chunk.meta_data['right_channel_gain'],
                        information['left_channel_sensor_sensitivity'] = list_chunk.meta_data[
                            'left_channel_sensor_sensitivity'],
                        information['right_channel_sensor_sensitivity'] = list_chunk.meta_data[
                            'right_channel_sensor_sensitivity']

                    else:
                        information['left_channel_gain (dB)'] = None
                        information['right_channel_gain (dB)'] = None
                        information['left_channel_sensor_sensitivity'] = None
                        information['right_channel_sensor_sensitivity'] = None
                        information['peak {} level'.format(i)] = peak_chunk.peak_amplitude[i]

        return information

    def _read_format_chunk(self, file):
        """
        To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

        :param file:
            The file reader that provides access to the file's contents
        """
        self.format_chunk = FormatChunk(
            file,
            self.scanner.format_chunk.chunk_offset,
            self.scanner.format_chunk.chunk_size,
            self.scanner.format_chunk.chunk_name
        )
        self.sample_rate = self.format_chunk.sample_rate

    def _read_peak_chunk(self, file):
        """
        To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

        :param file:
            The file reader that provides access to the file's contents
        """
        if self.scanner.peak_chunk is not None:
            self.peak_chunk = PeakChunk(
                file,
                self.scanner.peak_chunk.chunk_offset,
                self.scanner.peak_chunk.chunk_size,
                self.scanner.peak_chunk.chunk_name,
                self.format_chunk.channel_count
            )
        else:
            self.peak_chunk = None

    def _read_list_chunk(self, file):
        """
        To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

        :param file:
            The file reader that provides access to the file's contents
        """

        if self.scanner.list_chunk is not None:
            self.list_chunk = ListChunk(
                file,
                self.scanner.list_chunk.chunk_size,
                self.scanner.list_chunk.chunk_offset,
                self.scanner.list_chunk.chunk_name
            )
            if self.list_chunk.cropping_information is not None:
                if self.list_chunk.cropping_information == "normalized":
                    self.normalized = True
                else:
                    self.normalized = False
            else:
                self.normalized = False

            if 'gps_time' in self.list_chunk.meta_data.keys():
                self.start_time = dateutil.parser.parse(self.list_chunk.meta_data['gps_time'])
        else:
            #   If there is no list chunk in the file, create one so that we can hold the start_time data for the
            #   waveform
            self.list_chunk = ListChunk()
            self.normalized = False

    def _read_xml_chunk(self, file):
        """
        To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

        :param file:
            The file reader that provides access to the file's contents
        """
        if self.scanner.xml_chunk is not None:
            self.xml_chunk = XMLChunk(
                file,
                self.scanner.xml_chunk.chunk_size,
                self.scanner.xml_chunk.chunk_offset,
                self.scanner.xml_chunk.chunk_name
            )

            #   You can store the start time in the XML chunk if using Broadcast Wave Format. So this should be
            #   called after the _read_list_chunk so that we can guarantee that there is a list chunk within the
            #   class and that the time is overwritten based on what was contained in the XML chunk
            self.start_time = self.xml_chunk.start_time
        else:
            self.xml_chunk = None

    def _read_fact_chunk(self, file):
        """
        To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

        :param file:
            The file reader that provides access to the file's contents
        """
        if self.scanner.fact_chunk is not None:
            self.fact_chunk = FactChunk(
                file,
                self.scanner.format_chunk.chunk_offset,
                self.scanner.format_chunk.chunk_offset,
                self.scanner.format_chunk.chunk_name
            )
        else:
            self.fact_chunk = None

    def _read_data_chunk(self, file, s0: int, s1: int):
        """
        To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

        :param file:
            The file reader that provides access to the file's contents
        :param s0:
            The start sample for reading the data from the file
        :param s1:
            The end sample for reading the data from the file
        """
        self.data_chunk = DataChunk(
            file,
            self.scanner.data_chunk.chunk_offset,
            self.scanner.data_chunk.chunk_size,
            self.scanner.data_chunk.chunk_name,
            self.format_chunk,
            self.peak_chunk,
            s0,
            s1,
            self.normalized
        )

    def _read_file(self, path: str, s0: int, s1: int, get_peak: bool):
        """
        This function reads the contents of the WaveFile based on the canonical format.

        :param path:
            The path to the file that we want to read.
        :param s0:
            The start sample for reading the data from the file
        :param s1:
            The end sample for reading the data from the file
        """

        #   Store the name of the file within the property
        self.filename = path

        #   Parse the chunks
        self.scanner = ChunkScanner(self.filename)

        #   Now open the file and read the information from the format and peak chunks for the class
        with open(self.filename, 'rb') as file:
            #   Call functions within the protected section of the class to read the various chunks, if they exist
            #   within the file
            self._read_format_chunk(file)
            self._read_peak_chunk(file)
            self._read_list_chunk(file)
            self._read_xml_chunk(file)
            self._read_fact_chunk(file)
            self._read_data_chunk(file, s0, s1)

            #   If the peak chunk was not read from the file, we need to create one from the data that was read from
            #   the wav file.

            if self.peak_chunk is None and get_peak:
                self.peak_chunk = PeakChunk()
                self.peak_chunk.peak_amplitude = np.max(self.data_chunk.waveform, axis=0)
                self.peak_chunk.peak_sample = np.argmax(self.data_chunk.waveform, axis=0)

        #   Create the data and build the information for the generic_time_waveform
        super().__init__(self.data_chunk.waveform, self.format_chunk.sample_rate, self.start_time,
                         remove_dc_offset=False)

    def _build_waveform(self, fs=None, samples=None, time=None):
        """
        This function permits the construction of the waveform from the arguments passed to the constructor rather
        than reading the file.

        :param fs: int - the number of samples per second.  This facilitates calling the based class with the required
            data
        :param samples: ndarray - the actual samples to define the waveform
        :param time: float or datetime - the time of the first sample
        """
        if (fs is None) and (samples is None) and (time is None):
            #   Build a blank Waveform
            self.list_chunk = ListChunk()
            self.format_chunk = FormatChunk()
            self.samples = None
            self.start_time = None
            self.sample_rate = None
            self.peak_chunk = None
            self.normalized = False
        elif (fs is not None) and (samples is not None):
            #   Construct a waveform from the information passed to the function
            #
            #   If the time is not specified, the set it to floating point zero
            if time is None:
                t0 = 0
            else:
                t0 = time

            #   Call the parent constructor
            super().__init__(samples, sample_rate=fs, start_time=t0)

            #   Now build the format chunk from this information
            self.format_chunk = FormatChunk()

            #   Specify the channel count within the Format Chunk
            if len(self.samples.shape) == 1:
                self.format_chunk.channel_count = 1
            else:
                self.format_chunk.channel_count = self.samples.shape[1]

            #   Create an empty peak chunk and a blank list chunk
            self.peak_chunk = None
            self.list_chunk = ListChunk()

            #   Since the contents of the WaveFile use the ListChunk's start_time, let's overwrite the representation
            #   of the start time now to ensure that it is stored in the list chunk
            self.start_time = t0

        self.normalized = False

    def __init__(
            self, path=None, s0: int = None, s1: int = None, fs: int = None, samples=None, time=None,
            get_peak: bool = True
    ):
        """
        This constructor reads the chunks from the wave file and then processes those that are canonical.

        :param path: str - the full path to the file that we want to read
        :param s0: int - the starting sample for the reading of the audio file
        :param s1: int - the ending sample for the reading of the audio file
        :param fs: int - the number of samples per second.  This facilitates calling the based class with the required
            data
        :param samples: ndarray - the actual samples to define the waveform
        :param time: float or datetime - the time of the first sample
        :param get_peak: bool - whether the constructor should get the peak value (and create the peak chunk).
        Getting this value doubles memory usage.
        """
        warnings.warn(f"{self.__class__.__name__} is obsolete and will be removed in version 1.0.2")

        # warnings.warn('Test for Insert Start Time using wfm.start_time=...is failing.')
        # TODO - Correct the wfm.start_time setting feature.

        if path is None:
            self._build_waveform(fs, samples, time)
        elif path is not None:
            if not isinstance(path, str):
                raise ValueError("You must provide the path to the file")

            if not os.path.exists(path):
                raise ValueError("The supplied path ({})does not lead to a valid file".format(path))

            self._read_file(path, s0, s1, get_peak)

    @property
    def full_path(self):
        """
        The fully realized path to the file that was read
        """

        return self.filename

    @property
    def bytes_per_sample(self):
        """
        the number of bytes per sample, which is the bits per sample read from the format chunk divided by 8
        """

        return self.format_chunk.bits_per_sample / 8

    @property
    def peak_value(self):
        return self.peak_chunk.peak_value

    @property
    def channel_count(self):
        return self.format_chunk.num_channels

    @property
    def audio_format(self):
        return self.format_chunk.audio_format

    @property
    def bits_per_sample(self):
        return self.format_chunk.bits_per_sample

    @property
    def block_align(self):
        return self.format_chunk.block_align

    @property
    def meta_data(self):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        return self.list_chunk.meta_data

    @meta_data.setter
    def meta_data(self, values):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()

        self.list_chunk.meta_data = values

    @property
    def header(self):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        return self.list_chunk.header

    @property
    def archival_location(self):
        if self.list_chunk is not None:
            return self.list_chunk.archival_location
        else:
            return None

    @archival_location.setter
    def archival_location(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()

        self.list_chunk.meta_data["archival_location"] = value

    @property
    def artist(self):
        if self.list_chunk is not None:
            return self.list_chunk.artist
        else:
            return None

    @artist.setter
    def artist(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["artist"] = value

    @property
    def commissioned_organization(self):
        if self.list_chunk is not None:
            return self.list_chunk.commissioned_organization
        else:
            return None

    @commissioned_organization.setter
    def commissioned_organization(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["commissioned_organization"] = value

    @property
    def general_comments(self):
        if self.list_chunk is not None:
            return self.list_chunk.general_comments
        else:
            return None

    @general_comments.setter
    def general_comments(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["general_comments"] = value

    @property
    def copyright(self):
        if self.list_chunk is not None:
            return self.list_chunk.copyright
        else:
            return None

    @copyright.setter
    def copyright(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["copyright"] = value

    @property
    def creation_date(self):
        if self.list_chunk is not None:
            return self.list_chunk.creation_date
        else:
            return None

    @creation_date.setter
    def creation_date(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["creation_date"] = value

        if isinstance(value, str):
            raise ValueError("Expected the creation date to be a datetime")
        elif isinstance(value, datetime):
            self.list_chunk.time0 = value

    @property
    def cropping_information(self):
        if self.list_chunk is not None:
            return self.list_chunk.cropping_information
        else:
            return None

    @cropping_information.setter
    def cropping_information(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["cropping_information"] = value

    @property
    def originating_object_dimensions(self):
        if self.list_chunk is not None:
            return self.list_chunk.originating_object_dimensions
        else:
            return None

    @originating_object_dimensions.setter
    def originating_object_dimensions(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["originating_object_dimensions"] = value

    @property
    def dots_per_inch(self):
        if self.list_chunk is not None:
            return self.list_chunk.dots_per_inch
        else:
            return None

    @dots_per_inch.setter
    def dots_per_inch(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["dots_per_inch"] = value

    @property
    def engineer_name(self):
        if self.list_chunk is not None:
            return self.list_chunk.engineer_name
        else:
            return None

    @engineer_name.setter
    def engineer_name(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["engineer_name"] = value

    @property
    def subject_genre(self):
        if self.list_chunk is not None:
            return self.list_chunk.subject_genre
        else:
            return None

    @subject_genre.setter
    def subject_genre(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["subject_genre"] = value

    @property
    def key_words(self):
        if self.list_chunk is not None:
            return self.list_chunk.key_words
        else:
            return None

    @key_words.setter
    def key_words(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["key_words"] = value

    @property
    def lightness_settings(self):
        if self.list_chunk is not None:
            return self.list_chunk.lightness_settings
        else:
            return None

    @lightness_settings.setter
    def lightness_settings(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["lightness_settings"] = value

    @property
    def originating_object_medium(self):
        if self.list_chunk is not None:
            return self.list_chunk.originating_object_medium
        else:
            return None

    @originating_object_medium.setter
    def originating_object_medium(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["originating_object_medium"] = value

    @property
    def title(self):
        if self.list_chunk is not None:
            return self.list_chunk.title
        else:
            return None

    @title.setter
    def title(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["title"] = value

    @property
    def color_palette_count(self):
        if self.list_chunk is not None:
            return self.list_chunk.color_palette_count
        else:
            return None

    @color_palette_count.setter
    def color_palette_count(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["color_palette_count"] = value

    @property
    def subject_name(self):
        if self.list_chunk is not None:
            return self.list_chunk.subject_name
        else:
            return None

    @subject_name.setter
    def subject_name(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["subject_name"] = value

    @property
    def description(self):
        if self.list_chunk is not None:
            return self.list_chunk.description
        else:
            return None

    @description.setter
    def description(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["description"] = value

    @property
    def creation_software(self):
        if self.list_chunk is not None:
            return self.list_chunk.creation_software
        else:
            return None

    @creation_software.setter
    def creation_software(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["creation_software"] = value

    @property
    def data_source(self):
        if self.list_chunk is not None:
            return self.list_chunk.data_source
        else:
            return None

    @data_source.setter
    def data_source(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["data_source"] = value

    @property
    def original_form(self):
        if self.list_chunk is not None:
            return self.list_chunk.original_form
        else:
            return None

    @original_form.setter
    def original_form(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["original_form"] = value

    @property
    def digitizing_engineer(self):
        if self.list_chunk is not None:
            return self.list_chunk.digitizing_engineer
        else:
            return None

    @digitizing_engineer.setter
    def digitizing_engineer(self, value):
        if self.list_chunk is None:
            self.list_chunk = ListChunk()
        self.list_chunk.meta_data["digitizing_engineer"] = value

    @property
    def track_number(self):
        return self.list_chunk.track_number

    @track_number.setter
    def track_number(self, value):
        self.list_chunk.meta_data['track_no'] = value

    @property
    def start_time(self):
        if 'creation_date' in self.list_chunk.meta_data.keys() and self.list_chunk.meta_data['creation_date'] is not \
                None:
            if isinstance(self.list_chunk.meta_data['creation_date'], str):
                if self.list_chunk.meta_data['creation_date'].isdigit():
                    return float(self.list_chunk.meta_data['creation_date'])
                else:
                    try:
                        return datetime.fromisoformat(self.list_chunk.meta_data['creation_date'])
                    except:
                        try:
                            return datetime.strptime(
                                self.list_chunk.meta_data['creation_date'],
                                "%Y-%m-%d %H:%M:%S.%f"
                                )
                        except ValueError:
                            return datetime.strptime(
                                self.list_chunk.meta_data['creation_date'],
                                "%Y-%m-%d %H:%M:%S"
                                )
            else:
                return self.list_chunk.meta_data['creation_date']
        else:
            return 0

    @start_time.setter
    def start_time(self, value):
        self.list_chunk.meta_data['creation_date'] = value

    @property
    def channels(self) -> np.ndarray:
        """
        This property creates a set of Waveform objects that represent the individual channels within the audio file.
        """

        array = np.empty((self.channel_count,), dtype=Waveform)
        for i in range(self.channel_count):
            array[i] = Waveform(
                pressures=self.samples[:, i],
                sample_rate=self.sample_rate,
                start_time=self.start_time,
                header=self.header
                )

        return array

    def save(self, path):
        """
        This function will save the data to a canonical wav formatted file with appropriate scaling to recover the
        actual Pascal values.

        :param path: str - the output path for the scaled canonical wav format
        """

        #   Ensure that the output path is fully formed before attempting to open the output file

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        #   Now we open the file

        with open(path, 'wb') as file:
            #   Write the canonical WAVE header with a zero file size that we will return later to modify

            file.write("RIFF".encode('utf-8'))
            file.write(struct.pack("<i", 0))
            file.write("WAVE".encode('utf-8'))

            #   Write the format chunk

            FormatChunk.write_chunk(file, self.sample_rate, 32, self.format_chunk.channel_count)

            #   To scale the audio data correctly we either need to have a standard limit, or define the maximum in some
            #   other way.  The PEAK chunk provides a new way to represent the audio information, so let's write that
            #   now.

            if self.peak_chunk is None:
                self.peak_chunk = PeakChunk()
                self.peak_chunk.peak_amplitude = np.max(self.samples, axis=0)
                self.peak_chunk.peak_sample = np.argmax(self.samples, axis=0)

            self.peak_chunk.write_chunk(file)

            #   Write the data chunk header

            file.write("data".encode('utf-8'))
            file.write(struct.pack("<i", 4 * len(self.samples) * self.channel_count))

            #   Now we will loop through the data elements and write the information, scaled to 1.0f full scale based
            #   on the data within the PEAK chunk

            if self.normalized:
                if self.format_chunk.channel_count > 1:
                    for i in range(self.samples.shape[1]):
                        self.samples[:, i] /= np.max(self.samples[:, i])
                else:
                    self.samples[:] /= np.max(self.samples[:])

            samples_to_write = np.reshape(self.samples, (np.prod(self.samples.shape),))
            file.write(samples_to_write.astype("<f").tobytes())

            #   Write the LIST chunk

            # if self.list_chunk is not None: # There will always be a list chunk
            if self.creation_date is None:
                self.creation_date = datetime.now()
            if self.start_time is not None:
                if not isinstance(self.start_time, datetime):
                    self.list_chunk.time0 = datetime.now()
                else:
                    self.list_chunk.time0 = self.start_time

            self.list_chunk.write_chunk(file)

            #   Get the current number of bytes within the file

            file_size = file.tell()

            #   Search for the file size - 8 within the header and update the information

            file.seek(4, 0)
            file.write(struct.pack("<i", file_size - 8))

    def resample_16kHz_16bit(self, channel_index: int = 0):
        """
        In preparation for the transcription of the waveform with the Vosk wrapping of the Kaldi models we need to
        transform this signal to a 16 Khz, 16-bit signal.  This function performs the resmapling and scaling and returns
        the byte-array that is directly provided to the Vosk interface.

        :param channel_index: int - the index of the channel that will be read into the interface
        """

        #   Determine the resampling levels

        ratio = int(np.floor((16000 * self.samples.shape[0] / self.sample_rate)))

        samples = scipy.signal.resample(self.samples[:, channel_index], ratio)

        #   Now convert the data from current floating point representation to the short representation

        samples *= (2 ** 16) - 1
        int_samples = np.zeros(samples.shape, dtype='int')

        for i in range(len(int_samples)):
            int_samples[i] = int(np.round(samples[i]))

        short_data = int_samples.astype(np.int16)

        #   Now convert this short data to a binary array

        byte_data = bytearray()
        for i in range(len(short_data)):
            byte_data += struct.pack('h', short_data[i])

        return byte_data

    def is_calibration(self, channel_index: int = 0):
        """
        This function examines the samples and determines whether the single contains a single pure tone.  If it does
        the function returns the approximate frequency of the tone.  This will examine every channel and determine
        whether each channel is a calibration tone

        :returns: bool - flag determining whether the signal was pure tone
                  float - the approximate frequency of the pure tone
        """

        #   Loop through the channels
        if self.channel_count > 1:
            calibration = np.zeros((self.channel_count,))
            frequency = np.zeros((self.channel_count,))

            for ch_idx in range(self.channel_count):
                wfm = Waveform(self.samples[:, ch_idx], self.sample_rate, self.start_time).apply_lowpass(2000)
                calibration[ch_idx], frequency[ch_idx] = wfm.is_calibration()

            return calibration, frequency
        else:
            wfm = Waveform(self.samples, self.sample_rate, self.start_time).apply_lowpass(2000)
            return wfm.is_calibration()
