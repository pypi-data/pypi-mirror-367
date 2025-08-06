import unittest
import sys
from singleton_decorator1 import singleton, __version__
from threading import Lock, RLock, Thread
from copy import deepcopy, copy
import asyncio
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
    C1_init_count = 0
    C2_init_count = 0
    C3_init_count = 0
    C4_init_count = 0
    C5_init_count = 0
    C10_init_count = 0
    saved_C = None
    saved_C1 = None
    saved_C2 = None
    saved_C3 = None
    basic_refcount = 0
    list_C10: list[tuple[datetime, any, datetime]] = []
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

    class C1(C) :
        """
        This is C1's description
        C1 should be singleton too? (yes, but different)
        """
        def __init__(self):
            super().__init__()
            self.my_var = TestSingletonClass.C_init_count

    @singleton
    class C2 :
        """
        C2's description
        """
        def __init__(self, a) :
            self.my_var = a

        def f(self):
            return (TestSingletonClass.C_init_count, sys.getrefcount(self))

    @singleton
    class C3 :
        """
        C3's description
        """
        def __init__(self, a=3) :
            self.my_var = a

        def f(self):
            return (TestSingletonClass.C_init_count, sys.getrefcount(self))

    @singleton
    class C4 :
        """
        C4's description
        """
        def __init__(self, a=4) :
            self.my_var = a

        def f(self):
            return (TestSingletonClass.C_init_count, sys.getrefcount(self))

    class C10:
        """
        This is class C10's description
        """

        lock = RLock()

        def __init__(self):
            with TestSingletonClass.C10.lock:
                sleep(0.5)  # to have a chance to start at "same" time
                TestSingletonClass.C10_init_count += 1

#        async def ____(self):
#            return await TestSingletonClass.C10.lock

        @staticmethod
        def make():
            t1 = datetime.now()
            c1 = TestSingletonClass.C10()
            t2 = datetime.now()
            with TestSingletonClass.lock:
                TestSingletonClass.list_C10.append((t1, c1, t2))

        def f(self):
            return (TestSingletonClass.C10_init_count, sys.getrefcount(self))

    def test_01_initial_state(self):
        # @singleton creates (the only) instance for the first instantiation
        # (which hasn't happened yet, because the tests go in numeric order!)
        self.assertEqual(__version__, "0.5.6")
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

    def test_07_inheritance(self):
        c8 = TestSingletonClass.C1()
        c9 = TestSingletonClass.C1()
        self.assertFalse(c8 is TestSingletonClass.saved_C)
        self.assertTrue(c8 is c9)  
        self.assertEqual(c8.f(), (2, TestSingletonClass.basic_refcount + 1))
        self.assertEqual(c9.f(), (2, TestSingletonClass.basic_refcount + 1))
        
    def test_08_only_classes(self):
        with self.assertRaises(ValueError) as context:
            @singleton
            def fn(a:int) -> int:
                return a + 1
        self.assertEqual("@singleton should decorate a class declaration", str(context.exception))

    def test_09_arguments(self):
        c10 = TestSingletonClass.C2(1)
        c11 = TestSingletonClass.C2(2)
        self.assertTrue(c10 is c11)  
        self.assertEqual(c11.my_var, 1)
        
    def test_10_arguments(self):
        c12 = TestSingletonClass.C3()
        c13 = TestSingletonClass.C3(5)
        self.assertTrue(c12 is c13)  
        self.assertEqual(c13.my_var, 3)
        
    def test_11_arguments(self):
        c14 = TestSingletonClass.C4(5)
        c15 = TestSingletonClass.C4()
        self.assertTrue(c14 is c15)  
        self.assertEqual(c15.my_var, 5)
        
    # def test_19_async(self) :
    #     TestSingletonClass.list_C10 = []
    #     asyncio.gather([TestSingletonClass.C10.make(),
    #                     TestSingletonClass.C10.make()])
    #     self.assertEqual(len(TestSingletonClass.list_C10), 2)
    #     c1_t1, c1, c1_t2 = TestSingletonClass.list_C10[0]
    #     c2_t1, c2, c2_t2 = TestSingletonClass.list_C10[1]
    #     TestSingletonClass.list_C10 = []
    #     self.assertEqual(type(c1), TestSingletonClass.C10)
    #     self.assertTrue(isinstance(c1, TestSingletonClass.C10))

    # def test_20_instantiation(self):
    #     TestSingletonClass.list_C10 = []
    #     thread1 = Thread(target=TestSingletonClass.C10.make())
    #     thread2 = Thread(target=TestSingletonClass.C10.make())
    #     thread1.start()
    #     thread2.start()
    #     thread2.join()
    #     thread1.join()
    #     self.assertEqual(len(TestSingletonClass.list_C10), 2)
    #     c1_t1, c1, c1_t2 = TestSingletonClass.list_C10[0]
    #     c2_t1, c2, c2_t2 = TestSingletonClass.list_C10[1]
    #     TestSingletonClass.list_C10 = []
    #     self.assertEqual(type(c1), TestSingletonClass.C10)
    #     self.assertTrue(isinstance(c1, TestSingletonClass.C10))
    #     self.assertEqual(c1.f(), (1, TestSingletonClass.basic_refcount + 1))
    #     self.assertEqual(c2.f(), (1, TestSingletonClass.basic_refcount + 1))
    #     self.assertTrue((c1_t2 - c1_t1) > (c2_t2 - c2_t1))
    #     # and verify that c1 and c2 are the same object
    #     self.assertTrue(c1 is c2)



if __name__ == "__main__":
    unittest.main()
