
from time import sleep
from urllib import parse
import pyttsx3
import wave
import requests
import time
import base64
from pyaudio import PyAudio, paInt16
import webbrowser
import pyaudio
import threading


framerate = 16000  # 采样率
num_samples = 2000  # 采样点
channels = 1  # 声道
sampwidth = 2  # 采样宽度2bytes
FILEPATH = 'speech.wav'

base_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s"
APIKey = "iyfr2KoqKXF6WVH7vAI1Y8E5"
SecretKey = "WssHINzG9VNGBxiwefo0pCUkb7Om7iVs"

HOST = base_url % (APIKey, SecretKey)


def getToken(host):
    res = requests.post(host)
    return res.json()['access_token']


def save_wave_file(filepath, data):
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b''.join(data))
    wf.close()


def my_record():
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=channels,
                     rate=framerate, input=True, frames_per_buffer=num_samples)
    my_buf = []
    # count = 0
    t = time.time()
    print('正在录音...')

    while time.time() < t + 4:  # 秒  # 设置录音时间（秒） 循环read，每次read 2000frames
        string_audio_data = stream.read(num_samples)
        my_buf.append(string_audio_data)
    print('录音结束.')
    save_wave_file(FILEPATH, my_buf)
    stream.close()

class Recorder:
    def __init__(self, chunk=1024, channels=1, rate=64000):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = True
        self._frames = []

    # 定义开始录音
    def start(self): #定义一个新的线程
        threading._start_new_thread(self.__recording, ())

    # 定义录音
    def __recording(self):
        self._running = True
        self._frames = []
        p = pyaudio.PyAudio() #
        stream = p.open(format=paInt16, channels=channels,
                         rate=framerate, input=True, frames_per_buffer=num_samples)

        while self._running:
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    # 定义停止
    def stop(self):
        self._running = False

    # 定义保存
    def save(self, filename):

        p = pyaudio.PyAudio()
        if not filename.endswith(".wav"):
            filename = filename + ".wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        print("Saved")

def get_audio(file):
    with open(file, 'rb') as f:
        data = f.read()
    return data

#传入语音二进制数据，token
#dev_pid为百度语音识别提供的几种语言选择
def speech2text(speech_data, token, dev_pid=1536):
    FORMAT = 'wav'
    RATE = '16000'
    CHANNEL = 1
    CUID = '*******'
    SPEECH = base64.b64encode(speech_data).decode('utf-8')

    data = {
        'format': FORMAT,
        'rate': RATE,
        'channel': CHANNEL,
        'cuid': CUID,
        'len': len(speech_data),
        'speech': SPEECH,
        'token': token,
        'dev_pid': dev_pid  #dev_pid表述输入语音的类型，1536表示中文普通话
    }
    url = 'https://vop.baidu.com/server_api'
    headers = {'Content-Type': 'application/json'}
    # r=requests.post(url,data=json.dumps(data),headers=headers)
    print('正在识别...')
    r = requests.post(url, json=data, headers=headers)
    Result = r.json()
    if 'result' in Result:
        return Result['result'][0]
    else:
        return Result

########################

###调用chatgpt接口
import openai

# Set your API key
openai.api_key = "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"
# Use the GPT-3 model
def chat(msg):
    completion = openai.Completion.create(
        engine="text-davinci-003",
        prompt=msg,
        max_tokens=1024,
        temperature=0.5
    )
    # Print the generated text
    # print(completion.choices[0].text)
    return completion.choices[0].text

def ownthink(msg):
    #调用思知API
    msg = parse.quote(msg)  # 编码
    url = 'https://api.ownthink.com/bot?spoken={}'.format(msg)
    html = requests.get(url)
    return html.json()["data"]['info']['text']


def chat_robot(msg):
    """调用青云客机器人接口实现对话"""
    msg = parse.quote(msg)  # 编码
    url = "http://api.qingyunke.com/api.php?key=free&appid=0&msg={}".format(msg)
    html = requests.get(url)  # GET请求

    return html.json()["content"].replace("{br}", "\n\t\t")


def write_error_content(msg, file="UnicodeEncodeError.txt"):
    """如果遇到无法解码的问题，就写入文件中"""
    with open(file, "w", encoding="utf-8") as f:
        content = "我>>>%s\n机器人：%s" % (msg, chat(msg))
        f.write(content)
    print("遇到无法解码的问题，请在新创建的'%s'文件中查看聊天信息！" % file)
    sleep(4)

##############购物模块############
def openbrowser(text):
    maps = {
        '百度': ['百度', 'baidu'],
        '腾讯': ['腾讯', 'tengxun'],
        '网易': ['网易', 'wangyi']

    }
    if text in maps['百度']:
        webbrowser.open_new_tab('https://www.baidu.com')
    elif text in maps['腾讯']:
        webbrowser.open_new_tab('https://www.qq.com')
    elif text in maps['网易']:
        webbrowser.open_new_tab('https://www.163.com/')
    # else:
    #     webbrowser.open_new_tab('https://www.baidu.com/s?wd=%s' % text)
    else:
        webbrowser.open_new_tab('https://search.jd.com/Search?keyword={}'.format(text))

def videobrowser(text):
    maps = {
        '百度': ['百度', 'baidu'],
        '腾讯': ['腾讯', 'tengxun'],
        '网易': ['网易', 'wangyi']

    }
    if text in maps['百度']:
        webbrowser.open_new_tab('https://www.baidu.com')

    else:
        webbrowser.open_new_tab('https://v.qq.com/x/search/?q={}'.format(text))





base_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s"
APIKey = "iyfr2KoqKXF6WVH7vAI1Y8E5"
SecretKey = "WssHINzG9VNGBxiwefo0pCUkb7Om7iVs"

speed = 260
def main():
    """主函数"""
    while True:
        engine = pyttsx3.init()
        print("请选择聊天模式：1、打字 2、语音")
        choice = int(input("请输入1或2选择聊天模式"))
        if choice == 1:
            while True:
                massage = input("我>>>")

                if massage == "exit":
                    print("机器人：", "下再聊吧，拜拜~")
                    sleep(1)
                    break
                if massage == "再见":
                    print("机器人：", "下再聊吧，拜拜~")
                    sleep(1)
                    break
                elif not massage.replace(" ", ""):  # 如果什么也没输入，则输出下面消息
                    print("机器人：", "没有输入内容！")
                    continue

                try:
                    p=0
                    #判断是否为购物
                    for ii in range(len(massage)):
                        if massage[ii]=="买":
                            p = 1
                            #从txt中读取关键词
                            x = list()
                            with open("D:/shopping.txt", encoding="UTF-8") as f:
                                for line in f.readlines():
                                    line = line.strip('\n')  # 去掉列表中每一个元素的换行符
                                    x.append(line)

                            for k in range(len(x)):
                                for i in range(len(massage)):
                                    if massage[i:i + 2] == x[k]:
                                        key = massage[i:i + 2]
                                        openbrowser(key.strip('，'))
                                        print("网页已打开")
                        elif massage[ii] == "看":
                            p = 1
                            #判断看视频
                            print("正在搜索视频")
                            x = list()
                            with open("D:/video.txt", encoding="UTF-8") as f:
                                for line in f.readlines():
                                    line = line.strip('\n')  # 去掉列表中每一个元素的换行符
                                    x.append(line)

                            for k in range(len(x)):  #x代表txt里面名称的个数
                                for i in range(len(massage)):
                                    if len(x[k][1:-2])>=3:
                                        if massage[i:i + 3] == x[k][1:4]:
                                            key = massage[i:i + 3]
                                            videobrowser(key.strip('，'))
                                            print("网页已打开")
                                    else:
                                        if massage[i:i + 2] == x[k][1:3]:
                                            key = massage[i:i + 2]
                                            videobrowser(key.strip('，'))
                                            print("网页已打开")

                    if p == 0:
                        res = ownthink(massage)
                        print("思知机器人：", res)
                        engine.setProperty('rate', speed)
                        pyttsx3.speak(res)

                    print("回答是否满意？可使用加强型机器人")
                    b = int(input("若使用，请输入1，否则请输入2 "))
                    if b==1:
                        res = chat(massage)
                        print("ChatGPT机器人：", res)
                        pyttsx3.speak(res)
                    else:
                        continue
                except UnicodeEncodeError:
                    write_error_content(massage)
                    break
                except:
                    print("离线机器人：", "网络异常，请检查网络！")
        elif choice == 2:
            while True:
                a = int(input('请输入数字1开始录音:'))
                if a == 1:
                    rec = Recorder()
                    begin = time.time()
                    print("Start recording")
                    rec.start()
                    b = int(input('请输入相应2停止录音:'))
                    if b == 2:
                        print("Stop recording")
                        rec.stop()
                        fina = time.time()
                        t = fina - begin
                        print('录音时间为%ds' % t)
                        rec.save("speech.wav")
                # print("欢迎使用语音聊天功能！(输入空格以开始或结束录音)")
                # my_record()
                TOKEN = getToken(HOST)
                speech = get_audio(FILEPATH)
                result = speech2text(speech, TOKEN, int(1536))
                print(result)
                massage = result

                if massage == "exit":
                    print("机器人：", "下再聊吧，拜拜~")
                    sleep(1)
                    break

                if massage == "再见":
                    print("机器人：", "下再聊吧，拜拜~")
                    sleep(1)
                    break
                elif not massage.replace(" ", ""):  # 如果什么也没输入，则输出下面消息
                    print("机器人：", "没有输入内容！")
                    continue

                try:
                    p = 0
                    # 判断是否为购物
                    for ii in range(len(massage)):
                        if massage[ii] == "买":
                            p = 1
                            # 从txt中读取关键词
                            x = list()
                            with open("D:/shopping.txt", encoding="UTF-8") as f:
                                for line in f.readlines():
                                    line = line.strip('\n')  # 去掉列表中每一个元素的换行符
                                    x.append(line)

                            for k in range(len(x)):
                                for i in range(len(massage)):
                                    if massage[i:i + 2] == x[k]:
                                        key = massage[i:i + 2]
                                        openbrowser(key.strip('，'))
                                        print("网页已打开")
                        elif massage[ii] == "看":
                            p = 1
                            # 判断看视频
                            print("正在搜索视频")
                            x = list()
                            with open("D:/video.txt", encoding="UTF-8") as f:
                                for line in f.readlines():
                                    line = line.strip('\n')  # 去掉列表中每一个元素的换行符
                                    x.append(line)

                            for k in range(len(x)):  # x代表txt里面名称的个数
                                for i in range(len(massage)):
                                    if len(x[k][1:-2]) >= 3:
                                        if massage[i:i + 3] == x[k][1:4]:
                                            key = massage[i:i + 3]
                                            videobrowser(key.strip('，'))
                                            print("网页已打开")
                                    else:
                                        if massage[i:i + 2] == x[k][1:3]:
                                            key = massage[i:i + 2]
                                            videobrowser(key.strip('，'))
                                            print("网页已打开")

                    if p == 0:
                        res = ownthink(massage)
                        print("思知机器人：", res)
                        engine.setProperty('rate', speed)
                        pyttsx3.speak(res)

                    print("回答是否满意？可使用加强型机器人")
                    b = int(input("若使用，请输入1，否则请输入2 "))
                    if b == 1:
                        res = chat(massage)
                        print("ChatGPT机器人：", res)
                        pyttsx3.speak(res)
                    else:
                        continue
                except UnicodeEncodeError:
                    write_error_content(massage)
                    break
                except:
                    print("离线机器人：", "网络异常，请检查网络！")



if __name__ == '__main__':
    print("支持功能：天气、翻译、笑话、计算、古诗、购物、搜索电影、人工智能聊天等功能")
    print("输入'exit'退出此程序\n")
    pyttsx3.speak("欢迎使用对话机器人")
    main()


