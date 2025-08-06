import io
import numpy as np
import enum, datetime, mmap
from typing import Callable
from pypamguard.utils.bitmap import Bitmap
from pypamguard.core.exceptions import WarningException, ErrorException, CriticalException
from pypamguard.logger import logger
from pypamguard.core.serializable import Serializable
from contextlib import contextmanager
import traceback

class DTYPES(enum.Enum):
    INT8 = np.dtype(np.int8)
    UINT8 = np.dtype(np.uint8)
    INT16 = np.dtype(np.int16)
    UINT16 = np.dtype(np.uint16)
    INT32 = np.dtype(np.int32)
    UINT32 = np.dtype(np.uint32)
    INT64 = np.dtype(np.int64)
    UINT64 = np.dtype(np.uint64)
    FLOAT32 = np.dtype(np.float32)
    FLOAT64 = np.dtype(np.float64)

class Shape:
    def __init__(self, shape, length: int):
        self.shape = shape
        self.length = length
        
        if type(self.shape) == self.__class__:
            self.size = self.length * self.shape.size
        elif type(self.shape) == DTYPES:
            self.size = self.length * self.shape.value.itemsize
            self.shape = self.shape.value
        else:
            raise ValueError(f"shape must be of type Shape or np.dtype (got {type(self.shape)}).")

    def __str__(self):
        if type(self.shape) == self.__class__:
            return f"{self.length} * ({self.shape})"
        else:
            return f"{self.length} * {self.shape}"





class Report(Serializable):
    warnings = []
    errors: list[ErrorException] = []
    errors_tb: list = []

    def __init__(self):
        self.current_context = ""
        self.warnings = []
    
    def set_context(self, context):
        self.current_context = context

    def add_warning(self, warning: WarningException):
        warning.add_context(self.current_context)
        self.warnings.append(warning)
        logger.warning(warning)
    
    def add_error(self, error: Exception):
        error.add_context(self.current_context)
        self.errors.append(error)
        logger.error(error)
        tb = traceback.format_stack()
        self.errors_tb.append(tb)
    
    
    def __str__(self):
        string = "### REPORT SUMMARY ###\n"
        if len(self.warnings) != 0:
            string += f" - {len(self.warnings)} warnings (access warnings via .warnings list).\n"
        if len(self.errors) != 0:
            string += f" - {len(self.errors)} errors (access errors via .errors list and tracebacks via .errors_tb parallel list).\n"
        string += "### END OF REPORT ###"
        return string


class BinaryReader:

    def __init__(self, fp: mmap.mmap, report: Report, endianess='>'):
        self.fp = fp
        self._endianess = endianess
        self.report = report
    
    
    def set_endianess(self, endianess):
        if not endianess in ('>', '<'): raise ValueError("Endianess must be one of '>' (big) or '<' (small)")
        self._endianess = endianess

    def __collate(self, data, dtypes, shape):
        for i, dtype_i in enumerate(dtypes):            
            d = data[f'f{i}'][0] if (len(shape) == 1 and shape[0] == 1) else data[f'f{i}'].reshape(shape)
            yield dtype_i[1](d) if dtype_i[1] is not None else d

    def __read(self, length: int) -> bytes:
        data = self.fp.read(length)
        return data

    def tell(self):
        return self.fp.tell()

    def seek(self, offset, whence: int = io.SEEK_SET):
        return self.fp.seek(offset, whence)

    def set_checkpoint(self, offset: int):
        self.next_checkpoint = self.tell() + offset

    def goto_checkpoint(self):
        self.seek(self.next_checkpoint)
    
    def at_checkpoint(self):
        if self.tell() == self.next_checkpoint: return True
        else: return False

    def bin_read(self, dtype: list[tuple[DTYPES, Callable[[np.ndarray], np.ndarray]]], shape: tuple = (1,)) -> int | float | np.ndarray | tuple[np.ndarray]:
        """
        Read data from the file. This function is polymorphic in the sense that it
        can be used for any of the following purposes:

        1. Read in a single value of a given datatype (for example `read_numeric(DTYPES.INT32)`).
        2. Read in an array of values of a given datatype (for example `read_numeric(DTYPES.INT32, (5,))`).
        3. Read in an n-dimensional array of values of a given datatype (for example `read_numeric(DTYPES.INT32, (5, 5))`).
        4. Read in an interleaved array of values of a given datatype (for example `read_numeric([DTYPES.INT32, DTYPES.INT32], (5,))`).

        Read in an array of 5 integers (32-bit).
        Return a single `np.ndarray` of type `np.int32`.
        ```python
        bin_read(DTYPES.INT32, (5,))
        ```

        Read in two 5-length arrays (interleaved int32, int32).
        Return a tuple of two `np.ndarray`s of type `np.int16`
        and `np.int64`.
        ```python
        bin_read([DTYPES.INT16, DTYPES.INT64], (5,))
        ```

        Read in a single float (32-bit) and divide by 100.
        Return a single `np.float32`.
        ```python
        bin_read((DTYPES.FLOAT32, lambda x: x / 100))
        ```

        Read in two 5-length arrays (interleaved float32, int8).
        Divide the int8 array by 100.
        Return a tuple of two `np.ndarray`s of type `np.float32` and `np.float32`.
        (NOTE: the int8 array is returned as a float32 array due to the division by 100.)
        ```python
        bin_read([(DTYPES.FLOAT32), (DTYPES.INT8, lambda x: x/100)], (5,))
        ```

        Read in a single 5x2 array of floats (32-bit).
        Return a 2d `np.ndarray` of type `np.float32`.
        ```python
        bin_read(DTYPES.FLOAT32, (5, 2))
        ```
        """
        if type(shape) != tuple: shape = (shape,)
        dtypes = [(dtype_i, None) if isinstance(dtype_i, DTYPES) else dtype_i for dtype_i in ([dtype] if not isinstance(dtype, list) else dtype)]
        data = np.frombuffer(self.__read(sum(dtype_i[0].value.itemsize for dtype_i in dtypes) * np.prod(shape)   ), dtype=[(f'f{i}', dtype_i[0].value.newbyteorder(self._endianess)) for i, dtype_i in enumerate(dtypes)])
        ret_val = tuple(self.__collate(data, dtypes, shape))
        return ret_val[0] if len(ret_val) == 1 else ret_val

    @classmethod
    def millis_to_timestamp(self, millis):
        # datetime.datetime.fromtimestamp() requires millis to be in seconds
        return datetime.datetime.fromtimestamp(millis / 1000, tz=datetime.UTC)

    def timestamp_read(self) -> tuple[int, datetime.datetime]:
        with br_report(self):
            millis = self.bin_read(DTYPES.INT64)
            return millis, self.millis_to_timestamp(millis)
        return millis, None # in case timestamp conversion does not work

    def nstring_read(self, length: int) -> str:
        with br_report(self):
            return self.__read(length).decode("utf-8")

    def string_read(self) -> str:
        with br_report(self):
            return self.nstring_read(self.bin_read(DTYPES.INT16))
    
    def bitmap_read(self, dtype: DTYPES, labels: list[str] = None) -> Bitmap:
        with br_report(self):
            return Bitmap(dtype.value.itemsize, labels, int(self.bin_read(dtype)))
    
@contextmanager
def br_report(br: BinaryReader):
    try:
        yield
    except WarningException as e:
        br.report.add_warning(e)
    except ErrorException as e:
        br.report.add_error(e)
    except CriticalException as e:
        raise e
    except Exception as e:
        br.report.add_error(ErrorException(br=br, message=str(e)))
