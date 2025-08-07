from __future__ import annotations

from datetime import datetime # Already imported, but good for clarity
import time
import numpy as np
import polars as pl
# import matplotlib.pyplot as plt # Commented out as it's not used
from typing import Any, Union, List as TypingList, Iterator, Optional, Dict # Added Optional and Dict
from uncertainties import ufloat # ufloat factory
from uncertainties.core import UFloat, Variable # Variable is an alias for UFloat

# NOTE:
#   The real implementation is *replaced at runtime* by the compliance layer.
#   The stub class below is kept so that static type-checkers still see a
#   definition when users import MeasurementResult directly.
class MeasurementResult:  # noqa: D101
    """A class to represent a collection of measurement values.
    
    Attributes:
        values (Union[np.ndarray, pl.DataFrame, np.float64, TypingList[Any], UFloat]): The measurement data.
        units (str): The units of the measurements.
        instrument (str): The name of the instrument used for the measurements.
        measurement_type (str): The type of measurement.
        timestamp (float): Timestamp of when the result was created.
    """
    def __init__(self, values: Union[np.ndarray, pl.DataFrame, np.float64, TypingList[Any], UFloat],
                 instrument: str,
                 units: str,
                 measurement_type: str,
                 timestamp: Optional[float] = None, # Allow optional timestamp override
                 envelope: Optional[Dict[str, Any]] = None, # Add envelope as an explicit argument
                 sampling_rate: Optional[float] = None, # Add sampling_rate for FFT
                 **kwargs: Any) -> None: # Added **kwargs and type hint
        self.values: Union[np.ndarray, pl.DataFrame, np.float64, TypingList[Any], UFloat] = values
        self.units: str = units
        self.instrument: str = instrument
        self.measurement_type: str = measurement_type
        self.timestamp: float = timestamp if timestamp is not None else time.time()
        # Envelope logic: always provide an envelope attribute
        if envelope is not None:
            self.envelope = envelope
        else:
            # Default: minimal valid envelope (empty dict, or customize as needed)
            self.envelope = {}
        
        # Store sampling rate for FFT calculations
        self.sampling_rate = sampling_rate
        
        # Store any additional kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        """String representation of the measurement result.
        
        For backward compatibility with tests, returns a newline-separated list for arrays.
        For other types, uses a more descriptive representation.
        """
        if isinstance(self.values, UFloat):
            return f"{self.values} {self.units}"
        elif isinstance(self.values, np.float64):
            return f"{self.values} {self.units}"
        elif isinstance(self.values, pl.DataFrame):
            return str(self.values)
        elif isinstance(self.values, np.ndarray):
            # For numpy arrays, handle 1D arrays specially for backward compatibility
            if self.values.ndim == 1:
                return '\n'.join([f"{val} {self.units}" for val in self.values])
            # For multi-dimensional arrays, provide a concise representation
            return f"NumPy Array (shape: {self.values.shape}, dtype: {self.values.dtype}) {self.units}"
        elif isinstance(self.values, list):
            # For lists, special handling for backward compatibility
            if all(isinstance(x, (int, float)) for x in self.values):
                return '\n'.join([f"{val} {self.units}" for val in self.values])
            # For lists with mixed types or nested lists, show first few items if long
            if len(self.values) > 5:
                return f"List (first 5 of {len(self.values)}): {self.values[:5]}... {self.units}"
            return f"List: {self.values} {self.units}"
        
        # Fallback for other types
        return f"Values: {str(self.values)[:100]}... Type: {type(self.values)} {self.units}"
    
    def __repr__(self) -> str:
        """Detailed representation of the measurement result.
        
        For backward compatibility with tests, this matches __str__ behavior.
        In typical libraries, repr would show construction details instead.
        """
        return self.__str__()

    # Add this method to convert MeasurementResult to a dict for Polars DataFrame
    def to_dict(self) -> Dict[str, Any]:
        """Convert MeasurementResult to a dict for DataFrame conversion.
        
        This allows MeasurementResult objects to be directly used in Experiment.add_trial.
        """
        if isinstance(self.values, pl.DataFrame):
            # If values is already a DataFrame, convert to dict representation
            result = {}
            for col in self.values.columns:
                result[col] = self.values[col].to_list()
            return result
        elif isinstance(self.values, (np.ndarray, list)):
            # Convert array or list to a dict with a 'values' key
            return {'values': self.values}
        elif isinstance(self.values, (np.float64, UFloat)):
            # Convert scalar value to a dict with a 'value' key
            return {'value': self.values}
        else:
            # Default fallback
            return {'values': self.values}

    # Make the object dict-like so it can be used in Polars DataFrame constructor
    def keys(self):
        """Return the keys for dict-like behavior."""
        return self.to_dict().keys()
    
    def __getitem__(self, key):
        """Allow dictionary-style access."""
        return self.to_dict()[key]
    
    def items(self):
        """Return items for dict-like behavior."""
        return self.to_dict().items()

    def save(self, path: str) -> None:
        """Saves the measurement data to a file.
        
        If the data is a numpy array, it will be saved as a .npy file.
        If the data is a Polars DataFrame, it will be saved as a .parquet file.
        Other list-like data will be converted to numpy array and saved as .npy.
        np.float64 will be saved as a 0-D numpy array.
        UFloat objects will be saved as a two-element numpy array [nominal, std_dev] in a .npy file.
        """
        default_ext = ".npy"
        if isinstance(self.values, pl.DataFrame):
            default_ext = ".parquet"
        
        if not path.endswith(('.npy', '.parquet')):
            path += default_ext
            print(f"Warning: File extension not specified. Saving as {path}")

        if isinstance(self.values, np.ndarray):
            np.save(path, self.values)
        elif isinstance(self.values, pl.DataFrame):
            if not path.endswith(".parquet"):
                print(f"Warning: Saving Polars DataFrame to non-parquet file '{path}'. Consider using .parquet for DataFrames.")
            self.values.write_parquet(path)
        elif isinstance(self.values, UFloat):
            if not path.endswith(".npy"):
                print(f"Warning: Saving UFloat to non-npy file '{path}'. Consider using .npy.")
            np.save(path, np.array([self.values.nominal_value, self.values.std_dev]))
        elif isinstance(self.values, (list, np.float64)): # Convert list or float64 to ndarray
            if not path.endswith(".npy"):
                print(f"Warning: Saving {type(self.values).__name__} to non-npy file '{path}'. Consider using .npy.")
            np.save(path, np.array(self.values))
        else:
            raise TypeError(f"Unsupported data type for saving: {type(self.values)}. Can save np.ndarray, pl.DataFrame, list, np.float64, or UFloat.")
        print(f"Measurement saved to {path}")

    @property
    def nominal(self) -> float | np.ndarray | pl.DataFrame:
        if isinstance(self.values, UFloat):
            return self.values.nominal_value
        # Handle np.ndarray of UFloats if that's a possibility
        elif isinstance(self.values, np.ndarray) and self.values.size > 0 and \
             isinstance(self.values.flat[0], UFloat):
            return np.array([x.nominal_value for x in self.values.flat]).reshape(self.values.shape)
        # Handle Polars DataFrame with UFloat columns (see Polars serialization)
        # For now, assume if it's a DataFrame, it might already be split or handled by Polars part
        return self.values # type: ignore

    @property
    def sigma(self) -> Optional[float | np.ndarray | pl.DataFrame]:
        if isinstance(self.values, UFloat):
            return self.values.std_dev
        elif isinstance(self.values, np.ndarray) and self.values.size > 0 and \
             isinstance(self.values.flat[0], UFloat):
            return np.array([x.std_dev for x in self.values.flat]).reshape(self.values.shape)
        return None # Or handle DataFrame case

    def __repr__(self) -> str:
        """
        For backward compatibility with tests:
        - 1D arrays return a newline-separated list of values with units (like __str__)
        - Other types use a detailed representation
        """
        if isinstance(self.values, np.ndarray) and self.values.ndim == 1:
            return '\n'.join([f"{val} {self.units}" for val in self.values])
        return (f"MeasurementResult(instrument='{self.instrument}', type='{self.measurement_type}', "
                f"units='{self.units}', values_type='{type(self.values).__name__}', timestamp={self.timestamp})")
    
    def add(self, value: Any) -> None:
        """Adds a new value to the collection. Behavior depends on self.values type."""
        if isinstance(self.values, np.ndarray):
            # This might be inefficient for frequent additions. Consider list then convert.
            self.values = np.append(self.values, value)
        elif isinstance(self.values, list):
            self.values.append(value)
        elif isinstance(self.values, np.float64):
            # Convert to list or ndarray if adding to a single float
            self.values = np.array([self.values, value]) # type: ignore
            print("Warning: Added value to np.float64, converted 'values' to np.ndarray.")
        elif isinstance(self.values, UFloat):
            # If current value is UFloat, adding another value implies creating a list/array of UFloats
            self.values = [self.values, value] # type: ignore
            print("Warning: Added value to UFloat, converted 'values' to a list. Consider using a list of UFloats initially.")
        elif isinstance(self.values, pl.DataFrame):
            # Appending to Polars DataFrame is complex; typically done by creating a new DF and vstacking.
            # This simple 'add' might not be suitable.
            raise NotImplementedError("Direct 'add' to Polars DataFrame not supported. Use 'set_values' or manage DataFrame externally.")
        else:
            raise TypeError(f"Cannot 'add' to type {type(self.values)}")


    def set_values(self, values: Union[np.ndarray, pl.DataFrame, np.float64, TypingList[Any], UFloat]) -> None:
        """Sets the MeasurementValues in the collection."""
        self.values = values

    def get(self, index: int) -> Any:
        """Gets the MeasurementValue at a specified index. Assumes indexable values."""
        if isinstance(self.values, (np.ndarray, list)):
            return self.values[index]
        elif isinstance(self.values, pl.DataFrame):
            # For DataFrame, 'get' by index might mean row.
            # This returns a new DataFrame with one row.
            return self.values[index]
        elif isinstance(self.values, (np.float64, UFloat)) and index == 0:
            return self.values
        raise IndexError(f"Index {index} out of range or type {type(self.values)} not directly indexable by single int.")


    def get_all(self) -> Union[np.ndarray, pl.DataFrame, np.float64, TypingList[Any], UFloat]:
        """Returns all the MeasurementValues in the collection."""
        return self.values

    def clear(self) -> None:
        """Clears all the MeasurementValues from the collection, resetting to an empty/default state."""
        if isinstance(self.values, np.ndarray):
            self.values = np.array([])
        elif isinstance(self.values, (np.float64, UFloat)): # Reset UFloat to a default float or ufloat(0,0)
            self.values = np.float64(0.0) # Or ufloat(0,0) if preferred default for UFloat
        elif isinstance(self.values, pl.DataFrame):
            self.values = pl.DataFrame()
        elif isinstance(self.values, list):
            self.values = []
        else: # Fallback for unknown types, attempt to set to a default float64
            print(f"Warning: Clearing unknown type {type(self.values)}, setting to np.float64(0.0).")
            self.values = np.float64(0.0)
    
    def _to_numpy(self) -> np.ndarray:
        """
        Converts the measurement values to a numpy array if possible.
        For UFloat, it converts to a [nominal, std_dev] array.
        For list/array of UFloats, it converts to an array of [nominal, std_dev] pairs.
        """
        if isinstance(self.values, np.ndarray):
            if self.values.size > 0 and isinstance(self.values.flat[0], UFloat):
                # Array of UFloats
                return np.array([[x.nominal_value, x.std_dev] for x in self.values.flat]).reshape(self.values.shape + (2,))
            return self.values
        elif isinstance(self.values, pl.DataFrame):
            # This needs careful consideration if DataFrame contains UFloat objects.
            # For now, standard conversion. Database serialization handles UFloats in DFs.
            return self.values.to_numpy()
        elif isinstance(self.values, UFloat):
            return np.array([self.values.nominal_value, self.values.std_dev])
        elif isinstance(self.values, list):
            if self.values and isinstance(self.values[0], UFloat):
                return np.array([[x.nominal_value, x.std_dev] for x in self.values]) # type: ignore
            return np.array(self.values)
        elif isinstance(self.values, np.float64):
            return np.array(self.values)
        else:
            raise TypeError(f"Cannot convert type {type(self.values)} to NumPy array.")

    def __len__(self) -> int:
        if isinstance(self.values, (np.ndarray, list)):
            return len(self.values)
        elif isinstance(self.values, (np.float64, UFloat)):
            return 1
        elif isinstance(self.values, pl.DataFrame):
            return self.values.height # Number of rows
        return 0 # Default for unknown types

    def __getitem__(self, index: int) -> Any:
        """Allows indexing into the 'values' attribute."""
        if isinstance(self.values, (np.ndarray, list)):
            return self.values[index]
        elif isinstance(self.values, pl.DataFrame):
            return self.values[index] # Returns a row as a new DataFrame
        elif isinstance(self.values, (np.float64, UFloat)) and index == 0:
            return self.values
        raise IndexError(f"Index {index} not applicable for type {type(self.values)}")

    def __iter__(self) -> Iterator[Any]:
        """Allows iteration over the 'values' attribute."""
        if isinstance(self.values, (np.ndarray, list)):
            return iter(self.values)
        elif isinstance(self.values, pl.DataFrame):
            return iter(self.values.iter_rows())
        elif isinstance(self.values, (np.float64, UFloat)):
            return iter([self.values])
        raise TypeError(f"Iteration not supported for type {type(self.values)}")


    def __delitem__(self, index: int) -> None:
        """Allows deleting an item from 'values' if it's a list or ndarray."""
        if isinstance(self.values, list):
            del self.values[index]
        elif isinstance(self.values, np.ndarray):
            self.values = np.delete(self.values, index, axis=0)
        else:
            raise TypeError(f"Deletion by index not supported for type {type(self.values)}")

    def perform_fft(self) -> 'MeasurementResult':
        """Perform Fast Fourier Transform on the measurement data.
        
        Requires:
        - self.values to be a numpy array of time-domain data
        - self.sampling_rate to be set (in Hz)
        
        Returns:
            A new MeasurementResult containing the FFT data, with frequency in Hz
            and magnitude in the same units as the original data.
        """
        if self.sampling_rate is None:
            raise ValueError("Sampling rate must be set to perform FFT")
        
        if not isinstance(self.values, np.ndarray):
            raise TypeError(f"FFT requires numpy array, got {type(self.values)}")
        
        # Ensure we're working with a 1D array
        values = self.values.flatten() if self.values.ndim > 1 else self.values
        
        # Perform FFT
        fft_values = np.fft.rfft(values)
        fft_magnitude = np.abs(fft_values)
        
        # Create frequency axis
        freqs = np.fft.rfftfreq(len(values), 1/self.sampling_rate)
        
        # Create result with frequency and magnitude
        result_df = pl.DataFrame({
            "frequency": freqs,
            "magnitude": fft_magnitude
        })
        
        return MeasurementResult(
            values=result_df,
            instrument=self.instrument,
            units=self.units,
            measurement_type="FFT",
            timestamp=time.time(),
            original_type=self.measurement_type,
            sampling_rate=self.sampling_rate
        )