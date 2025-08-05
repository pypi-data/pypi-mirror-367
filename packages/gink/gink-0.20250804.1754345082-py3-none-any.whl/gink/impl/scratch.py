from .braid import Braid
from .typedefs import Request
from pathlib import Path
from .directory import Directory

def _get_braid(self, path: str, create_if_missing: bool = False) -> Braid:
    """ Returns the braid associated with the given path, creating it create_if_missing is True.
    """
    parts = Path(path).parts
    if len(parts) == 0 or parts[0] == "/":
        raise ValueError(f"invaid path: {path}")
    directory_keys = list(parts[:-1])
    directory_keys.insert(0, 'braids')
    braid_key = parts[-1]
    current = self._get_app_directory()
    assert isinstance(current, Directory)
    for key in directory_keys:
        if create_if_missing and key not in current:
            self._logger.debug("creating intermediate directory for %s", key)
            current[key] = Directory(database=self._control_db)
        current = current.get(key)
        if not isinstance(current, Directory):
            raise ValueError(f"could not traverse: {key}")
    if create_if_missing and braid_key not in current:
        self._logger.debug("creating braid for %s", braid_key)
        current[braid_key] = Braid(database=self._control_db)
    braid = current[braid_key]
    if not isinstance(braid, Braid):
        raise ValueError("not a braid")
    return braid
