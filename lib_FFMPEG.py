from pathlib import Path
import re
import subprocess
import pexpect
from pexpect.popen_spawn import PopenSpawn
import asyncio
from collections import deque
from datetime import timedelta
import time
from decimal import *


### 共通定数定義 ###
SUCCESS = 0
FAIL = -1
ABORT = -2

YES = 1
NO = 0

ANALYZE_START = 1
ANALYZING = 2
ANALYZE_COMPLETE = 3
CONVERT_START = 4
CONVERTING = 5
CONVERT_COMPLETE = 6

AR_KEEP = 0
AR_16_9 = 1
AR_4_3 = 2
####################

### グローバル変数 ###
duration_total = timedelta()
is_analyze_complete = False
####################


def timedelta_value(tc):

    h, m, sf = tc.split(":")
    s, ms = sf.split(".")
    return timedelta(hours = int(h), minutes = int(m), seconds = int(s), microseconds = int(ms))


async def analyze(que, folder_path):

    global duration_total
    global is_analyze_complete

    duration_total = timedelta(0)
    is_analyze_complete = False

    input_dir = Path(folder_path)
    input_files = sorted(input_dir.glob("**/*"))
    t = (ANALYZE_START, duration_total, 0)
    que.append(t)
    await asyncio.sleep(0.01)

    command = \
            "ffmpeg " + \
            '-i "concat:' + "|".join([i.as_posix() for i in input_files]) + '" ' + \
            "-f null -"

    thread = pexpect.popen_spawn.PopenSpawn(command)

    cpl = thread.compile_pattern_list([
        pexpect.EOF,
        "^(frame=.*)",
        '(.+)'
    ])

    while True:
        index = thread.expect_list(cpl, timeout=None)
        if index == 0: # EOF
            t = (ANALYZE_COMPLETE, 0, 0)
            que.append(t)
            await asyncio.sleep(0.01)
            break
        elif index == 1:
            line = thread.match.group(0).decode()
            array = tuple(re.sub('=\s+', '=', line.strip()).split(' '))
            duration_total = timedelta_value(array[4].split('=')[1])
            t = (ANALYZING, duration_total, 0)
            que.append(t)
            await asyncio.sleep(0.01)
        elif index == 2:
            pass

    is_analyze_complete = True
    t = (ANALYZE_COMPLETE, 0, 0)
    que.append(t)
    await asyncio.sleep(0.01)


async def convert(que, folder_path, file_name, start_time, end_time, aspect_ratio, is_reEncode):

    global duration_total
    global is_analyze_complete

    while True:
        if is_analyze_complete:
            input_dir = Path(folder_path)
            input_files = sorted(input_dir.glob("**/*"))
            output_file = file_name

            t = (CONVERT_START, 0, 0)
            que.append(t)
            await asyncio.sleep(0.01)

            index = 0
            line = ''

            # パラメータ設定
            if not start_time:                          # 開始時間
                ss = ""
            else:
                ss = "-ss " + start_time + " "
        
            if not end_time:                           # 終了時間
                to = ""
            else:
                to = "-to " + end_time + " "

            if  aspect_ratio == AR_KEEP:            # アスペクト比
                aspect = ""
                bwdif = "-vf bwdif=1,pp=dr,unsharp=5:5:0.20:5:5:0.10,hqdn3d "
            elif  aspect_ratio == AR_16_9:
                aspect = "-aspect 16:9 "
                bwdif = "-vf pp=dr,unsharp=5:5:0.20:5:5:0.10,hqdn3d "
            elif  aspect_ratio == AR_4_3:
                aspect = "-aspect 4:3 "
                bwdif = "-vf pp=dr,unsharp=5:5:0.20:5:5:0.10,hqdn3d "

            if is_reEncode == NO and (not start_time and not end_time):        # 音声再エンコード
                acopy = "-acodec copy "
            else:
                acopy = ""

            # MP4変換
            command = \
                    "ffmpeg -y " + \
                    ss + \
                    to + \
                    '-i "concat:' + "|".join([i.as_posix() for i in input_files]) + '" ' + \
                    aspect + \
                    bwdif + \
                    "-vcodec libx264 -pix_fmt yuv444p10le -level:v 4.0 " + \
                    acopy + \
                    "-crf 18 -preset veryfast -tune film -threads 10 " + \
                    output_file

            print(command)

            #   subprocess.run(command, shell=True)
            #   proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            thread = pexpect.popen_spawn.PopenSpawn(command)

            lt = timedelta(milliseconds = int(time.time() * 1000)) #開始時刻

            cpl = thread.compile_pattern_list([
                pexpect.EOF,
                "^(frame=.*)",
                '(.+)'
            ])

            while True:
                index = thread.expect_list(cpl, timeout=None)
                if index == 0: # EOF
                    t = (CONVERT_COMPLETE, 0, 0)
                    que.append(t)
                    await asyncio.sleep(0.01)
                    return
                elif index == 1:
                    dt = timedelta(milliseconds = int(time.time() * 1000)) - lt #経過時間
                    line = thread.match.group(0).decode()
                    array = tuple(re.sub('=\s+', '=', line.strip()).split(' '))
                    current_time = timedelta_value(array[4].split('=')[1])
                    remain_time = timedelta(milliseconds = ((duration_total - current_time) / timedelta(milliseconds = (current_time / dt) * 1000) * 1000))
                    percentage = Decimal(current_time / duration_total * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                    t = (CONVERTING, remain_time, percentage)
                    que.append(t)
                    await asyncio.sleep(0.01)
                elif index == 2:
                    await asyncio.sleep(0.01)
                    pass

        else:
            await asyncio.sleep(0.01)



def merge(folder_path, file_name):

    # フォルダ内のファイル一覧
    input_dir = Path(folder_path)
    input_files = sorted(input_dir.glob("**/*"))
    output_file = file_name

    # ファイル結合
    command = \
            "ffmpeg -y " + \
            '-i "concat:' + "|".join([i.as_posix() for i in input_files]) + '" ' + \
            "-c copy -preset veryfast -threads 10 " + \
            output_file

    print(command)
    subprocess.run(command, shell=True)

    # エラー判定
    path = Path(output_file)
    if path.stat().st_size == 0:
        ret = FAIL
    else:
        ret = SUCCESS

    return ret


def cut(input_file_name, output_file_name, start_time, end_time):

    # フォルダ内のファイル一覧
    input_file = input_file_name
    output_file = output_file_name

    # パラメータ設定
    if not start_time:                          # 開始時間
        ss = ""
    else:
        ss = "-ss " + start_time + " "
        
    if not end_time:                           # 終了時間
        to = ""
    else:
        to = "-to " + end_time + " "

    # カット
    command = \
            "ffmpeg -y " + \
            ss + \
            to + \
            '-i ' +'"' + input_file +'"' + ' ' + \
            "-codec copy -preset veryfast -threads 10 " + \
            output_file

    print(command)
    subprocess.run(command, shell=True)

    # エラー判定
    path = Path(output_file)
    if path.stat().st_size == 0:
        ret = FAIL
    else:
        ret = SUCCESS

    return ret


def changeAspectRatio(input_file_name, output_file_name, aspect_ratio):

    # フォルダ内のファイル一覧
    input_file = input_file_name
    output_file = output_file_name

    # パラメータ設定
    if  aspect_ratio == AR_16_9:            # アスペクト比
        aspect = "-aspect 16:9 "
    elif  aspect_ratio == AR_4_3:
        aspect = "-aspect 4:3 "
    else: 
        aspect = ""

    # アスペクト比変更
    command = \
            "ffmpeg -y " + \
            '-i ' +'"' + input_file +'"' + ' ' + \
            aspect + \
            "-codec copy -preset veryfast -threads 10 " + \
            output_file

    print(command)
    subprocess.run(command, shell=True)

    # エラー判定
    path = Path(output_file)
    if path.stat().st_size == 0:
        ret = FAIL
    else:
        ret = SUCCESS

    return ret


