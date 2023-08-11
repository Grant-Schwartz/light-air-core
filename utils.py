from enum import Enum
from datetime import date, datetime
import numpy as np

def JSONHandler(Obj):
    if hasattr(Obj, 'json'):
        return Obj.json()
    elif isinstance(Obj, Enum):
        return Obj.name
    elif isinstance(Obj, (datetime, date)):
        return Obj.isoformat()
    elif isinstance(Obj, np.ndarray):
        return Obj.tolist()
    else:
        raise TypeError("Object of type %s with value of %s is not JSON serializable" % (type(Obj), repr(Obj)))