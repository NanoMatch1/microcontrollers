
import unittest
from commands import MicroscopeCommand, CameraCommand, SpectrometerCommand, StageCommand, MonochromatorCommand
from dummy_microscope import DummyMicroscope

class TestMicroscopeCommand(unittest.TestCase):
    def setUp(self):
        self.cmd = MicroscopeCommand()

    def test_run_scan_spectrum(self):
        result = self.cmd('scan')

        if result is not True:
            standardMsg = 'Expected True from run_scan_spectrum(), but got {0}'.format(result)
            self.fail(self._formatMessage(None, standardMsg))

    def test_get_grating_position(self):
        # self.assertIsNone(self.cmd('get_grating_position'))
        self.assertIsInstance(self.cmd('get_grating_position'), int)

class TestCameraCommand(unittest.TestCase):
    def setUp(self):
        self.cmd = CameraCommand()

    def test_capture_frame(self):
        self.assertIsNone(self.cmd('capture'))

class TestSpectrometerCommand(unittest.TestCase):
    def setUp(self):
        self.cmd = SpectrometerCommand()

    def test_acquire_spectrum(self):
        self.assertIsNone(self.cmd('acquire'))

class TestStageCommand(unittest.TestCase):
    def setUp(self):
        self.cmd = StageCommand()

    def test_move_stage(self):
        self.assertIsNone(self.cmd('move'))

class TestMonochromatorCommand(unittest.TestCase):
    def setUp(self):
        self.cmd = MonochromatorCommand()

    def test_set_wavelength(self):
        self.assertIsNone(self.cmd('set_wavelength'))

class TestDummyMicroscope(unittest.TestCase):
    def setUp(self):
        self.microscope = DummyMicroscope()

    def test_integrity_checker(self):
        # Just checking no exceptions are raised
        self.assertIsNotNone(self.microscope)

if __name__ == '__main__':
    unittest.main()