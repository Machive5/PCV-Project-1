import cv2
import include.shared as shared
import numpy as np

class ObjectDetection:
    def __init__(self,):
        self.ref_pos = shared.player_pos
        self.ROI_calib = [None, None, None, None]
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.mouse_pos = (None,None)
        self.cvt_color_code = None
        self.auto_threshold = False;
        return
    
    def autoThreshold(self):
        if self.frame is None or self.frame.size == 0:
            return False

        if all(value is not None for value in self.ROI_calib):
            roi = self.frame[
                self.ROI_calib[1]:self.ROI_calib[3],
                self.ROI_calib[0]:self.ROI_calib[2],
            ]
        else:
            roi = self.frame

        if roi.size == 0:
            return False

        #get the min and max values for each channel
        blue_min, blue_max, _, _ = cv2.minMaxLoc(roi[:,:,0])
        green_min, green_max, _, _ = cv2.minMaxLoc(roi[:,:,1])
        red_min, red_max, _, _ = cv2.minMaxLoc(roi[:,:,2])
        
        shared.min_ch = [blue_min, green_min, red_min]
        shared.max_ch = [blue_max, green_max, red_max]
        
        # print(f"Auto threshold values - Blue: ({blue_min}, {blue_max}), Green: ({green_min}, {green_max}), Red: ({red_min}, {red_max})" )
        
        # print(f"Auto threshold applied. Min: {shared.min_ch}, Max: {shared.max_ch}")
        
        shared.is_slider_sync = False
        return True
    
    def mouse_callback(self, event, x, y, flags, param):
        if shared.is_calib is False or self.auto_threshold is False:
            return
            
        if self.ROI_calib[0] is not None and self.ROI_calib[1] is not None:
            if event == cv2.EVENT_LBUTTONDOWN:
                # print(f"Mouse cliccked at2: ({x}, {y})")
                self.ROI_calib[2] = x
                self.ROI_calib[3] = y
                self.autoThreshold()
                self.auto_threshold = False
                
            if event == cv2.EVENT_MOUSEMOVE:
                # print(f"mouse move ({x}, {y})")
                self.mouse_pos = (x,y);
                
        if self.ROI_calib[0] is None and self.ROI_calib[1] is None and event == cv2.EVENT_LBUTTONDOWN:
                    # print(f"Mouse clicked at1: ({x}, {y})")
                    self.ROI_calib[0] = x
                    self.ROI_calib[1] = y         
            
    def run(self):
        cap = cv2.VideoCapture(0)  # Use the default camera (0)
        cv2.namedWindow('Object Detection', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Object Detection', self.mouse_callback)
        
        while cap.isOpened():
            ret, self.frame = cap.read()
            if not ret:
                break

            # Process the frame (e.g., object detection)
            if shared.color_space == "BGR":
                self.cvt_color_code = None  # No conversion needed for BGR
            elif shared.color_space == "HSV":
                self.cvt_color_code = cv2.COLOR_BGR2HSV
            elif shared.color_space == "HLS":
                self.cvt_color_code = cv2.COLOR_BGR2HLS
            elif shared.color_space == "YUV":
                self.cvt_color_code = cv2.COLOR_BGR2YUV
            elif shared.color_space == "YCrCb":
                self.cvt_color_code = cv2.COLOR_BGR2YCrCb
            else:
                self.cvt_color_code = None
                
            cv2.cvtColor(self.frame, self.cvt_color_code, self.frame) if self.cvt_color_code is not None else self.frame
            
            
            show_frame = self.frame.copy()
            if shared.is_calib == True or self.auto_threshold == True:
                # print(f"ROI_calib: {self.ROI_calib}, mouse_pos: {self.mouse_pos}")
                if self.ROI_calib[0] is not None and self.ROI_calib[1] is not None:
                    cv2.circle(show_frame, (self.ROI_calib[0], self.ROI_calib[1]), 5, (0,0,255), -1)
                    
                if self.ROI_calib[0] is not None and self.ROI_calib[1] is not None and self.mouse_pos[0] is not None and self.mouse_pos[1] is not None:
                    cv2.rectangle(show_frame, (self.ROI_calib[0], self.ROI_calib[1]), (self.mouse_pos[0], self.mouse_pos[1]), (0,255,0), 3)

            
            
            # Display the processed frame
            cv2.imshow('Object Detection', show_frame)
            # cv2.imshow('Thresshold Settings', np.zeros((1, 400), dtype=np.uint8))  # Placeholder for trackbars

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break