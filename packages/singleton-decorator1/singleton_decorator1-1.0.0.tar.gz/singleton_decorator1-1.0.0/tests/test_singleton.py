#!/usr/bin/env python
import unittest
import asyncio
import sys
from threading import Lock as thread_Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy, copy
from datetime import datetime

from singleton_decorator1 import singleton

if sys.version_info < (3, 10):
    from typing import List as list
    from typing import Tuple as tuple

from typing import Any as any


def non_blocking_sleep(delay: float) -> None:
    ts = datetime.now()
    while (datetime.now() - ts).total_seconds() > delay:
        with open("file_to_read", "rb") as fp:
            fp.read()  # other threads can run
    return


class TestCls(unittest.TestCase):
    C_init_count = 0
    C1_init_count = 0
    C2_init_count = 0
    C3_init_count = 0
    C4_init_count = 0
    C5_init_count = 0
    saved_C = None
    basic_refcount = 0

    @singleton
    class C:
        """
        This is class C's description
        """

        def __init__(self):
            TestCls.C_init_count += 1

        def f(self):
            return (TestCls.C_init_count, sys.getrefcount(self))

    class C1(C):
        """
        This is C1's description
        C1 should be singleton too? (yes, but different)
        """

        def __init__(self):
            super().__init__()
            TestCls.C1_init_count += 1
            self.my_var = TestCls.C1_init_count

    @singleton
    class C2:
        """
        C2's description
        """

        def __init__(self, a):
            TestCls.C2_init_count += 1
            self.my_var = a

        def f(self):
            return (TestCls.C2_init_count, sys.getrefcount(self))

    @singleton
    class C3:
        """
        C3's description
        """

        def __init__(self, a=3):
            TestCls.C3_init_count += 1
            self.my_var = a

        def f(self):
            return (TestCls.C3_init_count, sys.getrefcount(self))

    @singleton
    class C4:
        """
        C4's description
        """

        def __init__(self, a=4):
            TestCls.C4_init_count += 1
            self.my_var = a

        def f(self):
            return (TestCls.C4_init_count, sys.getrefcount(self))

    @singleton
    class C5:
        """
        This is class C5's description:
        This is a test that actually has multithreading. If the IO is blocking
        (e.g. time.sleep), then there is no overlap in activity. The first
        thread runs until it is done, and then the second goes. As a result,
        the lock isn't really tested; If I used asyncio.sleep (see below), then
        I couldn't sleep in the __init__ or __new__ (which is C2 below).
        So instead I create a delay by waiting for time to pass while reading a
        large file. While I read the file, the other instance can run.
        """

        C5_create_lock = thread_Lock()
        C5_list_lock = thread_Lock()
        list_C5: list[tuple[datetime, any, datetime]] = []

        def __init__(self, a: int, delay: float):
            TestCls.C5_init_count += 1
            non_blocking_sleep(delay)
            self.a: int = a

        @classmethod
        def create(cls, delay1, delay2, a):
            t1 = datetime.now()
            non_blocking_sleep(delay1)
            c1 = cls(a, delay2)
            t2 = datetime.now()
            with cls.C5_list_lock:
                cls.list_C5.append((t1, c1, t2))
            return c1

        @classmethod
        def get_instance_list(cls):
            return cls.list_C5

        def f(self):
            return (TestCls.C5_init_count, sys.getrefcount(self))

    def test_01_initial_state(self):
        # @singleton creates (the only) instance for the first instantiation
        # (which hasn't happened yet, because the tests go in numeric order!)
        self.assertEqual(TestCls.C_init_count, 0)
        # __it__ exists, but the refcount is undefined at this point
        # Also, mypy hates checking C.__it__, since it was added outside
        #   the class definition
        # self.assertEqual(sys.getrefcount(TestCls.C.__it__), 0)

    def test_02_instantiation(self):
        c1 = TestCls.C()
        self.assertTrue(isinstance(c1, TestCls.C))
        # references below are C.__it__, c1, and the function argument, ???
        TestCls.basic_refcount = c1.f()[1]  # varies w/ python versions
        self.assertEqual(c1.f(), (1, TestCls.basic_refcount))
        c2 = TestCls.C()
        # basic, +1 for c1
        self.assertEqual(c1.f(), (1, TestCls.basic_refcount + 1))
        # and verify that c1 and c2 are the same object
        self.assertTrue(c1 is c2)

    def test_03_out_of_scope(self):
        # ... now c1 and c2 are out of scope, so back to 4 references
        TestCls.saved_C = TestCls.C()
        self.assertEqual(TestCls.saved_C.f(), (1, TestCls.basic_refcount))

    def test_04_new(self):
        # verify that forcing __new__ will not actually create a new instance
        c1 = TestCls.C.__new__(TestCls.C)
        # now we also have saved_C in the count (from test 3)
        self.assertEqual(c1.f(), (1, TestCls.basic_refcount + 1))
        self.assertTrue(c1 is TestCls.saved_C)

    def test_05_init(self):
        # verify that forcing __init__ will not actually re __init__()
        c1 = TestCls.C()
        TestCls.C.__init__(c1)
        self.assertEqual(c1.f(), (1, TestCls.basic_refcount + 1))

    def test_06_copy(self):
        # verify that copying doesn't really copy
        c1 = TestCls.C()
        c2 = deepcopy(c1)
        c3 = copy(c1)
        self.assertEqual(c1.f(), (1, TestCls.basic_refcount + 3))
        self.assertEqual(c2.f(), (1, TestCls.basic_refcount + 3))
        self.assertEqual(c3.f(), (1, TestCls.basic_refcount + 3))
        self.assertTrue(c1 is c2)
        self.assertTrue(c1 is c3)

    def test_07_inheritance(self):
        c1 = TestCls.C1()
        c2 = TestCls.C1()
        self.assertFalse(c1 is TestCls.saved_C)
        self.assertTrue(c1 is c2)
        self.assertEqual(c1.f(), (2, TestCls.basic_refcount + 1))
        self.assertEqual(c2.f(), (2, TestCls.basic_refcount + 1))

    def test_08_only_classes(self):
        with self.assertRaises(ValueError) as context:

            @singleton
            def fn(a: int) -> int:
                return a + 1

        self.assertEqual("@singleton should decorate a class declaration", str(context.exception))

    def test_09_arguments(self):
        c1 = TestCls.C2(1)
        c2 = TestCls.C2(5)
        self.assertTrue(c1 is c2)
        self.assertEqual(c2.my_var, 1)
        self.assertEqual(c1.f(), (1, TestCls.basic_refcount + 1))
        self.assertEqual(c2.f(), (1, TestCls.basic_refcount + 1))

    def test_10_arguments(self):
        c1 = TestCls.C3()
        c2 = TestCls.C3(5)
        self.assertTrue(c1 is c2)
        self.assertEqual(c2.my_var, 3)

    def test_11_arguments(self):
        c1 = TestCls.C4(5)
        c2 = TestCls.C4()
        self.assertTrue(c1 is c2)
        self.assertEqual(c2.my_var, 5)

    def test_12_multithread(self):
        t_start = datetime.now()
        attempts = range(2)
        results = {}
        with ThreadPoolExecutor(max_workers=10) as ex:
            attempt_map = {ex.submit(TestCls.C5.create, (50 + i) / 100, 0.50, i): i for i in attempts}
            for future in as_completed(attempt_map):
                i = attempt_map[future]
                results[i] = future.result()
        c1 = results[0]
        c2 = results[1]
        self.assertEqual(c1.a, 0)
        self.assertEqual(c2.a, 0)
        self.assertTrue(c1 is c2)
        inst_list = TestCls.C5.get_instance_list()
        self.assertTrue(inst_list[0][1] is c1)
        self.assertTrue(inst_list[1][1] is c2)
        self.assertTrue((inst_list[0][2] - t_start) < (inst_list[1][2] - t_start))
        # Verify the blocks ran in parallel
        #  print(f"{2*((inst_list[0][2]-t_start).total_seconds())} > {(inst_list[1][2]-t_start).total_seconds()}")
        self.assertTrue(1.8 * (inst_list[0][2] - t_start) > (inst_list[1][2] - t_start))


if sys.version_info >= (3, 10):

    class TestClsAsync(unittest.IsolatedAsyncioTestCase):
        C1_init_count = 0
        C2_init_count = 0

        class C1:
            """
            This is class C1's description: Not a singleton!
            Modelled roughly on what asyncio-redis does, as a realistic
            example of a class with async
            """

            C1_create_lock = asyncio.Lock()
            C1_list_lock = asyncio.Lock()
            list_C1: list[tuple[datetime, any, datetime]] = []

            def __init__(self, a, delay):
                TestClsAsync.C1_init_count += 1
                self.a = a
                non_blocking_sleep(delay)

            @classmethod
            async def create(cls, delay1, delay2, a):
                t1 = datetime.now()
                await asyncio.sleep(delay1)
                async with cls.C1_create_lock:
                    c1 = cls(a, delay2)
                t2 = datetime.now()
                async with cls.C1_list_lock:
                    cls.list_C1.append((t1, c1, t2))
                return c1

            @classmethod
            def get_instance_list(cls):
                return cls.list_C1

            def f(self):
                return (TestClsAsync.C1_init_count, sys.getrefcount(self))

        @singleton
        class C2:
            """
            This is class C2's description:
            Modelled roughly on what asyncio-redis does, as a realistic
            example of a class with async
            Note that since this is "correct" async code, no async functions
            happen in __new__ or __init__; they are ensured to be single
            access by the "create" class method.
            """

            C2_create_lock = asyncio.Lock()
            C2_list_lock = asyncio.Lock()
            list_C2: list[tuple[datetime, any, datetime]] = []

            def __init__(self, a, delay):
                TestClsAsync.C2_init_count += 1
                non_blocking_sleep(delay)
                self.a = a

            @classmethod
            async def create(cls, delay1, delay2, a):
                t1 = datetime.now()
                await asyncio.sleep(delay1)
                async with cls.C2_create_lock:
                    c1 = cls(a, delay2)
                t2 = datetime.now()
                async with cls.C2_list_lock:
                    cls.list_C2.append((t1, c1, t2))
                return c1

            @classmethod
            def get_instance_list(cls):
                return cls.list_C2

            def f(self):
                return (TestClsAsync.C2_init_count, sys.getrefcount(self))

        async def test_13_async(self):
            t_start = datetime.now()
            async with asyncio.TaskGroup() as tg:
                t1 = tg.create_task(TestClsAsync.C1.create(0.50, 0.50, 1))
                t2 = tg.create_task(TestClsAsync.C1.create(0.51, 0.50, 2))
            c2 = t2.result()
            c1 = t1.result()
            self.assertEqual(c1.a, 1)
            self.assertEqual(c2.a, 2)
            self.assertFalse(c1 is c2)
            inst_list = TestClsAsync.C1.get_instance_list()
            self.assertTrue(inst_list[0][1] is c1)
            self.assertTrue(inst_list[1][1] is c2)
            self.assertTrue((inst_list[0][2] - t_start) < (inst_list[1][2] - t_start))
            # Verify the blocks ran in parallel
            self.assertTrue(1.8 * (inst_list[0][2] - t_start) > (inst_list[1][2] - t_start))

        async def test_14_async_singleton(self):
            t_start = datetime.now()
            async with asyncio.TaskGroup() as tg:
                t1 = tg.create_task(TestClsAsync.C2.create(0.50, 0.50, 1))
                t2 = tg.create_task(TestClsAsync.C2.create(0.51, 0.50, 2))
            c2 = t2.result()
            c1 = t1.result()
            self.assertEqual(c1.a, 1)
            self.assertEqual(c2.a, 1)
            self.assertTrue(c1 is c2)
            inst_list = TestClsAsync.C2.get_instance_list()
            self.assertTrue(inst_list[0][1] is c1)
            self.assertTrue(inst_list[1][1] is c2)
            self.assertTrue((inst_list[0][2] - t_start) < (inst_list[1][2] - t_start))
            # Verify the blocks ran in parallel
            self.assertTrue(1.8 * (inst_list[0][2] - t_start) > (inst_list[1][2] - t_start))


if __name__ == "__main__":
    unittest.main()
