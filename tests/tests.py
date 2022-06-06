import unittest
import subprocess
import sys

sys.path.insert(0, '..')
from UltraDict import UltraDict

# Disable logging
if hasattr(UltraDict.log, 'disable'):
    UltraDict.log.disable(UltraDict.log.CRITICAL)
else:
    UltraDict.log.set_level(UltraDict.log.Levels.error)

class UltraDictTests(unittest.TestCase):

    def setUp(self):
        pass

    def exec(self, filepath):
        ret = subprocess.run([sys.executable, filepath],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ret.stdout = ret.stdout.replace(b'\r\n', b'\n');
        return ret

    def test_count(self):
        ultra = UltraDict()
        other = UltraDict(name=ultra.name)

        count = 100
        for i in range(count//2):
            ultra[i] = i

        for i in range(count//2, count):
            other[i] = i

        self.assertEqual(len(ultra), len(other))

    def test_huge_value(self):
        ultra = UltraDict()

        # One megabyte string
        self.assertEqual(ultra.full_dump_counter, 0)

        length = 1_000_000

        ultra['huge'] = ' ' * length

        self.assertEqual(ultra.full_dump_counter, 1)
        self.assertEqual(len(ultra.data['huge']), length)

        other = UltraDict(name=ultra.name)

        self.assertEqual(len(other.data['huge']), length)

    def test_parameter_passing(self):
        ultra = UltraDict(shared_lock=True, buffer_size=4096*8, full_dump_size=4096*8)
        # Connect `other` dict to `ultra` dict via `name`
        other = UltraDict(name=ultra.name)

        self.assertIsInstance(ultra.lock, ultra.SharedLock)
        self.assertIsInstance(other.lock, other.SharedLock)

        self.assertEqual(ultra.buffer_size, other.buffer_size)

    def test_iter(self):
        ultra = UltraDict()
        # Connect `other` dict to `ultra` dict via `name`
        other = UltraDict(name=ultra.name)

        ultra[1] = 1
        ultra[2] = 2

        counter = 0
        for i in other.items():
            counter += 1

        self.assertEqual(counter, 2)

        self.assertEqual(ultra.items(), other.items())


    def test_full_dump(self):
        # TODO
        pass

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux")
    def test_cleanup(self):
        # TODO
        import psutil
        p = psutil.Process()
        file_count = len(p.open_files())
        self.assertEqual(file_count, 0, "file handle count before before tests should be 0")
        ultra = UltraDict(nested={ 1: 1})
        file_count = len(p.open_files())
        self.assertEqual(file_count, 4, "file handle count with one simple UltraDict should be 4")
        del ultra
        file_count = len(p.open_files())
        self.assertEqual(file_count, 0, "file handle count after deleting the UltraDict should be 0 again")
        ultra = UltraDict(nested={ 1: 1}, recurse=True)
        file_count = len(p.open_files())
        self.assertEqual(file_count, 12, "nested file handle count should be 12")
        del ultra
        file_count = len(p.open_files())
        self.assertEqual(file_count, 0, "nested file handle count after deleting UltraDict should be 0 again")

    def test_example_simple(self):
        filename = "examples/simple.py"
        ret = self.exec(filename)
        self.assertEqual(ret.returncode, 0, f'Running {filename} did return with an error.')
        self.assertEqual(ret.stdout.splitlines()[-1], b"Length:  100000  ==  100000  ==  100000")

    def test_example_parallel(self):
        filename = "examples/parallel.py"
        ret = self.exec(filename)
        self.assertEqual(ret.returncode, 0, f'Running {filename} did return with an error.')
        self.assertEqual(ret.stdout.splitlines()[-1], b'Counter:  100000  ==  100000')

    def test_example_nested(self):
        filename = "examples/nested.py"
        ret = self.exec(filename)
        self.assertEqual(ret.returncode, 0, f'Running {filename} did return with an error.')
        self.assertEqual(ret.stdout.splitlines()[-1], b"{'nested': {'deeper': {0: 2}}}  ==  {'nested': {'deeper': {0: 2}}}")

    def test_example_recover_from_stale_lock(self):
        filename = "examples/recover_from_stale_lock.py"
        ret = self.exec(filename)
        self.assertEqual(ret.returncode, 0, f'Running {filename} did return with an error.')
        self.assertEqual(ret.stdout.splitlines()[-1], b"Counter: 100 == 100")

if __name__ == '__main__':
    unittest.main()
