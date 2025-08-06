import unittest
import sys
from singleton_decorator1 import singleton
from threading import Lock, RLock, Thread
from copy import deepcopy, copy
from time import sleep
from datetime import datetime
import gc

if sys.version_info < (3, 10):
    from typing import List as list
    from typing import Tuple as tuple

from typing import Any as any
from typing import TYPE_CHECKING


class TestSingletonClass(unittest.TestCase):
    C_init_count = 0
    C2_init_count = 0
    C3_init_count = 0
    saved_C = None
    saved_C2 = None
    saved_C3 = None
    basic_refcount = 0
    list_C2: list[tuple[datetime, any, datetime]] = []
    list_C3: list[tuple[datetime, any, datetime]] = []
    lock = RLock()

    @singleton
    class C:
        """
        This is class C's description
        """

        def __init__(self):
            TestSingletonClass.C_init_count += 1

        def f(self):
            return (TestSingletonClass.C_init_count, sys.getrefcount(self))

    @singleton
    class C2:
        """
        This is class C2's description
        """

        lock = RLock()

        def __init__(self):
            with TestSingletonClass.C2.lock:
                sleep(0.5)  # to have a chance to start at "same" time
                TestSingletonClass.C2_init_count += 1

        @staticmethod
        def make():
            t1 = datetime.now()
            c1 = TestSingletonClass.C2()
            t2 = datetime.now()
            with TestSingletonClass.lock:
                TestSingletonClass.list_C2.append((t1, c1, t2))

        def f(self):
            return (TestSingletonClass.C2_init_count, sys.getrefcount(self))

    @singleton
    class C3:
        lock = Lock()

        def __init__(self):
            with TestSingletonClass.C3.lock:
                sleep(0.5)  # to have a chance to start at "same" time
                TestSingletonClass.C3_init_count += 1

        @staticmethod
        def make():
            t1 = datetime.now()
            c1 = TestSingletonClass.C3()
            t2 = datetime.now()
            with TestSingletonClass.lock:
                TestSingletonClass.list_C3.append((t1, c1, t2))

        def f(self):
            return (TestSingletonClass.C3_init_count, sys.getrefcount(self))

    def test_01_initial_state(self):
        # @singleton creates (the only) instance for the first instantiation
        # (which hasn't happened yet, because the tests go in numeric order!)
        self.assertEqual(TestSingletonClass.C_init_count, 0)
        # __it__ exists, but the refcount is undefined at this point
        # Also, mypy hates checking C.__it__, since it was added outside
        #   the class definition
        # self.assertEqual(sys.getrefcount(TestSingletonClass.C.__it__), 0)

    def test_02_instantiation(self):
        c1 = TestSingletonClass.C()
        self.assertTrue(isinstance(c1, TestSingletonClass.C))
        # references below are C.__it__, c1, and the function argument, ???
        TestSingletonClass.basic_refcount = c1.f()[1]  # varies w/ python versions
        self.assertEqual(c1.f(), (1, TestSingletonClass.basic_refcount))
        c2 = TestSingletonClass.C()
        # basic, +1 for c1
        self.assertEqual(c1.f(), (1, TestSingletonClass.basic_refcount + 1))
        # and verify that c1 and c2 are the same object
        self.assertTrue(c1 is c2)

    def test_03_out_of_scope(self):
        # ... now c1 and c2 are out of scope, so back to 4 references
        TestSingletonClass.saved_C = TestSingletonClass.C()
        self.assertEqual(TestSingletonClass.saved_C.f(), (1, TestSingletonClass.basic_refcount))

    def test_04_new(self):
        # verify that forcing __new__ will not actually create a new instance
        c3 = TestSingletonClass.C.__new__(TestSingletonClass.C)
        # now we also have saved_C in the count (from test 3)
        self.assertEqual(c3.f(), (1, TestSingletonClass.basic_refcount + 1))
        self.assertTrue(c3 is TestSingletonClass.saved_C)

    def test_05_init(self):
        # verify that forcing __init__ will not actually re __init__()
        c4 = TestSingletonClass.C()
        TestSingletonClass.C.__init__(c4)
        self.assertEqual(c4.f(), (1, TestSingletonClass.basic_refcount + 1))

    def test_06_copy(self):
        # verify that copying doesn't really copy
        c5 = TestSingletonClass.C()
        c6 = deepcopy(c5)
        c7 = copy(c5)
        self.assertEqual(c5.f(), (1, TestSingletonClass.basic_refcount + 3))
        self.assertEqual(c6.f(), (1, TestSingletonClass.basic_refcount + 3))
        self.assertEqual(c7.f(), (1, TestSingletonClass.basic_refcount + 3))
        self.assertTrue(c5 is c6)
        self.assertTrue(c5 is c7)

    def test_07_initial_state(self):
        # @singleton creates (the only) instance for the first instantiation
        # (which hasn't happened yet, because the tests go in numeric order!)
        self.assertEqual(TestSingletonClass.C2_init_count, 0)
        # __it__ exists, but the refcount is undefined at this point
        # Also, mypy hates checking C2.__it__, since it was added outside
        #   the class definition
        # self.assertEqual(sys.getrefcount(TestSingletonClass.C2.__it__), 0)

    def test_08_instantiation(self):
        TestSingletonClass.list_C2 = []
        thread1 = Thread(target=TestSingletonClass.C2.make())
        thread2 = Thread(target=TestSingletonClass.C2.make())
        thread1.start()
        thread2.start()
        thread2.join()
        thread1.join()
        self.assertEqual(len(TestSingletonClass.list_C2), 2)
        c1_t1, c1, c1_t2 = TestSingletonClass.list_C2[0]
        c2_t1, c2, c2_t2 = TestSingletonClass.list_C2[1]
        TestSingletonClass.list_C2 = []
        self.assertEqual(type(c1), TestSingletonClass.C2)
        self.assertTrue(isinstance(c1, TestSingletonClass.C2))
        self.assertEqual(c1.f(), (1, TestSingletonClass.basic_refcount + 1))
        self.assertEqual(c2.f(), (1, TestSingletonClass.basic_refcount + 1))
        self.assertTrue((c1_t2 - c1_t1) > (c2_t2 - c2_t1))
        # and verify that c1 and c2 are the same object
        self.assertTrue(c1 is c2)

    def test_09_out_of_scope(self):
        # ... now c1 and c2 are out of scope, so back to 2 references
        TestSingletonClass.saved_C2 = TestSingletonClass.C2()
        self.assertEqual(TestSingletonClass.saved_C2.f(), (1, TestSingletonClass.basic_refcount))

    def test_10_new(self):
        # verify that forcing __new__ will not actually create a new instance
        c3 = TestSingletonClass.C2.__new__(TestSingletonClass.C2)
        # now we also have saved_C2 in the count (from test 3)
        self.assertEqual(c3.f(), (1, TestSingletonClass.basic_refcount + 1))
        self.assertTrue(c3 is TestSingletonClass.saved_C2)

    def test_11_init(self):
        # verify that forcing __init__ will not actually re __init__()
        c4 = TestSingletonClass.C2()
        TestSingletonClass.C2.__init__(c4)
        self.assertEqual(c4.f(), (1, TestSingletonClass.basic_refcount + 1))

    def test_12_copy(self):
        # verify that copying doesn't really copy
        c5 = TestSingletonClass.C2()
        c6 = deepcopy(c5)
        c7 = copy(c5)
        self.assertEqual(c5.f(), (1, TestSingletonClass.basic_refcount + 3))
        self.assertEqual(c6.f(), (1, TestSingletonClass.basic_refcount + 3))
        self.assertEqual(c7.f(), (1, TestSingletonClass.basic_refcount + 3))
        self.assertTrue(c5 is c6)
        self.assertTrue(c5 is c7)

    def test_13_initial_state(self):
        # @singleton creates (the only) instance for the first instantiation
        # (which hasn't happened yet, because the tests go in numeric order!)
        self.assertEqual(TestSingletonClass.C3_init_count, 0)
        # __it__ exists, but the refcount is undefined at this point
        # Also, mypy hates checking C3.__it__, since it was added outside
        #   the class definition
        # self.assertEqual(sys.getrefcount(TestSingletonClass.C3.__it__), 0)

    def test_14_instantiation(self):
        TestSingletonClass.list_C3 = []
        thread1 = Thread(target=TestSingletonClass.C3.make())
        thread2 = Thread(target=TestSingletonClass.C3.make())
        thread1.start()
        thread2.start()
        thread2.join()
        thread1.join()
        self.assertEqual(len(TestSingletonClass.list_C3), 2)
        c1_t1, c1, c1_t2 = TestSingletonClass.list_C3[0]
        c2_t1, c2, c2_t2 = TestSingletonClass.list_C3[1]
        TestSingletonClass.list_C3 = []
        self.assertEqual(type(c1), TestSingletonClass.C3)
        self.assertTrue(isinstance(c1, TestSingletonClass.C3))
        # ... 5 references below are C3.__it__, c1, c2,  and the function argument,
        # and implicit self for f()
        # self.assertEqual(c1.f(), (1, TestSingletonClass.basic_refcount + 1))
        # self.assertEqual(c2.f(), (1, TestSingletonClass.basic_refcount + 1))
        self.assertTrue((c1_t2 - c1_t1) > (c2_t2 - c2_t1))
        # and verify that c1 and c2 are the same object
        self.assertTrue(c1 is c2)

    def test_15_out_of_scope(self):
        # ... now c1 and c2 are out of scope, so back to 2 references
        TestSingletonClass.saved_C3 = TestSingletonClass.C3()
        self.assertEqual(TestSingletonClass.saved_C3.f(), (1, TestSingletonClass.basic_refcount))

    def test_16_new(self):
        # verify that forcing __new__ will not actually create a new instance
        c3 = TestSingletonClass.C3.__new__(TestSingletonClass.C3)
        # now we also have saved_C3 in the count (from test 3)
        self.assertEqual(c3.f(), (1, TestSingletonClass.basic_refcount + 1))
        self.assertTrue(c3 is TestSingletonClass.saved_C3)

    def test_17_init(self):
        # verify that forcing __init__ will not actually re __init__()
        c4 = TestSingletonClass.C3()
        TestSingletonClass.C3.__init__(c4)
        self.assertEqual(c4.f(), (1, TestSingletonClass.basic_refcount + 1))

    def test_18_copy(self):
        # verify that copying doesn't really copy
        c5 = TestSingletonClass.C3()
        c6 = deepcopy(c5)
        c7 = copy(c5)
        self.assertEqual(c5.f(), (1, TestSingletonClass.basic_refcount + 3))
        self.assertEqual(c6.f(), (1, TestSingletonClass.basic_refcount + 3))
        self.assertEqual(c7.f(), (1, TestSingletonClass.basic_refcount + 3))
        self.assertTrue(c5 is c6)
        self.assertTrue(c5 is c7)


if __name__ == "__main__":
    unittest.main()
