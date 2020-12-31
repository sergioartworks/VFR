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
import sys


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

H264 = 1
H265 = 2

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
            "-c:v h264_nvenc " + \
            "-f null -"

    thread = pexpect.popen_spawn.PopenSpawn(command, logfile=sys.stdout.buffer)

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


def generate_convert_command(in_files, out_file, cd, stime, etime, asp, isRE):

    if cd == H264:      # H.264 パラメータ設定
        param = \
            "-pix_fmt yuv444p10le -level:v 4.0 -crf 18 -preset veryfast -tune film -qcomp 0.75 -max_muxing_queue_size 9999 -vcodec libx264 "
    elif cd == H265:    # H.265 パラメータ設定
        param = \
            "-pix_fmt yuv444p10le -level:v 4.0 -preset veryfast -max_muxing_queue_size 9999 " + \
            "-vcodec libx265 -x265-params " + '"' + \
            "ctu=32:max-tu-size=16:crf=20.0:tu-intra-depth=2:" + \
            "tu-inter-depth=2:rdpenalty=2:me=3:subme=5:merange=44:b-intra=1:amp=0:ref=5:" + \
            "weightb=1:keyint=360:min-keyint=1:bframes=8:aq-mode=1:aq-strength=1.0:rd=5:" + \
            "psy-rd=1.5:psy-rdoq=5.0:rdoq-level=1:sao=0:open-gop=0:rc-lookahead=80:scenecut=40:" + \
            "max-merge=4:qcomp=0.8:strong-intra-smoothing=0:deblock=-2,-2:qg-size=16:pbratio=1.2" + \
            '" '
    if not stime:                          # 開始時間
        ss = ""
    else:
        ss = "-ss " + stime + " "
        
    if not etime:                           # 終了時間
        to = ""
    else:
        to = "-to " + etime + " "

    if asp == AR_KEEP:            # アスペクト比
        aspect = ""
        bwdif = "-vf bwdif=1,pp=dr,unsharp=5:5:0.8:3:3:0.4,hqdn3d "
    elif asp == AR_16_9:
        aspect = "-aspect 16:9 "
        bwdif = "-vf pp=dr,unsharp=5:5:0.8:3:3:0.4,hqdn3d "
    elif asp == AR_4_3:
        aspect = "-aspect 4:3 "
        bwdif = "-vf pp=dr,unsharp=5:5:0.8:3:3:0.4,hqdn3d "

    if isRE == NO and (not stime and not etime):        # 音声再エンコード
        acopy = "-acodec copy "
    else:
        acopy = ""

    cmd = \
        "ffmpeg -y " + \
        ss + \
        to + \
        '-i "concat:' + "|".join([i.as_posix() for i in in_files]) + '" ' + \
        aspect + \
        bwdif + \
        param + \
        acopy + \
        out_file

    return cmd


async def convert(que, folder_path, file_name, codec, start_time, end_time, aspect_ratio, is_reEncode):

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

            # FFMPEG コマンド生成
            command = generate_convert_command(input_files, output_file, codec, start_time, end_time, aspect_ratio, is_reEncode)
            print(command)

            #   subprocess.run(command, shell=True)
            #   proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            thread = pexpect.popen_spawn.PopenSpawn(command, logfile=sys.stdout.buffer)

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


