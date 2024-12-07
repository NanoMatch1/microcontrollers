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

class Tucam():
    def __init__(self):
        self.scriptDir = os.path.dirname(os.path.abspath(__file__))
        self.TUCAMINIT = TUCAM_INIT(0, self.scriptDir.encode('utf-8'))
        self.TUCAMOPEN = TUCAM_OPEN(0, 0)
        TUCAM_Api_Init(pointer(self.TUCAMINIT), 5000)
        print(self.TUCAMINIT.uiCamCount)
        print(self.TUCAMINIT.pstrConfigPath)
        print('Connect %d camera' %self.TUCAMINIT.uiCamCount)

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
    def WaitForImageData(self):
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

        nTimes = 10
        for i in range(nTimes):
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
    
    def export_data(self, data, filename='default'):
        self.save_dir = os.path.join(self.scriptDir, 'data')
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        filepath = os.path.join(self.save_dir, filename)
        np.save(filepath, data)
        print('Data saved to %s' % filepath)

# def numpy_to_image(data):
#     import cv2
#     cv2.imshow('image', data)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
class Plotter:
    def __init__(self, dataDir=None):
        self.scriptDir = os.path.dirname(os.path.abspath(__file__))
        if dataDir is None:
            self.dataDir = os.path.join(self.scriptDir, 'data')
        else:
            self.dataDir = dataDir
        
    def load_data(self, filename):
        filepath = os.path.join(self.dataDir, filename)
        return np.load(filepath)
    
    def load_all_data(self, tag="tucsen_data"):
        dataDict = {}
        files = [file for file in os.listdir(self.dataDir) if tag in file]
        for filename in files:
            data = self.load_data(filename)
            dataDict[filename] = data
        return dataDict

    def plot_image(self, data):
        import matplotlib.pyplot as plt
        plt.imshow(data)
        plt.show()

def load_data(filepath):
    return np.load(filepath)

def plot_image(data: tuple):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(len(data), 1)
    for idx, spectrum in enumerate(data):
        ax[idx].imshow(spectrum)
    plt.show()



if __name__ == '__main__':
    def run_cam(set_ROI=(0, 0, 2048, 2048)):
        demo = Tucam()
        demo.OpenCamera(0)
        if demo.TUCAMOPEN.hIdxTUCam != 0:
            demo.SetROI(set_ROI=set_ROI)
            dataDict = demo.WaitForImageData()
            for key, value in dataDict.items():
                # plot_image(value)
                demo.export_data(value, filename='tucsen_data_{}.npy'.format(key))
            
            demo.CloseCamera()
        demo.UnInitApi()
    
    def plot_data():
        plotter = Plotter()
        dataDict = plotter.load_all_data()
        for key, value in dataDict.items():
            dataA = value[:, :, 0]
            dataB = value[:, :, 1]
            plot_image((dataA, dataB))
        
    run_cam(set_ROI=(0, 0, 2048, 2048))
    plot_data()