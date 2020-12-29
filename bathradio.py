# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import subprocess
import json
import os.path

# 設定ファイルパスを指定
setting_dir = "/etc/bath_radio"

# シェルのパスを指定
playradiko = "/opt/radio_core/playradiko.sh"

# ラジオ再生中フラグ
playing = False

# 処理タイミングカウンタ
maincnt = 0
retrycnt = 0

# Bluetoothスピーカー接続
def connectBltSpk():
    global playing
    global retrycnt
    currentpath = os.path.dirname(os.path.abspath(__file__))
    # 設定読み込み
    f = open(os.path.join(setting_dir, "bltspk_setting.json"), "r")
    bltset = json.loads(f.read())
    f.close()
    # 接続確認
    com = os.path.join(currentpath, "bltspk_status.sh") + " " + bltset["device"]
    ret = subprocess.call(com, shell=True)
    # 接続できていなければ接続
    if str(ret) == "1":
        if playing:
            retrycnt = retrycnt + 1
            if retrycnt > 9:
                playing = False
                subprocess.call(os.path.join(currentpath, "playradiko.sh") + ' stop', shell=True)
                retrycnt = 0
        com = os.path.join(currentpath, "bltspk_connect.sh") + " " + bltset["device"] + " " + str(bltset["vol"])
        subprocess.call(com, shell=True)
        if playing:
            # 一旦ラジオ停止
            subprocess.call(os.path.join(currentpath, "playradiko.sh") + ' stop', shell=True)
            # ラジオ再生
            ns = getStation()
            subprocess.call(os.path.join(currentpath, "playradiko.sh") + ' start ' + ns, shell=True)
    else:
        print("Bluetoothスピーカーに接続済です。")

# 地域から局リストを取得する
def Prefecture2Stations(prefecture):
    try:
        # 局リストを読み込む
        currentpath = os.path.dirname(os.path.abspath(__file__))
        f = open(os.path.join(currentpath, "stationlist.json"), "r")
        stationlist = f.read()
        f.close()
        sljson = json.loads(stationlist)
        # 地域⇒局リスト
        ret = sljson[prefecture]
        return ret
    except KeyError:
        return ""

# 現在のラジオ局を取得
def getStation():
    # 県を読み込む
    f = open (os.path.join(setting_dir, "region.txt"), "r")
    ken = f.read()
    f.close()
    # 現在の局を読み込む
    f = open (os.path.join(setting_dir, "now_station.txt"), "r")
    s = int(f.read())
    f.close()
    # 曲リストを読み込む
    p2s = Prefecture2Stations(ken)
    # ラジオ局コードを返す
    return p2s[s].encode("utf-8")

# 次の局に変更する
def nextStation():
    # 県を読み込む
    f = open (os.path.join(setting_dir, "region.txt"), "r")
    ken = f.read()
    f.close()
    # 現在の局を読み込む
    f = open (os.path.join(setting_dir, "now_station.txt"), "r")
    s = int(f.read())
    f.close()
    # 曲リストを読み込む
    p2s = Prefecture2Stations(ken)
    # 曲リストの配列サイズを求める
    stsize = len(p2s)
    # 次の局を求める
    nexts = (s + 1) % stsize
    # 現在の局を更新
    f = open (os.path.join(setting_dir, "now_station.txt"), "w")
    f.write(str(nexts))
    f.close()
    # 次のラジオ局コードを返す
    return p2s[nexts].encode("utf-8")

# 白ボタンが押されたときの処理
## ラジオ再生開始
def whiteBtn():
    global playing
    currentpath = os.path.dirname(os.path.abspath(__file__))
    if playing:
        subprocess.call(os.path.join(currentpath, "playradiko.sh") + ' stop', shell=True)
        playing = False
    else:
        # 現在の局を読み込む
        ns = getStation()
        print(ns + "を再生します。")
        # ラジオ再生
        playing = True
        subprocess.call(os.path.join(currentpath, "playradiko.sh") + ' start ' + ns, shell=True)

# 緑ボタンが押されたときの処理
## ラジオ局変更
def greenBtn():
    global playing
    if playing:
        currentpath = os.path.dirname(os.path.abspath(__file__))
        # 次の局を求める
        nexts = nextStation()
        print(nexts + "を再生します。")
        # 現在の局の再生を止める
        subprocess.call(os.path.join(currentpath, "playradiko.sh") + ' stop', shell=True)
        # 次の局を再生
        subprocess.call(os.path.join(currentpath, "playradiko.sh") + ' start ' + nexts, shell=True)

# GPIOへアクセスする番号をBCMの番号で指定することを宣言
GPIO.setmode(GPIO.BCM)

# BCM 5番、27番ピンを入力に設定
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ボタンが押された場合に呼ばれるコールバック関数
def push_white(gpio_pin):
    if gpio_pin == 5:
        whiteBtn()

def push_green(gpio_pin):
    if gpio_pin == 27:
        greenBtn()

# ボタンプッシュイベントを登録
GPIO.add_event_detect(5, GPIO.FALLING, bouncetime=500)
GPIO.add_event_callback(5, push_white)

GPIO.add_event_detect(27, GPIO.FALLING, bouncetime=500)
GPIO.add_event_callback(27, push_green)

try:
    while True:
        # 20秒に一度Bluetoothスピーカーの接続を確認し、
        # 接続されていなければ接続
        if maincnt % 20 == 0:
            connectBltSpk()
        maincnt = maincnt + 1
        time.sleep(1)
        if maincnt == 60:
            maincnt = 0
except KeyboardInterrupt:
    GPIO.cleanup()