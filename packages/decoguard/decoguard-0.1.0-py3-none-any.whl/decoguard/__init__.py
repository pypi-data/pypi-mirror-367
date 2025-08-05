"""
decoguard: Validate decorated functions using meta-decorators. 
Can be used to improve error reporting without code duplication from precondition demanding decorators.
"""

from .asserts import *
from .decorators import *
from .errors import *
from .validators import *