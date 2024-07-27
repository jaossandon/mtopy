import numpy as np
from datetime import datetime

def datenumvec(in_dict):
    """
    Converts date and time components into a datenum-like format and removes duplicates.
    
    Parameters:
    in_dict (dict): Dictionary containing Year, Month, Day, Hour, Minute, and Second arrays.
    
    Returns:
    tuple: (unique datenums, indices to keep, indices to throw away)
    """
    n = len(in_dict['Hour'])
    time = np.zeros(n)

    for i in range(n):
        dt = datetime(
            int(in_dict['Year'][i]),
            int(in_dict['Month'][i]),
            int(in_dict['Day'][i]),
            int(in_dict['Hour'][i]),
            int(in_dict['Minute'][i]),
            int(in_dict['Second'][i])
        )
        time[i] = dt.timestamp()

    unique_time, keep_indices = np.unique(time, return_index=True)
    throw_indices = np.setdiff1d(np.arange(n), keep_indices)
    
    return unique_time, keep_indices, throw_indices
