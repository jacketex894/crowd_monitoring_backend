#第三方函式庫
import yt_dlp as youtube_dl

class YoutubeVideo:
    def __init__(self):
        self.video_url = None

    """
    輸入：
        video_url:想取得的影片網址
    輸出：無
    處理：導出影片480p的url
    """
    def get_video_url(self, video_url : str):
        ydl_opts = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        
            #獲得url影片的相關資訊，並選擇不下載影片
            info_dict = ydl.extract_info(video_url, download=False)
            
            #取得所有影片格式相關資訊
            formats = info_dict.get('formats', None)
            
            #重新計算各影片格式的解析度
            #因為所取得的格式的resolution是以字串儲存的
            for _format in formats:

                #取用480p的影片
                #因為在高畫質的影片讀取再顯示會延遲
                if _format['resolution'] != 'audio only' and _format['height'] == 480:
                    select_format = _format
        self.video_url = select_format['url']
    
    
