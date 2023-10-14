#官方函式庫
import sys
from multiprocessing import Process

#第三方函式庫
import yaml
from flask import Flask,request,jsonify
from flask_cors import CORS
from flask_socketio import SocketIO



#自己撰寫部分
from video.YoutubeVideo import YoutubeVideo
from video.Video import Video

#因為有使用到yolov7的部分程式碼，所以調整path，避免import發生錯誤
sys.path.append('yolo')
from CustomDetect import CustomDetect

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

youtube_video_worker = YoutubeVideo()
Video_worker = Video()

"""
輸入:無
輸出:無
處理:回復前台並印出請求是來自哪個ip
"""
@app.route('/hello',methods = ["GET"])
def hello():
    ip = request.remote_addr
    print('{} Access'.format(ip))
    return jsonify('This project is written by JunYan, Zhao.')

@app.route('/', methods=['GET'])
def index():
    return 'Backend is running.'

"""
設定影片url
新增process去執行讀取影片的動作
固定回傳圖片至前台
"""
@app.route('/set_video_url', methods=['POST'])
def set_video_url():
    info = request.get_json()
    print(info)
    youtube_video_worker.get_video_url(info)
    read = Process(target=Video_worker.read,args=(youtube_video_worker.video_url,Video_worker.q,))
    read.start()
    Video_worker.show(socketio)
    return 'set success'




if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 15383,debug = True)
    
    
