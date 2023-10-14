#官方函式庫
from multiprocessing import Queue
import multiprocessing
import time
import sys
import base64
import threading

#第三方函式庫
import cv2

#自己撰寫部分
#因為有使用到yolov7的部分程式碼，所以調整path，避免import發生錯誤
sys.path.append('yolo')
from CustomDetect import CustomDetect

#目前與YoutubeVideo分開寫是考慮可以透過src的不同來擴充其他影片來源
#例如:local影片 或是攝影機
class Video:
    def __init__(self):
        
        #影片來源
        self.src = None

        #用來存取讀出來的影片frame
        #必須使用multiprocessing.Manager()所提供的queue
        #來進行process內以及外部的變數存取
        #否則直接傳入process外變數進入process內並有更改變數的狀況
        #會導致error ex:
        self.manager = multiprocessing.Manager()
        self.q = self.manager.Queue()

        #影片FPS
        self.FPS_s = 1/40

        self.CustomDetect_worker = CustomDetect()
    
    """
    輸入:
        src : 影片來源 可以是url或是loacl path
        q : cv2讀出來的圖片存放在queue裡面
    輸出:
    處理:
        讀取src提供的影片
        通常建議使用multiprocessing來處理讀取影片的部分
        因為read是返回下一個frame，

        而若是Thread再經過別的處理，再切回來的話可能造成delay
        並且會跟正常的撥放時間越差越大
        (這裡需要之後實驗來驗證)
    """
    def read(self,src : str, q : Queue):
        print('read start')
        cap = cv2.VideoCapture(src)
        while True:
            ret,frame = cap.read()

            if ret:
                q.put(frame)
            
            #保持取最新一格frame
            if q.qsize() > 1:
               q.get()
            """
            必須sleep一段時間再讀
            推測可能是因為讀取的速度太快，
            但一段時間內能讀取再顯示的資料有限，跟不上讀取的速度
            沒有sleep會導致 會有快速撥放一段影片在停滯的狀況
            選擇停1/40 是因為yt影片通常是30fps，
            但停1/30相當於每兩frame才讀1frame，會導致越來越延遲
            所以選擇停比1/30再少一點的時間，也就是1/40
            """
            time.sleep(self.FPS_s)
    
    """
    輸入:
        socketio:目前建立連線至前台的管道
    輸出:無
    處理:
        將讀取出來的圖片先偵測目前畫面人數，並將辨識出的人用格子標示出來
        base64編碼成所需格式
        透過flask-socketio將圖片傳至前台
    """
    def image_process(self,socketio):
        while True:
            frame = self.q.get()
            if frame is None:
                break
            frame = self.CustomDetect_worker.object_detect(frame)
            _, encoded_frame = cv2.imencode('.jpg', frame)
            frame_str = base64.encodebytes(encoded_frame).decode('utf-8')
            socketio.emit('receive_image', frame_str)
    
    """
    輸入:
        socketio:目前建立連線至前台的管道
    輸出:無
    處理:
        透過flask-socketio將目前偵測人數以一秒一次的頻率傳送至前台
    """
    def detect_number_process(self,socketio):
        while True:
            socketio.emit('receive_detect_number',self.CustomDetect_worker.detect_number)
            time.sleep(1)

    """
    輸入:
        socketio:目前建立連線至前台的管道
    輸出:無
    處理:
        使用thread來切換處理圖片跟傳送偵測人數
        由於detect_number是設定每秒一次，而不需要執行
        而image_process也不用保證每個frame都要處理到，只要處理時是最新的frame即可
        故這邊使用thread來切換detect與image_process
    """
    def show(self,socketio):
        image_process_thread =  threading.Thread(target=self.image_process, args=(socketio,))
        detect_number_thread =  threading.Thread(target=self.detect_number_process, args=(socketio,))
        image_process_thread.start()
        detect_number_thread.start()
