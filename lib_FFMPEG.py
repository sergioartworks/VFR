from pathlib import Path
import re
import subprocess
import pexpect
from pexpect.popen_spawn import PopenSpawn


### 共通定数定義 ###
SUCCESS = 0
FAIL = -1
ABORT = -2

YES = 1
NO = 0

AR_KEEP = 0
AR_16_9 = 1
AR_4_3 = 2
####################


def convert(folder_path, file_name, start_time, end_time, aspect_ratio, is_reEncode):
    # フォルダ内のファイル一覧
    input_dir = Path(folder_path)
    input_files = sorted(input_dir.glob("**/*"))
    output_file = file_name

    index = 0
    line = ''
    duration_total = 0

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
    subprocess.run(command, shell=True)

    # エラー判定
    path = Path(output_file)
    if path.stat().st_size == 0:
        ret = FAIL
    else:
        ret = SUCCESS

    return ret


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
