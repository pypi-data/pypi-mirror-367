# coding: utf-8

# Standard Python libraries
from pathlib import Path
from importlib import resources

def read_calc_file(parent_module: str,
                   filename: str) -> str:
    """
    Loads a file from the working directory if it is there, or from within
    iprPy if not.  Allows for quick modifications.
    
    Parameters
    ----------
    parent_module : str
        The name of the parent module where the file resource should be located.
    filename : str
        The name of the file to read/get content for.
    """
    if Path(filename).is_file():
        with open(filename, encoding='UTF-8') as f:
            return f.read()
    elif hasattr(resources, 'files'):
        return resources.files(parent_module).joinpath(filename).read_text(encoding='UTF-8')
    else:
        return resources.read_text(parent_module, filename, encoding='UTF-8')
