"""
Defines a decorator function, which can manage multiple classes as singletons
Based on the singleton by "Editor: 82 of wiki.python.org", with considerable
improvement.

This provides two decorators

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import functools
import inspect
from threading import RLock

from typing import TypeVar
# if sys.version_info < (3,10) :
#    from typing import Union as union

Class = TypeVar('Class')

def singleton(cls: Class) -> Class :
    """
    Use class as singleton, by modifications to __new__ and __init__
    Modifying __del__ is not required, since cls.__it__ ensures we will
    always have a pointer to the singleton after it is created, so
    it will never be garbage collected.
    """
    singleton_warning = """
    Singleton Warning: singletons are intended to be single instance, and thus
    not customizable. Arguments to __init__ are not recommended, and are
    ignored after the first instantiation. Consider using PyPi
    "simple-singleton", which is like a singleton, but expects variations.
    """

    if not inspect.isclass(cls) :
        raise(ValueError("@singleton should decorate a class declaration"))
    
    is_async = inspect.iscoroutinefunction(cls.__init__)
    sig = inspect.getfullargspec(cls.__init__)

    # preserve original initializations
    cls.__new_original__ = cls.__new__
    cls.__init_original__ = cls.__init__
    cls.__it__ = None
    cls._rlock_ = RLock()

    # create a new "new" which usually just returns
    # __it__, the single instance (the first time, it creates
    # and returns __it__)

    if sig == (['self'], None, None, None, [], None, {}) :
        print("Not Permitting initialization", file=sys.stderr)
        # The ideal case -- singletons should not need parameters
        @functools.wraps(cls.__new__)
        def _singleton_new(cls):
            it = None
            # lock before we get __it__, so we don't create multiple times
            # use RLock to miminize chance of deadlock if locking occurs
            # in original __new__ and/or __init
            with cls._rlock_:
                it = cls.__dict__.get("__it__")
                if it is None:
                    cls.__it__ = it = cls.__new_original__(cls)
                    cls.__init_original__(it)
                    # keep lock until __it__ is initialized
            return it

        # and a new init which does nothing (more)
        def _singleton_init(self):
            return

    else:
        print("Permitting initialization", file=sys.stderr)
        # Well, if you must -- we initialize from parameters the first time
        @functools.wraps(cls.__init__)
        def _singleton_new(cls, *args, **kw):
            if (len(args) + len(kw)) > 0:
                print(singleton_warning, file=sys.stderr)
            it = None
            # lock before we get __it__, so we don't create multiple times
            # use RLock to miminize chance of deadlock if locking occurs
            # in original __new__ and/or __init
            with cls._rlock_:
                it = cls.__dict__.get("__it__")
                if it is None:
                    cls.__it__ = it = cls.__new_original__(cls)
                    cls.__init_original__(it, *args, **kw)
                    # keep lock until __it__ is initialized
            return it

        # and a new init which does nothing (more)
        @functools.wraps(cls.__init__)
        def _singleton_init(self, *args, **kw):
            return

    # and copy operations that don't
    def _singleton_copy(self):
        return cls.__it__

    def _singleton_deepcopy(self, memo):
        return cls.__it__

    # Change new to the new one
    cls.__new__ = _singleton_new # type:ignore
    cls.__init__ = _singleton_init # type:ignore
    cls.__copy__ = _singleton_copy
    cls.__deepcopy__ = _singleton_deepcopy

    return cls
