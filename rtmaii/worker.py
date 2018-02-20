import threading
from queue import Queue
from rtmaii.analysis import frequency, pitch, key, spectral, spectrogram
from pydispatch import dispatcher
from numpy import arange, mean, int16, resize

class Worker(threading.Thread):
    """ Base worker class, responsible for initializing shared attributes.

        **Attributes**:
            - `queue`: queue of data to be processed by a worker.
            - `channel_id`: id of channel being analysed.
    """
    def __init__(self, channel_id: int):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.channel_id = channel_id
        self.setDaemon(True)
        self.queue = Queue()
        self.start()

    def run(self):
        raise NotImplementedError("Run should be implemented")

class PitchWorker(Worker):
    """ Specialised worker that has a method to analyse the key given the pitch. """
    def __init__(self, channel_id: int):
        Worker.__init__(self, args=(), kwargs=None)

    def analyse_key(self, pitch):
        estimated_key = key.note_from_pitch(pitch)
        dispatcher.send(signal='key', sender=self.channel_id, data=estimated_key)

class BandsWorker(Worker):
    """ Worker responsible for analysing interesting frequency bands.

        **Args**:
            - `bands_of_interest`: dictionary of frequency bands to analyse.
            - `channel_id`: id of channel being analysed.
    """
    def __init__(self, bands_of_interest: dict, channel_id: int):
        Worker.__init__(self, channel_id)
        self.bands_of_interest = bands_of_interest

    def run(self):
        while True:
            spectrum = self.queue.get()
            frequency_bands = frequency.frequency_bands(abs(spectrum), self.bands_of_interest)
            dispatcher.send(signal='bands', sender=self.channel_id, data=frequency_bands) #TODO: Move to a locator.

class ZeroCrossingWorker(PitchWorker):
    """ Worker responsible for analysing the fundamental pitch using the zero-crossings method.

        **Args**:
            - `sampling_rate`: sampling_rate of source being analysed.
            - `channel_id`: id of channel being analysed.
    """
    def __init__(self, sampling_rate: int, channel_id: int):
        Worker.__init__(self, channel_id)
        self.sampling_rate = sampling_rate

    def run(self):
        while True:
            signal = self.queue.get()
            estimated_pitch = pitch.pitch_from_zero_crossings(signal, self.sampling_rate)
            dispatcher.send(signal='pitch', sender=self.channel_id, data=estimated_pitch)
            self.analyse_key(estimated_pitch)

class AutoCorrelationWorker(PitchWorker):
    """ Worker responsible for analysing the fundamental pitch using the auto-corellation method.

        **Args**:
            - `sampling_rate`: sampling_rate of source being analysed.
            - `channel_id`: id of channel being analysed.
    """
    def __init__(self, sampling_rate: int, channel_id: int):
        Worker.__init__(self, channel_id)
        self.sampling_rate = sampling_rate

    def run(self):
        while True:
            signal = self.queue.get()
            convolved_spectrum = spectral.convolve_spectrum(signal)
            estimated_pitch = pitch.pitch_from_auto_correlation(convolved_spectrum, self.sampling_rate)
            dispatcher.send(signal='pitch', sender=self.channel_id, data=estimated_pitch)
            print(estimated_pitch)
            self.analyse_key(estimated_pitch)

class HPSWorker(PitchWorker):
    """ Worker responsible for analysing the fundamental pitch using the harmonic-product-spectrum method.

        **Args**:
            - `sampling_rate`: sampling_rate of source being analysed.
            - `channel_id`: id of channel being analysed.
    """
    def __init__(self, sampling_rate: int, channel_id: int):
        Worker.__init__(self, channel_id)
        self.sampling_rate = sampling_rate

    def run(self):
        while True:
            spectrum = self.queue.get()
            estimated_pitch = pitch.pitch_from_hps(spectrum, self.sampling_rate, 7)
            dispatcher.send(signal='pitch', sender=self.channel_id, data=estimated_pitch)
            self.analyse_key(estimated_pitch)

class FFTWorker(PitchWorker):
    """ Worker responsible for analysing the fundamental pitch using the FFT method.

        **Args**:
            - `sampling_rate`: sampling_rate of source being analysed.
            - `channel_id`: id of channel being analysed.
    """
    def __init__(self, sampling_rate: int, channel_id: int):
        Worker.__init__(self, channel_id)
        self.sampling_rate = sampling_rate

    def run(self):
        while True:
            spectrum = self.queue.get()
            estimated_pitch = pitch.pitch_from_fft(spectrum, self.sampling_rate)
            dispatcher.send(signal='pitch', sender=self.channel_id, data=estimated_pitch)
            self.analyse_key(estimated_pitch)