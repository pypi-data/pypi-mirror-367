"""
Core MS3Record implementation for pymseed

"""
import json
from typing import Optional, Any, Union, Callable
from .clib import clibmseed, ffi, cdata_to_string
from .util import nstime2timestr, timestr2nstime, encoding_string
from .exceptions import MiniSEEDError
from .definitions import TimeFormat, SubSecond


class MS3Record:
    """A miniSEED record wrapper around a MS3Record structure"""

    def __init__(
        self,
        reclen: Optional[int] = None,
        encoding: Optional[int] = None,
        samplecnt: Optional[int] = None,
        recordptr: Any = None,
    ) -> None:
        """
        Initialize MS3Record wrapper.

        Args:
            reclen: Record length in bytes (None for default)
            encoding: Data encoding format (None for default)
            samplecnt: Sample count (None for default)
            recordptr: Existing MS3Record pointer (for wrapping parsed records)
        """
        if recordptr is not None:
            # Wrap an existing record structure
            self._msr = recordptr
            self._msr_allocated = False
        else:
            # Allocate a new record
            self._msr = clibmseed.msr3_init(ffi.NULL)
            self._msr_allocated = True

            # Set values if provided
            if reclen is not None:
                self._msr.reclen = reclen
            if encoding is not None:
                self._msr.encoding = encoding
            if samplecnt is not None:
                self._msr.samplecnt = samplecnt

    def __del__(self) -> None:
        if self._msr and self._msr_allocated:
            msr_ptr = ffi.new("MS3Record **")
            msr_ptr[0] = self._msr
            clibmseed.msr3_free(msr_ptr)

    def __repr__(self) -> str:
        datasamples_str = "[]"
        if self._msr.numsamples > 0:
            samples = self.datasamples
            if samples:
                datasamples_str = (
                    str(samples[:5]) + " ..." if len(samples) > 5 else str(samples)
                )

        return (
            f"MS3Record(sourceid: {self.sourceid}\n"
            f"        pubversion: {self._msr.pubversion}\n"
            f"            reclen: {self._msr.reclen}\n"
            f"     formatversion: {self._msr.formatversion}\n"
            f"         starttime: {self._msr.starttime} => {self.starttime_str()}\n"
            f"         samplecnt: {self._msr.samplecnt}\n"
            f"          samprate: {self._msr.samprate}\n"
            f"             flags: {self._msr.flags} => {self.flags_dict()}\n"
            f"               CRC: {self._msr.crc} => {hex(self._msr.crc)}\n"
            f"          encoding: {self._msr.encoding} => {self.encoding_str()}\n"
            f"       extralength: {self._msr.extralength}\n"
            f"        datalength: {self._msr.datalength}\n"
            f"             extra: {self.extra}\n"
            f"        numsamples: {self._msr.numsamples}\n"
            f"       datasamples: {datasamples_str}\n"
            f"          datasize: {self._msr.datasize}\n"
            f"        sampletype: {self.sampletype} => {self.sampletype_str()}\n"
            f"    record pointer: {self._msr})"
        )

    def __lt__(self, obj: "MS3Record") -> bool:
        return (self.sourceid, self.starttime) < (obj.sourceid, obj.starttime)

    def __gt__(self, obj: "MS3Record") -> bool:
        return (self.sourceid, self.starttime) > (obj.sourceid, obj.starttime)

    def __le__(self, obj: "MS3Record") -> bool:
        return (self.sourceid, self.starttime) <= (obj.sourceid, obj.starttime)

    def __ge__(self, obj: "MS3Record") -> bool:
        return (self.sourceid, self.starttime) >= (obj.sourceid, obj.starttime)

    def __str__(self) -> str:
        return (
            f"{self.sourceid}, "
            f"{self.pubversion}, "
            f"{self.reclen}, "
            f"{self.samplecnt} samples, "
            f"{self.samprate} Hz, "
            f"{self.starttime_str()}"
        )

    @property
    def record(self) -> bytes:
        """Return raw, parsed miniSEED record as bytes (copy)"""
        if self._msr.record == ffi.NULL:
            raise ValueError("No raw record available")

        return bytes(ffi.buffer(self._msr.record, self._msr.reclen)[:])

    @property
    def record_mv(self) -> memoryview:
        """Return raw, parsed miniSEED record as memoryview (no copy)"""
        if self._msr.record == ffi.NULL:
            raise ValueError("No raw record available")

        return ffi.buffer(self._msr.record, self._msr.reclen)

    @property
    def reclen(self) -> int:
        """Return record length in bytes"""
        return self._msr.reclen

    @reclen.setter
    def reclen(self, value: int) -> None:
        """Set maximum record length in bytes"""
        self._msr.reclen = value

    @property
    def swapflag(self) -> int:
        """Return swap flags as raw integer"""
        return self._msr.swapflag

    def swapflag_dict(self) -> dict[str, bool]:
        """Return swap flags as dictionary"""
        swapflag = {}
        swapflag["header_swapped"] = bool(self._msr.swapflag & clibmseed.MSSWAP_HEADER)
        swapflag["payload_swapped"] = bool(self._msr.swapflag & clibmseed.MSSWAP_PAYLOAD)
        return swapflag

    @property
    def sourceid(self) -> Optional[str]:
        """Return source identifier as string"""
        return cdata_to_string(self._msr.sid)

    @sourceid.setter
    def sourceid(self, value: str) -> None:
        """Set source identifier

        The source identifier is limited to 63 characters.
        Typically this is an FDSN Source Identifier:
        https://docs.fdsn.org/projects/source-identifiers
        """
        if len(value) >= clibmseed.LM_SIDLEN:
            raise ValueError(f"Source ID too long (max {clibmseed.LM_SIDLEN-1} characters)")

        self._msr.sid = ffi.new(f"char[{clibmseed.LM_SIDLEN}]", value.encode("utf-8"))

    @property
    def formatversion(self) -> int:
        """Return format version"""
        return self._msr.formatversion

    @formatversion.setter
    def formatversion(self, value: int) -> None:
        """Set format version"""
        if value not in [2, 3]:
            raise ValueError(f"Invalid miniSEED format version: {value}")
        self._msr.formatversion = value

    @property
    def flags(self) -> int:
        """Return record flags as raw 8-bit integer"""
        return self._msr.flags

    @flags.setter
    def flags(self, value: int) -> None:
        """Set record flags as an 8-bit unsigned integer"""
        self._msr.flags = value

    def flags_dict(self) -> dict[str, bool]:
        """Return record flags as a dictionary"""
        flags = {}
        if self._msr.flags & 0x01:
            flags["calibration_signals_present"] = True
        if self._msr.flags & 0x02:
            flags["time_tag_is_questionable"] = True
        if self._msr.flags & 0x04:
            flags["clock_locked"] = True
        return flags

    @property
    def starttime(self) -> int:
        """Return start time as nanoseconds since Unix/POSIX epoch"""
        return self._msr.starttime

    @starttime.setter
    def starttime(self, value: int) -> None:
        """Set start time as nanoseconds since Unix/POSIX epoch"""
        self._msr.starttime = value

    @property
    def starttime_seconds(self) -> float:
        """Return start time as seconds since Unix/POSIX epoch"""
        return self._msr.starttime / clibmseed.NSTMODULUS

    @starttime_seconds.setter
    def starttime_seconds(self, value: float) -> None:
        """Set start time as seconds since Unix/POSIX epoch

        The value is limited to microsecond resolution and will be rounded
        to to ensure a consistent conversion to the internal representation.
        This is done to avoid floating point precision issues.
        """
        # Scale to microseconds, round to nearest integer, then scale to nanoseconds
        self._msr.starttime = int(value * 1000000 + 0.5) * 1000

    def starttime_str(
        self,
        timeformat: TimeFormat = TimeFormat.ISOMONTHDAY_Z,
        subsecond: SubSecond = SubSecond.NANO_MICRO_NONE,
    ) -> Optional[str]:
        """Return start time as formatted string"""
        return nstime2timestr(self._msr.starttime, timeformat, subsecond)

    def set_starttime_str(self, value: str) -> None:
        """Set start time from formatted string"""
        self._msr.starttime = timestr2nstime(value)

    @property
    def samprate(self) -> float:
        """Return nominal sample rate"""
        return self._msr.samprate

    @samprate.setter
    def samprate(self, value: float) -> None:
        """Set nominal sample rate

        For data sampled regularly, this value should be positive and represent
        samples/second (Hz).

        For data NOT sampled regularly, this value should be negative and
        represent the sample interval in seconds (-1/interval).
        """
        self._msr.samprate = value

    @property
    def samprate_raw(self) -> float:
        """Return sample rate for regular data or sample interval for irregular

        This directly returns the value from the structure, negative indicates
        the data are NOT regularly sampled and the value is an interval period.
        """
        return self._msr.samprate

    @property
    def encoding(self) -> int:
        """Return data encoding format code"""
        return self._msr.encoding

    @encoding.setter
    def encoding(self, value: int) -> None:
        """Set data encoding format code

        See DataEncoding enum for valid values
        """
        self._msr.encoding = value

    @property
    def pubversion(self) -> int:
        """Return publication version"""
        return self._msr.pubversion

    @pubversion.setter
    def pubversion(self, value: int) -> None:
        """Set publication version"""
        self._msr.pubversion = value

    @property
    def samplecnt(self) -> int:
        """Return number of samples specified in fixed header"""
        return self._msr.samplecnt

    @property
    def crc(self) -> int:
        """Return CRC of entire record"""
        return self._msr.crc

    @property
    def extralength(self) -> int:
        """Return length of extra headers in bytes"""
        return self._msr.extralength

    @property
    def datalength(self) -> int:
        """Return length of data payload in bytes"""
        return self._msr.datalength

    @property
    def extra(self) -> str:
        """Return extra headers as JSON string"""
        if self._msr.extra == ffi.NULL:
            return ""
        return cdata_to_string(self._msr.extra)

    @extra.setter
    def extra(self, value: str) -> None:
        """Set extra headers as JSON string, will be minified to reduce size"""
        if value:
            # Minify the JSON string to ensure valid JSON and minimize size
            minified = json.dumps(json.loads(value), separators=(",", ":"))

            c_value = ffi.new("char[]", minified.encode("utf-8"))
            status = clibmseed.mseh_replace(self._msr, c_value)
            if status < 0:
                raise ValueError(f"Error setting extra headers: {status}")

    @property
    def datasamples(self) -> memoryview:
        """Return data samples as a memoryview (no copy)

        A view of the data samples in an internal buffer owned by this MS3Record
        instance is returned.  If the data are needed beyond the lifetime of this
        instance, a copy must be made.

        The returned view can be used directly with slicing and indexing
        from `0` to `MS3Record.numsamples - 1`.

        The view can efficiently be copied to a _python list_ using:

            data_samples = MS3Record.datasamples[:]
        """
        if self._msr.numsamples <= 0:
            return memoryview(b'')  # Empty memoryview

        sampletype = self.sampletype

        if sampletype == "i":
            ptr = ffi.cast("int32_t *", self._msr.datasamples)
            buffer = ffi.buffer(ptr, self._msr.numsamples * ffi.sizeof("int32_t"))
            return memoryview(buffer).cast('i')
        elif sampletype == "f":
            ptr = ffi.cast("float *", self._msr.datasamples)
            buffer = ffi.buffer(ptr, self._msr.numsamples * ffi.sizeof("float"))
            return memoryview(buffer).cast('f')
        elif sampletype == "d":
            ptr = ffi.cast("double *", self._msr.datasamples)
            buffer = ffi.buffer(ptr, self._msr.numsamples * ffi.sizeof("double"))
            return memoryview(buffer).cast('d')
        elif sampletype == "t":
            ptr = ffi.cast("char *", self._msr.datasamples)
            buffer = ffi.buffer(ptr, self._msr.numsamples)
            return memoryview(buffer).cast('B')
        else:
            raise ValueError(f"Unknown sample type: {sampletype}")

    @property
    def np_datasamples(self) -> Any:
        """Return data samples as a numpy array view (no copy)

        A view of the data samples in an internal buffer owned by this MS3Record
        instance is returned. If the data are needed beyond the lifetime of this
        instance, a copy must be made.
        """
        try:
            import numpy as np
        except ImportError:
            raise ImportError(
                "numpy is not installed. Install numpy or this package with [numpy] optional dependency"
            ) from None

        if self._msr.numsamples <= 0:
            return np.array([])  # Empty array

        sampletype = self.sampletype

        # Translate libmseed sample type to numpy type
        nptype = {
            "i": np.int32,
            "f": np.float32,
            "d": np.float64,
            "t": "S1",  # 1-byte strings for text data
        }

        if sampletype not in nptype:
            raise ValueError(f"Unknown sample type: {sampletype}")

        # Create numpy array view from CFFI buffer
        return np.frombuffer(self.datasamples, dtype=nptype[sampletype])

    @property
    def datasize(self) -> int:
        """Return size of decoded data payload in bytes"""
        return self._msr.datasize

    @property
    def numsamples(self) -> int:
        """Return number of decoded samples at MS3Record.datasamples"""
        return self._msr.numsamples

    @property
    def sampletype(self) -> Optional[str]:
        """Return sample type code if available, otherwise None"""
        if self._msr.sampletype:
            return self._msr.sampletype.decode("ascii")
        else:
            return None

    def sampletype_str(self) -> Optional[str]:
        """Return sample type as descriptive string"""
        sampletype = self.sampletype
        if sampletype == "i":
            return "int32"
        elif sampletype == "f":
            return "float32"
        elif sampletype == "d":
            return "float64"
        elif sampletype == "t":
            return "text"
        else:
            return None

    @property
    def endtime(self) -> int:
        """Return end time as nanoseconds since Unix/POSIX epoch"""
        return clibmseed.msr3_endtime(self._msr)

    @property
    def endtime_seconds(self) -> float:
        """Return end time as seconds since Unix/POSIX epoch"""
        return clibmseed.msr3_endtime(self._msr) / clibmseed.NSTMODULUS

    def endtime_str(
        self,
        timeformat: TimeFormat = TimeFormat.ISOMONTHDAY_Z,
        subsecond: SubSecond = SubSecond.NANO_MICRO_NONE,
    ) -> Optional[str]:
        """Return end time as formatted string"""
        return nstime2timestr(self.endtime, timeformat, subsecond)

    def encoding_str(self) -> Optional[str]:
        """Return encoding format as descriptive string"""
        return encoding_string(self._msr.encoding)

    def print(self, details: int = 0) -> None:
        """Print details of the record to stdout, with varying levels of `details`"""
        clibmseed.msr3_print(self._msr, details)

    def _record_handler_wrapper(self, record: Any, record_length: int, handlerdata: Any) -> None:
        """Callback function for msr3_pack()"""
        # Convert CFFI buffer to bytes for the handler
        record_bytes = ffi.buffer(record, record_length)[:]
        self._record_handler(record_bytes, self._record_handler_data)

    def pack(
        self,
        handler: Callable[[bytes, Any], None],
        handler_data: Any = None,
        data_samples: Optional[Union[list[int], list[float], list[str]]] = None,
        sample_type: Optional[str] = None,
        verbose: int = 0,
    ) -> tuple[int, int]:
        """Pack `datasamples` into miniSEED record(s) and call `handler()`

        The `handler(record, handlerdata)` function must accept two arguments:
                record:         A buffer containing a miniSEED record
                handlerdata:    The `handlerdata` value

        The handler function must use or copy the record buffer as the memory may be
        reused on subsequent iterations.

        Returns a tuple of (packed_samples, packed_records)
        """
        # Set handler function as CFFI callback function
        self._record_handler = handler
        self._record_handler_data = handler_data

        # Create callback function type and instance
        RECORD_HANDLER = ffi.callback(
            "void(char *, int, void *)", self._record_handler_wrapper
        )

        packed_samples = ffi.new("int64_t *")
        flags = clibmseed.MSF_FLUSHDATA  # Always flush data when packing

        if data_samples is not None and sample_type is not None:
            msr_datasamples = self._msr.datasamples
            msr_sampletype = self._msr.sampletype
            msr_numsamples = self._msr.numsamples
            msr_samplecnt = self._msr.samplecnt

            # Set up data samples in the MS3Record before packing
            self._msr.samplecnt = len(data_samples)
            self._msr.numsamples = len(data_samples)

            # Set sample type (use first character only)
            self._msr.sampletype = sample_type[0].encode('ascii')

            # Allocate and copy data samples based on type
            if sample_type == "i":
                try:
                    mv = memoryview(data_samples)
                    if mv.format == 'i' and mv.itemsize == 4:
                        # Compatible format - safe to zero-copy
                        sample_array = ffi.cast("int32_t *", ffi.from_buffer(data_samples))
                    else:
                        raise ValueError("Incompatible buffer format")
                except (TypeError, ValueError):
                    # Not compatible or not a buffer - need conversion
                    sample_array = ffi.new("int32_t[]", [int(sample) for sample in data_samples])
                self._msr.datasamples = ffi.cast("void *", sample_array)
                self._msr.datasize = len(data_samples) * 4
            elif sample_type == "f":
                try:
                    mv = memoryview(data_samples)
                    if mv.format == 'f' and mv.itemsize == 4:
                        # Compatible format - safe to zero-copy
                        sample_array = ffi.cast("float *", ffi.from_buffer(data_samples))
                    else:
                        raise ValueError("Incompatible buffer format")
                except (TypeError, ValueError):
                    # Not compatible or not a buffer - need conversion
                    sample_array = ffi.new("float[]", [float(sample) for sample in data_samples])
                self._msr.datasamples = ffi.cast("void *", sample_array)
                self._msr.datasize = len(data_samples) * 4
            elif sample_type == "d":
                try:
                    mv = memoryview(data_samples)
                    if mv.format == 'd' and mv.itemsize == 8:
                        # Compatible format - safe to zero-copy
                        sample_array = ffi.cast("double *", ffi.from_buffer(data_samples))
                    else:
                        raise ValueError("Incompatible buffer format")
                except (TypeError, ValueError):
                    # Not compatible or not a buffer - need conversion
                    sample_array = ffi.new("double[]", [float(sample) for sample in data_samples])
                self._msr.datasamples = ffi.cast("void *", sample_array)
                self._msr.datasize = len(data_samples) * 8
            elif sample_type == "t":
                try:
                    mv = memoryview(data_samples)
                    if mv.format in ('c', 'b', 'B') and mv.itemsize == 1:
                        # Compatible format - safe to zero-copy
                        sample_array = ffi.cast("char *", ffi.from_buffer(data_samples))
                    else:
                        raise ValueError("Incompatible buffer format")
                except (TypeError, ValueError):
                    # Not compatible or not a buffer - need conversion
                    text_data = []
                    for sample in data_samples:
                        if isinstance(sample, str):
                            text_data.append(sample.encode('utf-8')[0])
                        else:
                            text_data.append(int(sample) if isinstance(sample, (int, float)) else str(sample).encode('utf-8')[0])
                    sample_array = ffi.new("char[]", text_data)
                self._msr.datasamples = ffi.cast("void *", sample_array)
                self._msr.datasize = len(data_samples)
            else:
                raise ValueError(f"Unknown sample type: {sample_type}")

        packed_records = clibmseed.msr3_pack(
            self._msr,
            RECORD_HANDLER,
            ffi.NULL,
            packed_samples,
            flags,
            verbose,
        )

        # Restore original values if they were replaced
        if data_samples is not None and sample_type is not None:
            self._msr.datasamples = msr_datasamples
            self._msr.sampletype = msr_sampletype
            self._msr.numsamples = msr_numsamples
            self._msr.samplecnt = msr_samplecnt

        if packed_records < 0:
            raise MiniSEEDError(packed_records, "Error packing miniSEED record(s)")

        return (packed_samples[0], packed_records)
