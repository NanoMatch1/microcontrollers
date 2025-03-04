#!/usr/bin/env python
# coding: utf-8
'''
Created on 2024-01-03
@author:fdy
'''

import ctypes
from ctypes import *
from TUCam import *
from enum import Enum
import time
import numpy as np
import os
import threading

class Tucam:
    def __init__(self, Microscope=None):
        self.scriptDir = os.path.dirname(os.path.abspath(__file__))
        self.microscope = Microscope
        self.transientDir = self.microscope.transientDir if self.microscope else self.scriptDir
        self.TUCAMINIT = TUCAM_INIT(0, self.scriptDir.encode('utf-8'))
        self.TUCAMOPEN = TUCAM_OPEN(0, 0)
        self.handle = self.TUCAMOPEN.hIdxTUCam
        TUCAM_Api_Init(pointer(self.TUCAMINIT), 5000)
        self.camera_lock = threading.Lock()
        self.stop_flag = threading.Event()
        self.is_running = False

    def acquire_one_frame(self):
        self.OpenCamera(0)
        self.SetROI()
        self.SetExposure(200)
        dataDict = self.WaitForImageData(nframes=1)
        self.CloseCamera()
        return dataDict[0] if dataDict else None

    def continuous_acquisition(self):
        self.stop_flag.clear()
        self.OpenCamera(0)
        self.SetROI()
        self.SetExposure(200)
        self.write_dir = self.transientDir

        while not self.stop_flag.is_set():
            try:
                with self.camera_lock:
                    dataDict = self.WaitForImageData(nframes=1)
                if not dataDict:
                    continue
                data = dataDict[0]
                np.save(os.path.join(self.transientDir, "transient_data.npy"), data)
                time.sleep(0.001)
            except Exception as e:
                print(f"Acquisition error: {e}")
                break

        self.CloseCamera()

    def start_continuous_acquisition(self):
        acq_thread = threading.Thread(target=self.continuous_acquisition)
        acq_thread.daemon = True
        acq_thread.start()
        print("Started continuous acquisition.")
        self.is_running = True

    def stop_continuous_acquisition(self):
        print("Stopping continuous acquisition.")
        self.stop_flag.set()
        self.is_running = False

    def OpenCamera(self, Idx):

        if  Idx >= self.TUCAMINIT.uiCamCount:
            return

        self.TUCAMOPEN = TUCAM_OPEN(Idx, 0)

        # ch:打开相机Idx | en:Open camera Idx
        TUCAM_Dev_Open(pointer(self.TUCAMOPEN))

        if 0 == self.TUCAMOPEN.hIdxTUCam:
            print('Open the camera failure!')
            return
        else:
            print('Open the camera success!')

    def CloseCamera(self):
        # ch:关闭相机 | en:Close camera
        if 0 != self.TUCAMOPEN.hIdxTUCam:
            TUCAM_Dev_Close(self.TUCAMOPEN.hIdxTUCam)
        print('Close the camera success')

    def UnInitApi(self):
        # ch:反初始化相机 | en:Uninitial Cameras
        TUCAM_Api_Uninit()

    def SetROI(self, set_ROI=(0, 0, 2048, 2048)):
        if len(set_ROI) != 4:
            print('ROI must be a tuple of 4 elements, (HOffset, VOffset, Width, Height)')
            return
        roi = TUCAM_ROI_ATTR()
        roi.bEnable  = 1
        roi.nHOffset = set_ROI[0]
        roi.nVOffset = set_ROI[1]
        roi.nWidth   = set_ROI[2]
        roi.nHeight  = set_ROI[3]

        try:
            # ch:设置相机感兴趣区域 | en:Set ROI
           TUCAM_Cap_SetROI(self.TUCAMOPEN.hIdxTUCam, roi)
           print('Set ROI state success, HOffset:%#d, VOffset:%#d, Width:%#d, Height:%#d'%(roi.nHOffset,
                    roi.nVOffset, roi.nWidth, roi.nHeight))
        except Exception:
            print('Set ROI state failure, HOffset:%#d, VOffset:%#d, Width:%#d, Height:%#d' % (roi.nHOffset,
                    roi.nVOffset, roi.nWidth,roi.nHeight))

    def convert_to_numpy(self, m_frame):
        # Convert buffer to list
        buffer = ctypes.cast(m_frame.pBuffer, ctypes.POINTER(ctypes.c_ubyte))
        buffer_list = list(buffer[:m_frame.uiImgSize])
        # Create numpy array from buffer list
        np_array = np.array(buffer_list, dtype=np.uint8)
        # Reshape array to match image dimensions
        np_array = np_array.reshape((m_frame.usHeight, m_frame.usWidth, m_frame.ucElemBytes))
        return np_array
        # return buffer_list

    # ch:获取相机数据流 | en:Get camera stream
    def WaitForImageData(self, nframes=10):
        dataDict = {}
        m_frame = TUCAM_FRAME()
        m_format = TUIMG_FORMATS
        m_frformat = TUFRM_FORMATS
        m_capmode = TUCAM_CAPTURE_MODES

        m_frame.pBuffer = 0;
        m_frame.ucFormatGet = m_frformat.TUFRM_FMT_USUAl.value
        m_frame.uiRsdSize = 1

        TUCAM_Buf_Alloc(self.TUCAMOPEN.hIdxTUCam, pointer(m_frame))
        TUCAM_Cap_Start(self.TUCAMOPEN.hIdxTUCam, m_capmode.TUCCM_SEQUENCE.value)

        for i in range(nframes):
            try:
                result = TUCAM_Buf_WaitForFrame(self.TUCAMOPEN.hIdxTUCam, pointer(m_frame), 1000)

                # print("Buffer as list:", buffer_list)
                print(
                    "Grab the frame success, index number is %#d, width:%d, height:%#d, channel:%#d, elembytes:%#d, image size:%#d"%(i, m_frame.usWidth, m_frame.usHeight, m_frame.ucChannels,
                    m_frame.ucElemBytes, m_frame.uiImgSize)
                    )
            except Exception:
                print('Grab the frame failure, index number is %#d',  i)
                continue
                # Convert buffer to list
            # buffer = ctypes.cast(m_frame.pBuffer, ctypes.POINTER(ctypes.c_ubyte))
            try:
                data = self.convert_to_numpy(m_frame)
            # dataDict[i] = data
            # buffer_list = list(buffer[:m_frame.uiImgSize])
                dataDict[i] = data
            except Exception as e:
                print(e)
                print('Convert to numpy failed')
                continue

        TUCAM_Buf_AbortWait(self.TUCAMOPEN.hIdxTUCam)
        TUCAM_Cap_Stop(self.TUCAMOPEN.hIdxTUCam)
        TUCAM_Buf_Release(self.TUCAMOPEN.hIdxTUCam)

        return dataDict
    
    def export_data(self, data, filename='default', spectrum=False):
        self.save_dir = os.path.join(self.scriptDir, 'data')
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
            # plt.plot(data[:, 0], data[:, 1])
        filepath = os.path.join(self.save_dir, filename)
        np.save(filepath, data)
        print('Data saved to %s' % filepath)

    def SetExposure(self, value):

        TUCAM_Capa_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDCAPA.TUIDC_ATEXPOSURE.value, 0)
        TUCAM_Prop_SetValue(self.TUCAMOPEN.hIdxTUCam, TUCAM_IDPROP.TUIDP_EXPOSURETM.value, value, 0);
        print("Set exposure:", value)
        # self.ShowAverageGray()

    def get_camera_info(self):
        from TUCam import get_camera_gain_attributes

        gain = get_camera_gain_attributes(self.handle)
        print(gain)
        self.gain = gain
# def numpy_to_image(data):
#     import cv2
#     cv2.imshow('image', data)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
class Plotter:
    # import os


    def __init__(self, dataDir=None):
        # import matplotlib.pyplot as plt
        self.scriptDir = os.path.dirname(os.path.abspath(__file__))
        if dataDir is None:
            self.dataDir = os.path.join(self.scriptDir, 'data')
        else:
            self.dataDir = dataDir

        self.dataDict = self.load_all_data()
        
    def load_data(self, filename):
        filepath = os.path.join(self.dataDir, filename)
        return np.load(filepath)
    
    def load_all_data(self, tag="tucsen_data"):
        dataDict = {}
        # files = [file for file in os.listdir(self.dataDir) if tag in file]
        files = [file for file in os.listdir(self.dataDir)]

        for filename in files:
            # breakpoint()
            filepath = os.path.join(self.dataDir, filename)
            try:
                if filename.endswith('.npy'):
                    data = self.load_data(filepath)
                    data = data.astype(float)
                elif filename.endswith('.tif'):
                    data = self.load_tif_as_numpy(filepath)
                else:
                    print('File format not supported {}'.format(filename))
                    continue
                dataDict[filename] = data
                print('Data loaded from {}'.format(filename))
            except Exception as e:
                print(e)
                print('Failed to load data from {}'.format(filename))
        return dataDict
    
    def load_tif_as_numpy(self, filepath):
        from PIL import Image
        with Image.open(filepath) as img:
            np_array = np.array(img)
        return np_array
    
    def plot_images(self):
        for key, value in self.dataDict.items():
            if value.ndim == 3:
                plot_image_SDK(value, filename=key)
            elif value.ndim == 2:
                plot_image_tucsen(value, filename=key)

    def crop_data(self, crop_range=None):
        newDict = {}
        for key, value in self.dataDict.items():
            if crop_range is None:
                crop_range = (2, len(value[:, 0]) - 2) # Crop the first and last 2 pixels
            if key.endswith('.npy'):
                data = value[crop_range[0]:crop_range[1], :, :]
            elif key.endswith('.tif'):
                data = value[crop_range[0]:crop_range[1], :]

            newDict[key] = data
        self.dataDict = newDict
        return newDict


    def plot_spectrum(self, data, binSize=2):
        import matplotlib.pyplot as plt

        dataY = np.sum(data, axis=0)
        if binSize > 1:
            dataY = np.add.reduceat(dataY, np.arange(0, dataY.size, binSize)) 
        # breakpoint()
        # dataY = np.sum(data, axis=0)
        dataX = np.arange(dataY.size)
        # dataX = np.arange(len(data[0, :]))
        # dataY = data[100, :]
        # dataX = np.arange(data.size)
        # dataY = data
        # breakpoint()
        
        plt.plot(dataX, dataY, label='')
        # plt.show()

    def plot_all_spectra(self, binSize=1, offset=0):
        import matplotlib.pyplot as plt
        for idx, (key, value) in enumerate(self.dataDict.items()):
            # self.plot_spectrum(value, binSize=binSize)
            if len(value.shape) > 1:
                dataX = value[:, 0]
                dataY = value[:, 1] + (offset*idx)
            
            else:
                dataX = np.arange(len(value))
                dataY = value
            # breakpoint()
            plt.plot(dataX, dataY, label=key)
            plt.legend()
        plt.show()

    def normalise_all_data(self, norm_range=None):
        '''Normalise the data from 0 to 1 within the x axis range'''
        newDict = {}
        for key, spectrum in self.dataDict.items():
            dataX = np.arange(len(spectrum))
            if norm_range is None:
                norm_range = (np.min(dataX), np.max(dataX))
            norm_spectrum = (spectrum - np.min(spectrum[norm_range[0]:norm_range[1]])) / np.ptp(spectrum[norm_range[0]:norm_range[1]])
            newDict[key] = norm_spectrum
        self.dataDict = newDict
        return newDict
        

            

    def take_second(self):
        newDict = {}
        for key, value in self.dataDict.items():
            if len(value.shape) < 3:
                print('Data has only one frame')
                data = value
            else:
                data = value[:, :, 1]
            newDict[key] = data
        self.dataDict = newDict
        return newDict
    
    def frames_to_spectrum(self):
        newDict = {}
        for key, value in self.dataDict.items():
            data = np.sum(value, axis=0)
            newDict[key] = data
        self.dataDict = newDict
        return newDict
    
    def save_all_data(self):
        for key, value in self.dataDict.items():
            filepath = os.path.join(self.dataDir, 'export', key)
            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))
            np.save(filepath, value)
            print('Data saved to {}'.format(filepath))
    
    
    
    # def plot_spectra(self):
    #     for key, value in self.dataDict.items():
    #         dataA = value[:, :, 0]
    #         dataB = value[:, :, 1]
            # plot_image((dataA, dataB))



    # def plot_image(self, data):
    #     import matplotlib.pyplot as plt
    #     plt.imshow(data)
    #     plt.show()

def load_data(filepath):
    return np.load(filepath)

def plot_image_SDK(data: tuple, filename='default'):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(len(data[0, 0, :]), 1)
    for idx, _ in enumerate(data[0, 0, :]):
        # breakpoint()
        spectrum = data[:, :, idx]
        ax[idx].imshow(spectrum)
        ax[idx].set_title(filename)
    plt.show()

def plot_image_tucsen(data: np.ndarray, filename='default'):
    import matplotlib.pyplot as plt
    plt.imshow(data)
    plt.title(filename)
    plt.show()

def plot_spectrum(data):
    import matplotlib.pyplot as plt
    plt.plot(data)
    plt.show()


def refresh_camera():
    print("refreshing camera")
    demo = Tucam()
    demo.OpenCamera(0)
    # demo.get_camera_info()
    demo.CloseCamera()
    demo.UnInitApi()

if __name__ == '__main__':
    def run_cam(set_ROI=(0, 0, 2048, 2048)):
        demo = Tucam()
        demo.OpenCamera(0)
        # demo.get_camera_info()
        # breakpoint()
        if demo.TUCAMOPEN.hIdxTUCam != 0:
            demo.SetROI(set_ROI=set_ROI)
            demo.SetExposure(500)
            dataDict = demo.WaitForImageData()
            for key, value in dataDict.items():
                # plot_image(value)
                demo.export_data(value, filename='tucsen_data_{}.npy'.format(key))
            
            demo.CloseCamera()
        demo.UnInitApi()
    
    def plot_data():
        plotter = Plotter()
        # dataDict = plotter.load_all_data()
        for key, value in plotter.dataDict.items():
            dataA = value[:, :, 0]
            dataB = value[:, :, 1]
            plot_image((dataA, dataB))
        
    refresh_camera()
    run_cam(set_ROI=(0, 1100, 2048, 400))
    # plot_data()