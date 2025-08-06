import pandas as pd
import numpy as np
import xarray as xr

import json
import gzip
import os
import hashlib
import inspect
import boto3
from botocore.exceptions import ClientError
from typing import Union, Type, Dict, Callable, Any, Optional
from functools import wraps
from pathlib import Path
import os
import yaml
import datetime
import os
import glob
import pprint
import pickle
import time

# Define supported data types for type hints
SupportedDataTypes = Union[
    pd.DataFrame,
    pd.Series,
    np.ndarray,
    dict,
    list,
    xr.Dataset,
    xr.DataArray,
    Any  # Add Any to support generic types via pickle
]

# Try to import geopandas for GeoDataFrame support
try:
    import geopandas as gpd
    GeoDataFrame = gpd.GeoDataFrame
    SupportedDataTypes = Union[SupportedDataTypes, GeoDataFrame]
except ImportError:
    GeoDataFrame = None

# Ensure .reprolab_data directory exists
REPROLAB_DATA_DIR = 'reprolab_data'
os.makedirs(REPROLAB_DATA_DIR, exist_ok=True)

# Mapping from type names to actual types and vice versa
TYPE_MAPPING: Dict[str, Type[SupportedDataTypes]] = {
    'DataFrame': pd.DataFrame,
    'Series': pd.Series,
    'ndarray': np.ndarray,
    'json': (dict, list),  # Handle both dict and list as JSON
    'list': list,  # Backward compatibility for legacy files
    'dict': dict,  # Backward compatibility for legacy files
    'Dataset': xr.Dataset,
    'DataArray': xr.DataArray,
    'pickle': Any  # Generic type for pickle serialization
}

# Add GeoDataFrame support if available
if GeoDataFrame is not None:
    TYPE_MAPPING['GeoDataFrame'] = GeoDataFrame

# Reverse mapping for getting type names
TYPE_NAME_MAPPING = {}
for type_name, type_class in TYPE_MAPPING.items():
    if isinstance(type_class, tuple):
        # Handle tuple of types (like json for dict and list)
        for t in type_class:
            TYPE_NAME_MAPPING[t] = type_name
    else:
        # For backward compatibility, only add if not already mapped
        if type_class not in TYPE_NAME_MAPPING:
            TYPE_NAME_MAPPING[type_class] = type_name
        # If already mapped (e.g., list is mapped to 'json'), keep the primary mapping
        elif type_name in ['json']:  # Primary mapping takes precedence
            TYPE_NAME_MAPPING[type_class] = type_name

# Add GeoDataFrame mapping if available
if GeoDataFrame is not None:
    TYPE_NAME_MAPPING[GeoDataFrame] = 'GeoDataFrame'

def _get_function_hash(func: Callable, args: tuple, kwargs: dict) -> str:
    """
    Calculate a unique hash for a function call based on its code and arguments.
    The hash is based on the function's body and arguments, excluding decorators.
    
    Args:
        func: The function to hash
        args: Positional arguments
        kwargs: Keyword arguments
    
    Returns:
        str: MD5 hash of the function body and its arguments
    """
    # Get function source code
    source = inspect.getsource(func)
    
    # Remove decorators from source code
    lines = source.split('\n')
    # Skip decorator lines (lines starting with @)
    body_lines = [line for line in lines if not line.strip().startswith('@')]
    # Skip empty lines at the start
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    # Reconstruct source without decorators
    source = '\n'.join(body_lines)
    
    # Convert args and kwargs to a stable string representation
    args_str = str(args)
    kwargs_str = str(sorted(kwargs.items()))
    
    # Combine all components and create hash
    hash_input = f"{source}{args_str}{kwargs_str}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def persistio(only_local: bool = False, verbose: bool = False, disable_metadata: bool = False) -> Callable:
    """
    Decorator that caches function results using save_compact and read_compact.
    The cache is based on a hash of the function's source code and its arguments.
    If only_local is False, it will also try to load/save from cloud storage.
    
    Args:
        only_local: If True, only use local storage. If False, also use cloud storage.
        verbose: If True, print detailed logging. If False, minimal logging for performance.
        disable_metadata: If True, skip metadata logging entirely for maximum performance.
    
    Returns:
        Callable: Decorated function that caches its results
    """
    def decorator(func: Callable) -> Callable:
        # Cache expensive operations at decorator level
        _cached_aws_env = None
        
        def get_cached_aws_env():
            nonlocal _cached_aws_env
            if _cached_aws_env is None and not only_local:
                try:
                    _cached_aws_env = get_aws_env()
                except Exception:
                    _cached_aws_env = None
            return _cached_aws_env
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Calculate hash for this function call
            name_hash = _get_function_hash(func, args, kwargs)
            
            if verbose:
                print(f"\n[persistio] Function: {func.__name__}")
                print(f"[persistio] Hash: {name_hash}")
            
            # Only log metadata on cache misses to avoid overhead
            metadata_logged = False
            
            # Try to read from local cache first
            try:
                if verbose:
                    print("[persistio] Attempting to load from local cache...")
                result = read_compact(name_hash, verbose=verbose)
                if verbose:
                    print("[persistio] Successfully loaded from local cache!")
                return result
            except ValueError:
                if verbose:
                    print("[persistio] Local cache miss")
                
                # Log metadata only on cache miss (unless disabled)
                if not metadata_logged and not disable_metadata:
                    try:
                        bucket_name = "local_only"
                        aws_env = get_cached_aws_env()
                        if aws_env:
                            bucket_name = aws_env['AWS_BUCKET']
                        
                        persist_metadata_for_current_notebook(name_hash, bucket_name)
                        if verbose:
                            print(f"[persistio] Trigger logged for function: {func.__name__}")
                        metadata_logged = True
                    except Exception as metadata_error:
                        if verbose:
                            print(f"[persistio] Failed to log trigger metadata: {str(metadata_error)}")
            
            # If local cache fails and cloud is enabled, try cloud
            if not only_local:
                try:
                    if verbose:
                        print("[persistio] Attempting to load from cloud...")
                    
                    aws_env = get_cached_aws_env()
                    if aws_env:
                        # Initialize S3 client
                        s3_client = boto3.client(
                            's3',
                            aws_access_key_id=aws_env['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=aws_env['AWS_SECRET_ACCESS_KEY']
                        )
                        
                        # List objects in bucket with the hash prefix
                        response = s3_client.list_objects_v2(
                            Bucket=aws_env['AWS_BUCKET'],
                            Prefix=name_hash
                        )
                        
                        # Check if we found any matching files
                        if 'Contents' in response:
                            # Get the first matching file
                            cloud_file = response['Contents'][0]['Key']
                            if verbose:
                                print(f"[persistio] Found file in cloud: {cloud_file}")
                            download_from_cloud(cloud_file)
                            result = read_compact(name_hash, verbose=verbose)
                            if verbose:
                                print("[persistio] Successfully loaded from cloud!")
                            return result
                        else:
                            if verbose:
                                print("[persistio] No matching file found in cloud")
                except Exception as e:
                    if verbose:
                        print(f"[persistio] Cloud load failed: {str(e)}")
            
            # If both local and cloud attempts fail, execute function
            if verbose:
                print("[persistio] Cache miss - executing function...")
            result = func(*args, **kwargs)
            
            # Save result (now supports all types via pickle fallback)
            if verbose:
                print(f"[persistio] Saving result of type {type(result).__name__} to cache...")
            save_compact(result, name_hash)
            if verbose:
                print("[persistio] Successfully saved to local cache!")
            
            if not only_local:
                try:
                    # Find the file that was just saved - optimize with direct file check
                    file_pattern = f"{name_hash}.*"
                    import glob
                    matching_files = glob.glob(os.path.join(REPROLAB_DATA_DIR, file_pattern))
                    if matching_files:
                        cloud_file = os.path.basename(matching_files[0])
                        upload_to_cloud(cloud_file)
                        if verbose:
                            print("[persistio] Successfully saved to cloud!")
                except Exception as e:
                    if verbose:
                        print(f"[persistio] Cloud save failed: {str(e)}")
            
            return result
        
        return wrapper
    return decorator

def _get_extension(data_type: Type[SupportedDataTypes]) -> str:
    """
    Get the appropriate file extension for a given data type.
    
    Args:
        data_type: The type of data to get extension for.
    
    Returns:
        str: The appropriate file extension (e.g., '.parquet', '.npy', '.json.gz', '.nc', '.pkl.gz')
    """
    if data_type in (pd.DataFrame, pd.Series):
        return '.parquet'
    elif data_type == np.ndarray:
        return '.npy'
    elif data_type in (dict, list):
        return '.json.gz'
    elif data_type in (xr.Dataset, xr.DataArray):
        return '.nc'
    elif GeoDataFrame is not None and data_type == GeoDataFrame:
        return '.gpkg'
    else:
        # For any unsupported type, use pickle with gzip compression
        return '.pkl.gz'

def save_compact(data: SupportedDataTypes, name_hash: str) -> None:
    """
    Save a Python data structure to the most compact file format possible in the .reprolab_data directory.
    
    Args:
        data: Input data (pandas.DataFrame, pandas.Series, numpy.ndarray, dict, list,
              xarray.Dataset, xarray.DataArray, or any other Python object via pickle).
        name_hash: Prefix for the filename. The final filename will be in the format:
                  <name_hash>.<original_type>.<compact_type>
    
    Raises:
        ValueError: If data type is unsupported or name_hash is invalid.
        Exception: For file I/O or library-specific errors.
    """
    try:
        original_type = type(data)
        
        # Check if it's a supported specific type
        if original_type in TYPE_NAME_MAPPING:
            original_type_name = TYPE_NAME_MAPPING[original_type]
        else:
            # For unsupported types, use generic pickle serialization
            original_type_name = 'pickle'
            
        compact_type = _get_extension(original_type).lstrip('.')
        
        file_name = f"{name_hash}.{original_type_name}.{compact_type}"
        file_path = os.path.join(REPROLAB_DATA_DIR, file_name)
        
        # GeoDataFrame (if available) - check this first to avoid being detected as DataFrame
        if GeoDataFrame is not None and isinstance(data, GeoDataFrame):
            # Save as GeoPackage for best compatibility
            data.to_file(file_path, driver='GPKG')
        
        # Pandas DataFrame
        elif isinstance(data, pd.DataFrame):
            data.to_parquet(file_path, engine='pyarrow', compression='snappy')
        
        # Pandas Series
        elif isinstance(data, pd.Series):
            data.to_frame().to_parquet(file_path, engine='pyarrow', compression='snappy')
        
        # NumPy Array (including Structured Array)
        elif isinstance(data, np.ndarray):
            np.save(file_path, data)
        
        # Python Dictionary or List (both handled as JSON)
        elif isinstance(data, (dict, list)):
            # Check if data contains non-JSON-serializable objects
            def is_json_serializable(obj):
                try:
                    json.dumps(obj)
                    return True
                except (TypeError, ValueError):
                    return False
            
            if is_json_serializable(data):
                # Use JSON for simple dicts/lists
                with gzip.open(file_path, 'wt', encoding='utf-8', compresslevel=6) as f:
                    json.dump(data, f)
            else:
                # Fall back to pickle for complex dicts/lists
                with gzip.open(file_path, 'wb', compresslevel=6) as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # xarray Dataset or DataArray
        elif isinstance(data, (xr.Dataset, xr.DataArray)):
            try:
                # Try netCDF4 first
                if isinstance(data, xr.Dataset):
                    encoding = {var: {'zlib': True, 'complevel': 6} for var in data.variables}
                else:
                    # For DataArray, create a Dataset
                    encoding = {data.name: {'zlib': True, 'complevel': 6}}
                    data = data.to_dataset()
                
                data.to_netcdf(file_path, engine='netcdf4', encoding=encoding)
            except ImportError:
                # Fall back to pickle if netCDF4 is not available
                with gzip.open(file_path, 'wb', compresslevel=6) as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Generic pickle serialization for any other type
        else:
            with gzip.open(file_path, 'wb', compresslevel=6) as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Data saved successfully - removed print for performance
    
    except Exception as e:
        raise Exception(f"Error saving data: {str(e)}")

def read_compact(name_hash: str, verbose: bool = False) -> SupportedDataTypes:
    """
    Read a file saved in a compact format back into its original Python data type from the .reprolab_data directory.
    
    Args:
        name_hash: Prefix of the file to read. The function will look for a file matching:
                  <name_hash>.<original_type>.<compact_type>
        verbose: If True, print detailed logging. If False, minimal logging for performance.
    
    Returns:
        Data in its original Python type (pandas.DataFrame, pandas.Series, numpy.ndarray, dict, list,
        xarray.Dataset, xarray.DataArray, or any other Python object via pickle).
    
    Raises:
        ValueError: If file does not exist, format is unsupported, or type is invalid.
        Exception: For file I/O or library-specific errors.
    """
    # Find the file with the given prefix
    matching_files = [f for f in os.listdir(REPROLAB_DATA_DIR) if f.startswith(name_hash + '.')]
    
    if not matching_files:
        raise ValueError(f"No file found with prefix '{name_hash}' in {REPROLAB_DATA_DIR}")
    if len(matching_files) > 1:
        raise ValueError(f"Multiple files found with prefix '{name_hash}' in {REPROLAB_DATA_DIR}: {matching_files}")
    
    file_name = matching_files[0]
    file_path = os.path.join(REPROLAB_DATA_DIR, file_name)
    
    if verbose:
        print(f"[read_compact] Processing file: {file_name}")
        print(f"[read_compact] File path: {file_path}")
    
    # Extract original type from filename
    # Handle filenames with multiple dots (e.g., test_xml_element.pickle.pkl.gz)
    parts = file_name.split('.')
    if verbose:
        print(f"[read_compact] Filename parts: {parts}")
        print(f"[read_compact] Number of parts: {len(parts)}")
    
    if len(parts) < 3:
        raise ValueError(f"Invalid filename format: {file_name}")
    
    # For files with multiple dots, we need to handle special cases
    # e.g., "hash.pickle.pkl.gz" -> type is "pickle"
    # e.g., "hash.DataFrame.parquet" -> type is "DataFrame"
    if len(parts) >= 4 and parts[1] == 'pickle' and parts[2] == 'pkl':
        # Special case for pickle files: hash.pickle.pkl.gz
        original_type_name = 'pickle'
    else:
        # Normal case: second part is the type
        original_type_name = parts[1]
    
    if verbose:
        print(f"[read_compact] Extracted type name: {original_type_name}")
    
    if original_type_name not in TYPE_MAPPING:
        raise ValueError(f"Unknown type name in filename: {original_type_name}")
    
    original_type = TYPE_MAPPING[original_type_name]
    if verbose:
        print(f"[read_compact] Mapped to type: {original_type}")
    
    try:
        # Pandas DataFrame
        if original_type == pd.DataFrame:
            if verbose:
                print(f"[read_compact] Reading as DataFrame")
            return pd.read_parquet(file_path, engine='pyarrow')
        
        # Pandas Series
        elif original_type == pd.Series:
            if verbose:
                print(f"[read_compact] Reading as Series")
            df = pd.read_parquet(file_path, engine='pyarrow')
            if df.shape[1] != 1:
                raise ValueError("Parquet file must contain exactly one column for Series")
            return df.iloc[:, 0]
        
        # GeoDataFrame (if available)
        elif GeoDataFrame is not None and original_type == GeoDataFrame:
            if verbose:
                print(f"[read_compact] Reading as GeoDataFrame")
            # Use the driver prefix approach
            return gpd.read_file(f"GPKG:{file_path}")
        
        # NumPy Array (including Structured Array)
        elif original_type == np.ndarray:
            if verbose:
                print(f"[read_compact] Reading as NumPy array")
            return np.load(file_path)
        
        # Python Dictionary or List (both handled as JSON)
        elif original_type in (dict, list) or (isinstance(original_type, tuple) and any(t in (dict, list) for t in original_type)):
            if verbose:
                print(f"[read_compact] Reading as JSON (dict/list)")
            try:
                # Try JSON first
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    return json.load(f)
            except (UnicodeDecodeError, json.JSONDecodeError):
                # Fall back to pickle if JSON fails
                if verbose:
                    print(f"[read_compact] JSON failed, trying pickle")
                with gzip.open(file_path, 'rb') as f:
                    return pickle.load(f)
        
        # xarray Dataset
        elif original_type == xr.Dataset:
            if verbose:
                print(f"[read_compact] Reading as xarray Dataset")
            try:
                return xr.open_dataset(file_path, engine='netcdf4')
            except Exception:
                # Fall back to pickle if netCDF4 fails
                if file_path.endswith('.gz'):
                    with gzip.open(file_path, 'rb') as f:
                        return pickle.load(f)
                else:
                    with open(file_path, 'rb') as f:
                        return pickle.load(f)
        
        # xarray DataArray
        elif original_type == xr.DataArray:
            if verbose:
                print(f"[read_compact] Reading as xarray DataArray")
            try:
                ds = xr.open_dataset(file_path, engine='netcdf4')
                if len(ds.data_vars) != 1:
                    raise ValueError("NetCDF file must contain exactly one variable for DataArray")
                return ds[list(ds.data_vars.keys())[0]]
            except Exception:
                # Fall back to pickle if netCDF4 fails
                if file_path.endswith('.gz'):
                    with gzip.open(file_path, 'rb') as f:
                        return pickle.load(f)
                else:
                    with open(file_path, 'rb') as f:
                        return pickle.load(f)
        
        # Generic pickle deserialization for any other type
        elif original_type == Any:  # This handles the 'pickle' type
            if verbose:
                print(f"[read_compact] Reading as pickle")
            # Check if file is gzipped by looking at the extension
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rb') as f:
                    return pickle.load(f)
            else:
                # Regular pickle file (not gzipped)
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
        
        else:
            raise ValueError(f"Unsupported original type: {original_type}. Supported types: {list(TYPE_MAPPING.keys())}")
    
    except Exception as e:
        if verbose:
            print(f"[read_compact] Error reading data: {str(e)}")
        raise Exception(f"Error reading data: {str(e)}")

def get_aws_env() -> dict:
    """
    Read AWS credentials from aws_env.json file in the reprolab_data directory.
    
    Returns:
        dict: Dictionary containing AWS credentials (AWS_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    
    Raises:
        ValueError: If required credentials are missing
    """
    try:
        aws_env_path = Path(REPROLAB_DATA_DIR) / 'aws_env.json'
        if not aws_env_path.exists():
            raise ValueError("AWS credentials file not found")
            
        with open(aws_env_path) as f:
            env_vars = json.load(f)
            
        # Check for required credentials
        required_vars = ['AWS_BUCKET', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        missing_vars = [var for var in required_vars if var not in env_vars or not env_vars[var]]
        
        if missing_vars:
            raise ValueError(f"Missing required AWS credentials: {', '.join(missing_vars)}")
            
        return env_vars
    except Exception as e:
        raise ValueError(f"Could not read AWS credentials: {str(e)}")

def upload_to_cloud(file_name: str) -> None:
    """
    Upload a file from reprolab_data to S3.
    
    Args:
        file_name: Name of the file to upload (must exist in reprolab_data)
    
    Raises:
        ValueError: If required credentials are not set
        Exception: If upload fails
    """
    try:
        # Get AWS credentials
        aws_env = get_aws_env()
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_env['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=aws_env['AWS_SECRET_ACCESS_KEY']
        )
        
        # Create full local path
        local_path = os.path.join(REPROLAB_DATA_DIR, file_name)
        if not os.path.exists(local_path):
            raise ValueError(f"File not found: {local_path}")
        
        print(f"[upload_to_cloud] Uploading {local_path} to s3://{aws_env['AWS_BUCKET']}/{file_name}")
        s3_client.upload_file(local_path, aws_env['AWS_BUCKET'], file_name)
        print(f"[upload_to_cloud] Successfully uploaded to s3://{aws_env['AWS_BUCKET']}/{file_name}")
        
    except ClientError as e:
        raise Exception(f"Failed to upload file: {str(e)}")
    except Exception as e:
        raise Exception(f"Error during upload: {str(e)}")

def download_from_cloud(file_name: str) -> str:
    """
    Download a file from S3 and save it to reprolab_data.
    
    Args:
        file_name: Name of the file to download
    
    Returns:
        str: Path to the downloaded file
    
    Raises:
        ValueError: If required credentials are not set
        Exception: If download fails
    """
    try:
        # Get AWS credentials
        aws_env = get_aws_env()
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_env['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=aws_env['AWS_SECRET_ACCESS_KEY']
        )
        
        # Create local path
        local_path = os.path.join(REPROLAB_DATA_DIR, file_name)
        
        print(f"[download_from_cloud] Downloading s3://{aws_env['AWS_BUCKET']}/{file_name} to {local_path}")
        s3_client.download_file(aws_env['AWS_BUCKET'], file_name, local_path)
        print(f"[download_from_cloud] Successfully downloaded to {local_path}")
        
        return local_path
        
    except ClientError as e:
        raise Exception(f"Failed to download file: {str(e)}")
    except Exception as e:
        raise Exception(f"Error during download: {str(e)}")


def get_last_changed_notebook():
    """
    Returns the name of the most recently modified Jupyter notebook (.ipynb) file 
    in the current directory.
    """
    try:
        # Find all .ipynb files in the current directory
        notebook_files = glob.glob('*.ipynb')
        if not notebook_files:
            raise RuntimeError("No .ipynb files found in the current directory")
        
        # Get the most recently modified notebook
        latest_notebook = max(notebook_files, key=os.path.getmtime)
        return latest_notebook
    except Exception as e:
        raise RuntimeError(f"Error finding last changed notebook: {str(e)}")

def persist_metadata_for_current_notebook(cell_hash, bucket_name):
    """
    Store hashes in the fastest possible format for reading and writing.
    Uses persistio_hashes.yaml with simple hash list format.
    """
    try:
        yaml_filename = "persistio_hashes.yaml"
        now_iso = datetime.datetime.now(datetime.UTC)

        # Load existing hashes or create new file
        hashes = set()
        if os.path.exists(yaml_filename):
            try:
                with open(yaml_filename, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    hashes = set(data.get('hashes', []))
            except yaml.YAMLError as e:
                print(f"⚠️ Warning: Corrupted YAML file detected. Creating backup and starting fresh.")
                # Create backup of corrupted file
                backup_filename = f"{yaml_filename}.backup_{int(time.time())}"
                try:
                    import shutil
                    shutil.copy2(yaml_filename, backup_filename)
                    print(f"📁 Backup created: {backup_filename}")
                except Exception as backup_error:
                    print(f"⚠️ Failed to create backup: {backup_error}")

        # Add new hash
        hashes.add(cell_hash)

        # Create minimal metadata structure for fastest I/O
        metadata = {
            'last_updated': now_iso.isoformat(),
            'bucket_name': bucket_name,
            'hashes': sorted(list(hashes))  # Sorted for consistent output
        }

        # Write to temporary file first to avoid corruption
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as temp_file:
            yaml.dump(metadata, temp_file, sort_keys=False, default_flow_style=False, indent=2)
            temp_filename = temp_file.name
        
        # Move temporary file to final location
        import shutil
        shutil.move(temp_filename, yaml_filename)

        print(f"✅ Hash written to {yaml_filename}")
    except Exception as e:
        print(f"❌ Error persisting hash: {e}")
        # If all else fails, try to write minimal hash list
        try:
            minimal_metadata = {
                'last_updated': now_iso.isoformat(),
                'bucket_name': bucket_name,
                'hashes': [cell_hash]
            }
            with open(yaml_filename, 'w') as f:
                yaml.dump(minimal_metadata, f, default_flow_style=False, indent=2)
            print(f"✅ Minimal hash written to {yaml_filename}")
        except Exception as minimal_error:
            print(f"❌ Failed to write even minimal hash: {minimal_error}")

def download_notebook_cache_package(notebook_name: str, output_zip_path: str = None) -> str:
    """
    Download all cached data for a given notebook and package it with metadata into a zip file.
    
    Args:
        notebook_name: Name of the notebook (with or without .ipynb extension)
        output_zip_path: Optional path for the output zip file. If None, uses default naming.
    
    Returns:
        str: Path to the created zip file
    
    Raises:
        ValueError: If notebook metadata file is not found
        Exception: If download or packaging fails
    """
    import zipfile
    import tempfile
    import shutil
    
    try:
        # Use the new hash file format
        yaml_filename = "persistio_hashes.yaml"
        
        # Check if hash file exists
        if not os.path.exists(yaml_filename):
            raise ValueError(f"Hash file not found: {yaml_filename}")
        
        # Load metadata
        with open(yaml_filename, 'r') as f:
            metadata = yaml.safe_load(f)
        
        if not metadata or 'hashes' not in metadata:
            raise ValueError(f"No cached hashes found in file: {yaml_filename}")
        
        # Create output zip path if not provided
        if output_zip_path is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_zip_path = f"{notebook_name}_cache_package_{timestamp}.zip"
        
        print(f"[download_notebook_cache_package] Processing notebook: {notebook_name}")
        print(f"[download_notebook_cache_package] Using hash file: {yaml_filename}")
        print(f"[download_notebook_cache_package] Found {len(metadata['hashes'])} cached hashes")
        
        # Create temporary directory for organizing files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy hash file to temp directory
            temp_yaml_path = os.path.join(temp_dir, yaml_filename)
            shutil.copy2(yaml_filename, temp_yaml_path)
            
            # Get AWS environment for cloud downloads
            aws_env = None
            try:
                aws_env = get_aws_env()
                print(f"[download_notebook_cache_package] Using cloud storage: {aws_env['AWS_BUCKET']}")
            except Exception as e:
                print(f"[download_notebook_cache_package] Cloud storage not available: {str(e)}")
            
            # Download each cached file
            downloaded_count = 0
            for cell_hash in metadata['hashes']:
                
                # Check if file exists locally first
                local_files = [f for f in os.listdir(REPROLAB_DATA_DIR) if f.startswith(cell_hash + '.')]
                
                if local_files:
                    # File exists locally, copy it
                    local_file = local_files[0]
                    local_path = os.path.join(REPROLAB_DATA_DIR, local_file)
                    temp_path = os.path.join(temp_dir, local_file)
                    shutil.copy2(local_path, temp_path)
                    print(f"[download_notebook_cache_package] Copied local file: {local_file}")
                    downloaded_count += 1
                
                elif aws_env:
                    # Try to download from cloud
                    try:
                        s3_client = boto3.client(
                            's3',
                            aws_access_key_id=aws_env['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=aws_env['AWS_SECRET_ACCESS_KEY']
                        )
                        
                        # List objects with the hash prefix
                        response = s3_client.list_objects_v2(
                            Bucket=aws_env['AWS_BUCKET'],
                            Prefix=cell_hash
                        )
                        
                        if 'Contents' in response:
                            cloud_file = response['Contents'][0]['Key']
                            temp_path = os.path.join(temp_dir, cloud_file)
                            
                            # Download from S3
                            s3_client.download_file(aws_env['AWS_BUCKET'], cloud_file, temp_path)
                            print(f"[download_notebook_cache_package] Downloaded from cloud: {cloud_file}")
                            downloaded_count += 1
                        else:
                            print(f"[download_notebook_cache_package] Warning: No cloud file found for hash: {cell_hash}")
                    
                    except Exception as e:
                        print(f"[download_notebook_cache_package] Warning: Failed to download {cell_hash} from cloud: {str(e)}")
                else:
                    print(f"[download_notebook_cache_package] Warning: No local or cloud file found for hash: {cell_hash}")
            
            # Create zip file
            print(f"[download_notebook_cache_package] Creating zip package: {output_zip_path}")
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from temp directory to zip
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arc_name)
            
            print(f"[download_notebook_cache_package] ✅ Successfully created package: {output_zip_path}")
            print(f"[download_notebook_cache_package] 📦 Package contains {downloaded_count} cached files + metadata")
            
            return output_zip_path
    
    except Exception as e:
        raise Exception(f"Failed to create notebook cache package: {str(e)}")

import subprocess

def commit_and_checkout_git_tag(tag, repo_path='.'):
    try:
        # Ensure the tag exists
        result = subprocess.run(
            ['git', '-C', repo_path, 'tag'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        tags = [t for t in result.stdout.strip().split('\n') if t]

        if tag not in tags:
            print(f"Tag '{tag}' not found.")
            return False

        # Stage all changes (new, modified, deleted)
        subprocess.run(['git', '-C', repo_path, 'add', '-A'], check=True)

        # Check if there is anything to commit
        status_result = subprocess.run(
            ['git', '-C', repo_path, 'status', '--porcelain'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if status_result.stdout.strip():  # There are changes to commit
            subprocess.run(
                ['git', '-C', repo_path, 'commit', '-m', f'Committing before checkout to tag {tag}'],
                check=True
            )
            print(f"Committed changes before checking out to tag '{tag}'.")
        else:
            print("No changes to commit before checkout.")

        # Checkout to the tag
        subprocess.run(['git', '-C', repo_path, 'checkout', tag], check=True)
        print(f"Checked out to tag '{tag}' successfully.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def download_reproducability_package(tag_name: str) -> str:
    """
    Create a complete reproducibility package for a given git tag.
    
    This function:
    1. Checks out to the specified git tag
    2. Downloads code package as <tag>_code.zip
    3. Downloads data package as <tag>_data.zip
    4. Combines both into <tag>_reproducability_package.zip
    
    Args:
        tag_name: The git tag to create the package for
    
    Returns:
        str: Path to the final reproducibility package zip file
    
    Raises:
        Exception: If any step in the process fails
    """
    import zipfile
    import tempfile
    import shutil
    import glob
    
    try:
        print(f"[download_reproducability_package] 🚀 Starting reproducibility package creation for tag: {tag_name}")
        
        # Step 1: Checkout to the git tag
        print(f"[download_reproducability_package] 📋 Step 1: Checking out to git tag '{tag_name}'")
        if not commit_and_checkout_git_tag(tag_name):
            raise Exception(f"Failed to checkout to tag '{tag_name}'")
        
        # Step 2: Find all notebooks in the current directory
        print(f"[download_reproducability_package] 📋 Step 2: Finding notebooks")
        notebook_files = glob.glob('*.ipynb')
        if not notebook_files:
            raise Exception("No .ipynb files found in the current directory")
        
        print(f"[download_reproducability_package] Found {len(notebook_files)} notebooks: {notebook_files}")
        
        # Step 3: Create code package (all files except those in folders starting with .)
        print(f"[download_reproducability_package] 📋 Step 3: Creating code package")
        code_zip_path = f"{tag_name}_code.zip"
        
        with zipfile.ZipFile(code_zip_path, 'w', zipfile.ZIP_DEFLATED) as code_zip:
            # Add all files in the current directory and subdirectories
            for root, dirs, files in os.walk('.'):
                # Skip directories that start with a dot and node_modules
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
                
                for file in files:
                    # Skip certain file types
                    if file.endswith(('.pyc', '.pyo', '.DS_Store', '.zip', '.tar.gz')):
                        continue
                    
                    file_path = os.path.join(root, file)
                    # Use relative path for the archive
                    arc_name = os.path.relpath(file_path, '.')
                    code_zip.write(file_path, arc_name)
                    print(f"[download_reproducability_package] Added to code package: {arc_name}")
        
        print(f"[download_reproducability_package] ✅ Code package created: {code_zip_path}")
        
        # Step 4: Create data packages for each notebook
        print(f"[download_reproducability_package] 📋 Step 4: Creating data packages")
        data_packages = []
        
        for notebook in notebook_files:
            notebook_name = notebook.replace('.ipynb', '')
            try:
                data_zip_path = f"{tag_name}_{notebook_name}_data.zip"
                download_notebook_cache_package(notebook_name, data_zip_path)
                data_packages.append(data_zip_path)
                print(f"[download_reproducability_package] ✅ Data package created: {data_zip_path}")
            except Exception as e:
                print(f"[download_reproducability_package] ⚠️ Warning: Failed to create data package for {notebook_name}: {str(e)}")
        
        # Step 5: Create final reproducibility package
        print(f"[download_reproducability_package] 📋 Step 5: Creating final reproducibility package")
        final_package_path = f"{tag_name}_reproducability_package.zip"
        
        with zipfile.ZipFile(final_package_path, 'w', zipfile.ZIP_DEFLATED) as final_zip:
            # Add code package
            final_zip.write(code_zip_path, f"code/{code_zip_path}")
            print(f"[download_reproducability_package] Added to final package: code/{code_zip_path}")
            
            # Add data packages
            for data_package in data_packages:
                final_zip.write(data_package, f"data/{data_package}")
                print(f"[download_reproducability_package] Added to final package: data/{data_package}")
            
            # Add a README file with package information
            readme_content = f"""# Reproducibility Package for Tag: {tag_name}

This package contains all the code and data needed to reproduce the results from git tag '{tag_name}'.

## Contents

### Code Package
- `code/{code_zip_path}`: Contains all project files (excluding files in folders starting with '.' and node_modules)

### Data Packages
"""
            for data_package in data_packages:
                notebook_name = data_package.replace(f"{tag_name}_", "").replace("_data.zip", "")
                readme_content += f"- `data/{data_package}`: Cached data for {notebook_name}.ipynb\n"
            
            readme_content += f"""
## Usage

1. Extract this package
2. Extract the code package to get the notebooks
3. Extract the data packages to get the cached data
4. Run the notebooks with the reprolab environment

## Package Creation Details
- Created on: {datetime.datetime.now(datetime.UTC).isoformat()}
- Git tag: {tag_name}
- Total notebooks: {len(notebook_files)}
- Total data packages: {len(data_packages)}
"""
            
            final_zip.writestr("README.md", readme_content)
            print(f"[download_reproducability_package] Added to final package: README.md")
        
        # Clean up intermediate files
        print(f"[download_reproducability_package] 🧹 Cleaning up intermediate files")
        try:
            os.remove(code_zip_path)
            for data_package in data_packages:
                os.remove(data_package)
            print(f"[download_reproducability_package] ✅ Intermediate files cleaned up")
        except Exception as e:
            print(f"[download_reproducability_package] ⚠️ Warning: Failed to clean up some intermediate files: {str(e)}")
        
        print(f"[download_reproducability_package] 🎉 SUCCESS! Reproducibility package created: {final_package_path}")
        print(f"[download_reproducability_package] 📦 Package contains:")
        print(f"   - Code package with {len(notebook_files)} notebooks")
        print(f"   - {len(data_packages)} data packages")
        print(f"   - README with usage instructions")
        
        # Checkout back to main branch
        print(f"[download_reproducability_package] 🔄 Checking out to main branch...")
        try:
            subprocess.run(['git', 'checkout', 'main'], check=True)
            print(f"[download_reproducability_package] ✅ Successfully checked out to main branch")
        except subprocess.CalledProcessError as e:
            print(f"[download_reproducability_package] ⚠️ Warning: Failed to checkout to main branch: {str(e)}")
        
        return final_package_path
    
    except Exception as e:
        print(f"[download_reproducability_package] ❌ ERROR: Failed to create reproducibility package: {str(e)}")
        raise Exception(f"Failed to create reproducibility package for tag '{tag_name}': {str(e)}")

import subprocess
import re

def list_and_sort_git_tags(repo_path='.'):
    try:
        result = subprocess.run(
            ['git', '-C', repo_path, 'tag'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        tags = result.stdout.strip().split('\n')
        tags = [tag for tag in tags if tag]

        # Convert tags like v1.2.3 to 123 for sorting
        def tag_to_sort_key(tag):
            match = re.match(r'v(\d+)\.(\d+)\.(\d+)', tag)
            if match:
                return int(''.join(match.groups()))
            return -1  # Push malformed tags to the end

        sorted_tags = sorted(tags, key=tag_to_sort_key, reverse=True)
        return sorted_tags
    except subprocess.CalledProcessError as e:
        print(f"Error listing tags: {e.stderr}")
        return []

