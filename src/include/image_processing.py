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
            elif shared.color_space == "LAB":
                self.cvt_color_code = cv2.COLOR_BGR2LAB
            else:
                self.cvt_color_code = None
            
            cv2.flip(self.frame, 1, self.frame)
            showed_frame = self.frame.copy()
            
            lab = cv2.cvtColor(self.frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            self.frame = cv2.merge((clahe.apply(l), a, b))
            cv2.cvtColor(self.frame, cv2.COLOR_LAB2BGR, self.frame)
            cv2.cvtColor(self.frame, self.cvt_color_code, self.frame) if self.cvt_color_code is not None else self.frame
            proc_frame = self.frame.copy()
            
            if shared.is_calib == True or self.auto_threshold == True:
                # print(f"ROI_calib: {self.ROI_calib}, mouse_pos: {self.mouse_pos}")
                if self.ROI_calib[0] is not None and self.ROI_calib[1] is not None:
                    cv2.circle(proc_frame, (self.ROI_calib[0], self.ROI_calib[1]), 5, (0,0,255), -1)
                    
                if self.ROI_calib[0] is not None and self.ROI_calib[1] is not None and self.mouse_pos[0] is not None and self.mouse_pos[1] is not None:
                    cv2.rectangle(proc_frame, (self.ROI_calib[0], self.ROI_calib[1]), (self.mouse_pos[0], self.mouse_pos[1]), (0,255,0), 3)

            thresholded_image = cv2.inRange(self.frame, np.array(shared.min_ch), np.array(shared.max_ch))
            cv2.erode(thresholded_image, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)), thresholded_image, iterations= 1)
            cv2.dilate(thresholded_image, cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2)), thresholded_image, iterations=5)
            
            contour , _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            convex_hull_area = thresholded_image.copy()
            
            for cnt in contour:
                convex_hull = cv2.convexHull(cnt)
                cv2.drawContours(convex_hull_area, [convex_hull], -1, (255, 255, 255), -1)
                
            contour, _ = cv2.findContours(convex_hull_area, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            sorted_contours = sorted(contour, key=cv2.contourArea, reverse=True)
            if sorted_contours:
                largest_contour = sorted_contours[0]
                cv2.rectangle(proc_frame, cv2.boundingRect(largest_contour), (0, 255, 0), 2)
                cv2.rectangle(showed_frame, cv2.boundingRect(largest_contour), (0, 255, 0), 2)
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    margin = 10;
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    normalized_cX = (cX - margin) / (proc_frame.shape[1] - 2 * margin)
                    normalized_cY = (cY - margin) / (proc_frame.shape[0] - 2 * margin)
                    normalized_cX = max(0, min(1, normalized_cX))
                    normalized_cY = max(0, min(1, normalized_cY))
                    shared.player_pos = (normalized_cX, normalized_cY)
                    cv2.circle(proc_frame, (cX, cY), 5, (0, 255, 0), -1)
                    cv2.putText(proc_frame, f"Player Pos: ({cX}, {cY})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
            thresholded_image = cv2.bitwise_or(thresholded_image, convex_hull_area)
                
            
            # Display the processed frame

            
            if shared.is_calib == True:
                if cv2.getWindowProperty('Object Detection', cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyWindow('Object Detection')
                
                cv2.namedWindow('Processed frame', cv2.WINDOW_NORMAL)
                cv2.setMouseCallback('Processed frame', self.mouse_callback)    
                
                cv2.imshow('Processed frame', proc_frame)
                cv2.imshow('Thresholded frame', thresholded_image)
            elif shared.is_calib == False:
                if cv2.getWindowProperty('Processed frame', cv2.WND_PROP_VISIBLE) >= 1 and cv2.getWindowProperty('Thresholded frame', cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyWindow('Processed frame')
                    cv2.destroyWindow('Thresholded frame')
                cv2.imshow('Object Detection', showed_frame)

            # cv2.imshow('Thresshold Settings', np.zeros((1, 400), dtype=np.uint8))  # Placeholder for trackbars

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break