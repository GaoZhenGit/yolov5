from time import sleep, time
import requests
from multiprocessing import Process
from multiprocessing import Queue
import threading

multiprocess_queue:Queue = None

# ========== should call in sub process start ========== 
def needSubProcessStop():
    ret = multiprocess_queue is not None and not multiprocess_queue.empty()
    if ret:
        from utils.general import LOGGER
        LOGGER.info('receive stop signal from main process')
        multiprocess_queue.get(False)
    return ret

def setSavePath(path):
    if multiprocess_queue is not None:
        multiprocess_queue.put(path)

# ========== should call in sub process end ========== 

server_base_url = "http://localhost:8090/"

def getRequest(url:str,param):
    printColor('request:'+url+',param:'+str(param))
    x = requests.post(url=url,json=param)
    code = x.status_code
    printColor('request:'+url+'code:'+str(code))
    if code == 200:
        return x.json()
    else:
        return None

def uploadDetectionResult():
    printColor('uploadDetectionResult')
    pass


class NetworkFlow:
    def __init__(self) -> None:
        self.streamUrl = ''
        self.resultUrl = ''
        pass

    def isLiveStart(self):
        ret = getRequest(server_base_url+'isLiveStart', {})
        printColor(str(ret))
        success = ret['result'].lower() == 'success'
        if success:
            self.streamUrl = ret['streamUrl']
            self.resultUrl = ret['resultUrl']
            return True
        else:
            return False

    def isLiveStop(self):
        ret = getRequest(server_base_url+'isLiveStop', {"streamUrl":self.streamUrl})
        printColor(str(ret))
        return ret['result'].lower() == 'success'

    def uploadVideo(self,path):
        printColor('uploadVideo')
        file_name = str(int(time())) + '.mp4'
        url=server_base_url+'videoUpload'
        files = {'fileName': (file_name,open(path, 'rb'),'multipart/form-data')}
        p = {'streamUrl':self.streamUrl}
        x = requests.post(url=url,files=files,params=p)
        printColor(str(x.json()))
        self.uploadVideoName = file_name

    def start(self):
        while True:
            if not self.isLiveStart():
                sleep(1)
                printColor('no live start')
                continue
            printColor('receive start message')
            driver = Driver()
            driver.execYolo(src=self.streamUrl, des=self.resultUrl)
            sleep(20) # give some free time until yolo really start
            while True:
                if not self.isLiveStop() and driver.processAlive:
                    sleep(3)
                    printColor('receive continue message')
                    continue
                else:
                    printColor('receive end message')
                    driver.stopYolo()
                    break
            self.uploadVideo(path=driver.getSavePath())
            uploadDetectionResult()
            printColor('one live end')
            sleep(5) # give some free time before next detection
            
class Driver:
    def __init__(self) -> None:
        pass
    
    def execYolo(self, src, des):
        self.q = Queue()
        args = (
            "--weights", "F:\\dataset\\mask_weight\\yolov5x_120epoch_1280_all_cls_nomos\\weights\\best.pt",
            "--img", "1280",
            "--source", src,
            "--push", des,
            "--ofps", "14",
            "--line-thickness","1",
            "--name", "rtmp",
            "--agnostic-nms",
            self.q
        )
        import sys,os 
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        import detect
        self.process = Process(target=detect.run_from_other_process, args=args, name='YoloProcess')
        self.process.start()
        printColor('yolo process start!')
        self.checkThread = threading.Thread(target=self.__checkProcessStatus)
        self.processAlive = self.process.is_alive()
        self.checkThread.start()

    def __checkProcessStatus(self):
        while True:
            sleep(1)
            self.processAlive = self.process.is_alive()
            if not self.processAlive:
                printColor('yolo process end detect')
                break;
        pass

    def stopYolo(self):
        self.q.put('stop')
        self.process.join()
        printColor('yolo process stop!')

    def getSavePath(self):
        path = self.q.get(False)
        if not path.endswith('.mp4'):
            path = path + '.mp4'
        return path

def printColor(text:str):
    print('\033[32m==========' + text + '==========\033[0m')


if __name__ == '__main__':
    flow = NetworkFlow()
    flow.start()
