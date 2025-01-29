import matplotlib.pyplot as plt
import os

from instruments import TucsenCamera
from interface import Interface

class DummyInterface:
    def __init__(self, simulate=True):
        self.simulate = simulate
        self.scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.transientDir = os.path.join(self.scriptDir, 'transient')

def test_camera():
    interface = DummyInterface(simulate=True)
    camera = TucsenCamera(interface)
    camera.connect()
    camera.refresh_camera()
    breakpoint()
    data = camera.acquire_one_frame()
    # camera.disconnect()
    return data

def plot_data(data):
    breakpoint()
    plt.show()


if __name__ == '__main__':
    # test_camera()
    breakpoint()