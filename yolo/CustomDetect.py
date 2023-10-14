#官方函式庫
import sys

#第三方函式庫
import cv2
import torch
from numpy import random
import numpy

#yolov7部分
from models.experimental import attempt_load
from utils.general import non_max_suppression

class CustomDetect:
    def __init__(self):
        weight = 'yolo/yolov7.pt'
        self.device = 'cuda'
        self.image_size = 320
        self.model = attempt_load(weight, map_location=self.device)
        self.thickness = 2  # 框線厚度
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        """
        取得模型分類類別
        隨機分配各類別顏色
        """
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        #self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
        self.detect_number = 0

    """
    輸入：
        img:想做物件偵測的圖片
    輸出：
        img:做完物件偵測的圖片
    處理：對圖片進行物件偵測，並將偵測的結果畫到原圖片上並回傳
    """
    def object_detect(self, img : numpy.ndarray) -> numpy.ndarray:
        
        #記錄圖片原大小
        origin_h, origin_w = img.shape[:2]

        #將圖片縮放到符合模型所需大小
        image = cv2.resize(img, (self.image_size, self.image_size))
        
        #將image轉換成torch的tensor並搬移到指定裝置
        image_pt = torch.from_numpy(image).permute(2, 0, 1).to(self.device)

        #將tensor中的值正規化
        image_pt = image_pt.float() / 255.0
        
        # Infer
        with torch.no_grad():
            pred = self.model(image_pt[None], augment=False)[0]
        
        # NMS
        pred = non_max_suppression(pred)[0].cpu().numpy()
        
        # 將pred的結果還原成員圖片大小
        pred[:, [0, 2]] *= origin_w / self.image_size
        pred[:, [1, 3]] *= origin_h / self.image_size

        self.detect_number  = 0
        
        #根據pred的結果把原圖片畫上方框與pred分類
        #限定只畫出person
        for x1, y1, x2, y2, conf, class_id in pred:
            if self.names[int(class_id)] == 'person':
                self.detect_number = self.detect_number + 1
                color = (0,256,0)
                cv2.rectangle(img,(int(x1),int(y1)),(int(x2),int(y2)),color,self.thickness)
                cv2.putText(img, 'person', (int(x1),int(y1)), self.font , 1.0, color, self.thickness)
        return img
    
if __name__ == '__main__':
    pass



