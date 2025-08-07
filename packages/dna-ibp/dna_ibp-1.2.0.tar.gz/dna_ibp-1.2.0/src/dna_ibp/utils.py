# utils.py
import re
import shutil
from pandas import DataFrame, Series
from uuid import UUID

def is_valid_uuid(test_uuid: str) -> bool:
    """
    Util function that checks whether the input is a valid UUID.

    Returns: True (input is a valid UUID) | False (input is not a valid UUID)
    """
    try:
        uuid_obj: UUID = UUID(test_uuid)
    except (ValueError, AttributeError):
        return False
    return str(uuid_obj) == test_uuid

def is_int_or_slice(input: str) -> bool:
    """
    Util function that checks whether the input is either int or a convertible array slice ("a:b").

    Returns: True (input is either int or a slice) | False (input is neither int or a slice)
    """
    try:
        match = re.fullmatch("-?\d:?\d?", input)
    except TypeError:
        return False
    return match

def is_fasta(file_path: str) -> bool:
    """
    Util function that checks whether the input points to a FASTA file.

    Returns: True (input path points to a FASTA file) | False (input path doesn't point to a FASTA file)
    """
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                return True
            else:
                return False
    return False

def is_multi_fasta(file_path: str) -> bool:
    """
    Util function used to check whether the input path points to a MultiFASTA file (FASTA with multiple entries).

    Returns: True | False
    """
    with open(file_path, 'r') as file:
        header_count = sum(1 for line in file if line.startswith('>'))
    return header_count > 1
    
def parse_slice(input: str) -> int | slice:
    """
    Util function used to convert 'slice' strings into array slices

    Returns: int (if input only contains a single digit) | slice (otherwise)
    """
    try:
        return int(input)
    except ValueError:
        parts: list[str] = input.split(":")
        indices: int = [int(x) if x else None for x in parts]
        return slice(*indices)

def format_dataframe(df_or_ser: DataFrame | Series) -> None:
    """
    Util function used to improve readability of displayed DataFrames in the CLI.

    Returns: None
    """  
    terminal_window_size = shutil.get_terminal_size().columns
    padding = 2
    if isinstance(df_or_ser, Series):
        df = df_or_ser.to_frame()
    elif isinstance(df_or_ser, DataFrame):
        df = df_or_ser
    else:
        raise TypeError("Input is not Pandas DataFrame or Series")

    column_widths = [max(len(str(col)), df[col].astype(str).map(len).max()) + padding for col in df.columns]
    
    groups = []
    current_group = []
    current_width = 0

    for col, width in zip(df.columns, column_widths):
        if current_width + width <= terminal_window_size or not current_group:
            current_group.append(col)
            current_width += width
        else:
            groups.append(current_group)
            current_group = [col]
            current_width = width
    if current_group:
        groups.append(current_group)

    ind = True if isinstance(df_or_ser, Series) else False
    for group in groups:
        print("-" * terminal_window_size)
        print(df[group].to_string(index=ind))