'''
    Test file
    Sine Wave, Sawtooth and Square
'''
import unittest
from numpy import arange
from rtmaii.analysis import frequency

class TestSuite(unittest.TestCase):
    '''
        Test Suite for the bands module.
    '''

    def setUp(self):
        """ Perform setup of initial parameters. """
        self.band_sum = 10000
        self.bands = 10230
        self.spectrum = arange(0, 100, 1) # Create 100 values increasing by 1 at each step.
        self.bands = {'0.1': 10, '0.2': 20, '0.3': 30, '1': 100} # key value where key == expected value after normalization.
        self.bands_sum = 100 # Sum to compare normalized values against.

    def test_noise_removal(self):
        """ Remove frequencies below amplitude of 11. Keep amplitudes above. """
        noiseless_spectrum = frequency.remove_noise(self.spectrum, 11)
        for i in range(10):
            self.assertEqual(noiseless_spectrum[i], 0)
        for i in range(11, len(self.spectrum)):
            self.assertNotEqual(noiseless_spectrum[i], 0)

    def test_normalization(self):
        """ Test that the values are normalized as expected. """
        normalized_dictionary = frequency.normalize_dict(self.bands, self.bands_sum)
        for key, value in normalized_dictionary.items():
            self.assertEqual(float(key), value)

    def test_band_power(self):
        """ Test that a given frequency range is summed correctly. """
        power = frequency.get_band_power(self.spectrum, {'full_range': [0, len(self.spectrum)]})
        self.assertEqual(power['full_range'], sum(self.spectrum))

    def test_frequency_bands(self):
        """ End-to-end test of retrieiving the presence of a frequency bands. """
        bands = frequency.frequency_bands(self.spectrum, {'full_range': [0, len(self.spectrum)]})
        self.assertEqual(bands['full_range'], 1)

