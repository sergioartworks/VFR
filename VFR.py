import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import lib_FFMPEG


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


def ask_folder1():
    """　タブ１　フォルダ指定
    """
    path = filedialog.askdirectory(initialdir="F:\DVD2MPG")
    folder_path1.set(path)


def ask_folder2():
    """　タブ２　フォルダ指定
    """
    path = filedialog.askdirectory(initialdir="F:\DVD2MPG")
    folder_path2.set(path)


def ask_filename1():
    """　タブ１　ファイル名指定
    """
    name = filedialog.asksaveasfilename(initialdir="F:\DVD2MPG", initialfile="output.mp4", filetypes=[("MP4 files", "*.mp4")], defaultextension=".mp4")
    file_name1.set(name)


def ask_filename2():
    """　タブ２　ファイル名指定
    """
    name = filedialog.asksaveasfilename(initialdir="F:\DVD2MPG", initialfile="output.mp4", filetypes=[("MP4 files", "*.mp4")], defaultextension=".mp4")
    file_name2.set(name)


def ask_filename3_1():
    """　タブ３　ファイル名指定①
    """
    name = filedialog.askopenfilename(initialdir="F:\DVD2MPG\input_file", filetypes=[("MP4 files", "*.mp4")], defaultextension=".mp4")
    file_name3_1.set(name)


def ask_filename3_2():
    """　タブ３　ファイル名指定②
    """
    name = filedialog.asksaveasfilename(initialdir="F:\DVD2MPG", initialfile="output.mp4", filetypes=[("MP4 files", "*.mp4")], defaultextension=".mp4")
    file_name3_2.set(name)


def ask_filename4_1():
    """　タブ４　ファイル名指定①
    """
    name = filedialog.askopenfilename(initialdir="F:\DVD2MPG\input_file", filetypes=[("MP4 files", "*.mp4")], defaultextension=".mp4")
    file_name4_1.set(name)


def ask_filename4_2():
    """　タブ４　ファイル名指定②
    """
    name = filedialog.asksaveasfilename(initialdir="F:\DVD2MPG", initialfile="output.mp4", filetypes=[("MP4 files", "*.mp4")], defaultextension=".mp4")
    file_name4_2.set(name)


def convertMP4():
    """ 処理実行
    """
    input_dir = folder_path1.get()
    output_file = file_name1.get()
    s_time = start_time1.get()
    e_time = end_time1.get()
    apt = aspect1.get()
    is_re_enc = is_reEncode1.get()

    if not input_dir or not output_file:
        return
    # 変換実行
    ret = lib_FFMPEG.convert(input_dir, output_file, s_time, e_time, apt, is_re_enc)
    # メッセージボックス
    if ret == SUCCESS:
        messagebox.showinfo('完了', '変換が完了しました。')
        # 再生
        if is_playVF1.get() == YES:
            subprocess.Popen(['start', output_file], shell=True)
    else:
        messagebox.showinfo('完了', '変換に失敗しました。')


def merge():
    """ 処理実行
    """
    input_dir = folder_path2.get()
    output_file = file_name2.get()

    if not input_dir or not output_file:
        return
    # 結合実行
    ret = lib_FFMPEG.merge(input_dir, output_file,)
    # メッセージボックス
    if ret == SUCCESS:
        messagebox.showinfo('完了', '結合が完了しました。')
        # 再生
        if is_playVF2.get() == YES:
            subprocess.Popen(['start', output_file], shell=True)
    else:
        messagebox.showinfo('完了', '結合に失敗しました。')
    

def cut():
    """ 処理実行
    """
    input_file = file_name3_1.get()
    output_file = file_name3_2.get()
    s_time = start_time3.get()
    e_time = end_time3.get()

    if not input_file or not output_file:
        return
    # 結合実行
    ret = lib_FFMPEG.cut(input_file, output_file, s_time, e_time)
    # メッセージボックス
    if ret == SUCCESS:
        messagebox.showinfo('完了', 'カットが完了しました。')
        # 再生
        if is_playVF3.get() == YES:
            subprocess.Popen(['start', output_file], shell=True)
    else:
        messagebox.showinfo('完了', 'カットに失敗しました。')
    

def change_aspect_ratio():
    """ 処理実行
    """
    input_file = file_name4_1.get()
    output_file = file_name4_2.get()
    apt = aspect4.get()


    if not input_file or not output_file:
        return
    # 結合実行
    ret = lib_FFMPEG.changeAspectRatio(input_file, output_file, apt)
    # メッセージボックス
    if ret == SUCCESS:
        messagebox.showinfo('完了', 'アスペクト変更が完了しました。')
        # 再生
        if is_playVF4.get() == YES:
            subprocess.Popen(['start', output_file], shell=True)
    else:
        messagebox.showinfo('完了', 'アスペクト変更に失敗しました。')
    

# メインウィンドウ
main_win = tkinter.Tk()
main_win.resizable(0,0)
main_win.title("VFR - Video File Remaker")
main_win.update_idletasks() 
width = 600 
height = 450 
x = (main_win.winfo_screenwidth() //2) - (width //2) 
y = (main_win.winfo_screenheight() //2) - (height //2) 
main_win.geometry("%dx%d+%d+%d" % (width, height, x, y))
main_win.configure(background="#d9d9d9")

# スタイル
#style = ttk.Style()
#style.configure(".",font=("",12))

# メインフレーム
tabControl = ttk.Notebook(main_win) # Create Tab Control
tab1 = ttk.Frame(tabControl) # Create a Tab
tab1.grid(column=0, row=0, sticky=tkinter.NSEW, padx=0, pady=0)
tabControl.add(tab1, text='MP4変換') # Add the Tab
tab2 = ttk.Frame(tabControl) # Create second Tab
tab2.grid(column=0, row=0, sticky=tkinter.NSEW, padx=0, pady=0)
tabControl.add(tab2, text='結合') # Add second Tab
tab3 = ttk.Frame(tabControl) # Create second Tab
tab3.grid(column=0, row=0, sticky=tkinter.NSEW, padx=0, pady=0)
tabControl.add(tab3, text='カット') # Add second Tab
tab4 = ttk.Frame(tabControl) # Create second Tab
tab4.grid(column=0, row=0, sticky=tkinter.NSEW, padx=0, pady=0)
tabControl.add(tab4, text='アスペクト比変更') # Add second Tab
tabControl.pack(expand=1, fill='both') # Pack to make visible

###
#######  タブ１  ###############
###

# パラメータ
folder_path1 = tkinter.StringVar()
file_name1 = tkinter.StringVar()
start_time1 = tkinter.StringVar()
end_time1 = tkinter.StringVar()
aspect1 = tkinter.IntVar()
is_reEncode1 = tkinter.IntVar()
is_playVF1 = tkinter.IntVar()

# ウィジェット（フォルダ名）
folder_label1 = ttk.Label(tab1, text="入力フォルダ:")
folder_box1 = ttk.Entry(tab1, textvariable=folder_path1)
folder_box1.insert(0, "F:\DVD2MPG\input_file")
folder_btn1 = ttk.Button(tab1, text="参照", command=ask_folder1)

# ウィジェット（ファイル名）
filename_label1 = ttk.Label(tab1, text="出力ファイル:")
filename_box1 = ttk.Entry(tab1, textvariable=file_name1)
filename_box1.insert(0, "F:\DVD2MPG\output.mp4")
filename_btn1 = ttk.Button(tab1, text="参照", command=ask_filename1)

# ウィジェット（セパレータ）
separator1 = ttk.Separator(tab1)

# ウィジェット（開始時間）
starttime_label1 = ttk.Label(tab1, text="開始時間:")
starttime_box1 = ttk.Entry(tab1, textvariable=start_time1)

# ウィジェット（終了時間）
endtime_label1 = ttk.Label(tab1, text="終了時間:")
endtime_box1 = ttk.Entry(tab1, textvariable=end_time1)

# ウィジェット（アスペクト比変更）
aspectframe_labelframe1 = ttk.LabelFrame(tab1, relief='raised', text="アスペクト比")
aspect_keep_radiobutton1 = ttk.Radiobutton(aspectframe_labelframe1, text="維持する", value=AR_KEEP, variable=aspect1)
aspect_16_9_radiobutton1 = ttk.Radiobutton(aspectframe_labelframe1, text="16:9", value=AR_16_9, variable=aspect1)
aspect_4_3_radiobutton1 = ttk.Radiobutton(aspectframe_labelframe1, text="4:3", value=AR_4_3, variable=aspect1)
aspect1.set(AR_KEEP)

# ウィジェット（チェックボタン）
reEncode_checkbutton1 = ttk.Checkbutton(tab1, text="音声を再エンコードする", variable=is_reEncode1, onvalue=YES, offvalue=NO)
playVF_checkbutton1 = ttk.Checkbutton(tab1, text="変換終了後に出力ファイルを再生する", variable=is_playVF1, onvalue=YES, offvalue=NO)
is_reEncode1.set(NO)
is_playVF1.set(YES)

# ウィジェット（実行ボタン）
app_btn1 = ttk.Button(tab1, text="実行", command=convertMP4)

# ウィジェットの配置
folder_label1.place(relx=0.05, rely=0.089, height=31, width=74)
folder_box1.place(relx=0.183, rely=0.089, height=31, relwidth=0.67)
folder_btn1.place(relx=0.867, rely=0.089, height=31, width=57)
filename_label1.place(relx=0.05, rely=0.178, height=31, width=74)
filename_box1.place(relx=0.183, rely=0.178, height=31, relwidth=0.67)
filename_btn1.place(relx=0.867, rely=0.178, height=31, width=57)
separator1.place(relx=0.05, rely=0.32,  relwidth=0.915)
starttime_label1.place(relx=0.067, rely=0.4, height=31, width=64)
starttime_box1.place(relx=0.183, rely=0.4, height=27, relwidth=0.173)
endtime_label1.place(relx=0.067, rely=0.489, height=31, width=64)
endtime_box1.place(relx=0.183, rely=0.489, height=27, relwidth=0.173)
aspectframe_labelframe1.place(relx=0.517, rely=0.378, relheight=0.278, relwidth=0.367)
aspect_keep_radiobutton1.place(relx=0.091, rely=0.16, relheight=0.28, relwidth=0.586, bordermode='ignore')
aspect_16_9_radiobutton1.place(relx=0.091, rely=0.4, relheight=0.28, relwidth=0.445, bordermode='ignore')
aspect_4_3_radiobutton1.place(relx=0.091, rely=0.64, relheight=0.28, relwidth=0.277, bordermode='ignore')
reEncode_checkbutton1.place(relx=0.1, rely=0.667, relheight=0.078, relwidth=0.3)
playVF_checkbutton1.place(relx=0.1, rely=0.733, relheight=0.078, relwidth=0.4)
app_btn1.place(relx=0.417, rely=0.844, height=44, width=107)


###
#######  タブ２  ###############
###

# パラメータ
folder_path2 = tkinter.StringVar()
file_name2 = tkinter.StringVar()
is_playVF2 = tkinter.StringVar()

# ウィジェット（フォルダ名）
folder_label2 = ttk.Label(tab2, text="入力フォルダ:")
folder_box2 = ttk.Entry(tab2, textvariable=folder_path2)
folder_box2.insert(0, "F:\DVD2MPG\input_file")
folder_btn2 = ttk.Button(tab2, text="参照", command=ask_folder2)

# ウィジェット（ファイル名）
filename_label2 = ttk.Label(tab2, text="出力ファイル:")
filename_box2 = ttk.Entry(tab2, textvariable=file_name2)
filename_box2.insert(0, "F:\DVD2MPG\output.mp4")
filename_btn2 = ttk.Button(tab2, text="参照", command=ask_filename2)

# ウィジェット（セパレータ）
separator2 = ttk.Separator(tab2)

# ウィジェット（チェックボタン）
playVF_checkbutton2 = ttk.Checkbutton(tab2, text="変換終了後に出力ファイルを再生する", variable=is_playVF2, onvalue=YES, offvalue=NO)
is_playVF2.set(YES)

# ウィジェット（実行ボタン）
app_btn2 = ttk.Button(tab2, text="実行", command=merge)

# ウィジェットの配置
folder_label2.place(relx=0.05, rely=0.089, height=31, width=74)
folder_box2.place(relx=0.183, rely=0.089, height=31, relwidth=0.67)
folder_btn2.place(relx=0.867, rely=0.089, height=31, width=57)
filename_label2.place(relx=0.05, rely=0.178, height=31, width=74)
filename_box2.place(relx=0.183, rely=0.178, height=31, relwidth=0.67)
filename_btn2.place(relx=0.867, rely=0.178, height=31, width=57)
separator2.place(relx=0.05, rely=0.32,  relwidth=0.915)
playVF_checkbutton2.place(relx=0.1, rely=0.733, relheight=0.078, relwidth=0.4)
app_btn2.place(relx=0.417, rely=0.844, height=44, width=107)


###
#######  タブ３  ###############
###

# パラメータ
file_name3_1 = tkinter.StringVar()
file_name3_2 = tkinter.StringVar()
start_time3 = tkinter.StringVar()
end_time3 = tkinter.StringVar()
is_playVF3 = tkinter.StringVar()

# ウィジェット（ファイル名）
filename_label3_1 = ttk.Label(tab3, text="入力ファイル:")
filename_box3_1 = ttk.Entry(tab3, textvariable=file_name3_1)
filename_box3_1.insert(0, "F:\DVD2MPG\input_file")
filename_btn3_1 = ttk.Button(tab3, text="参照", command=ask_filename3_1)

# ウィジェット（ファイル名）
filename_label3_2 = ttk.Label(tab3, text="出力ファイル:")
filename_box3_2 = ttk.Entry(tab3, textvariable=file_name3_2)
filename_box3_2.insert(0, "F:\DVD2MPG\output.mp4")
filename_btn3_2 = ttk.Button(tab3, text="参照", command=ask_filename3_2)

# ウィジェット（セパレータ）
separator3 = ttk.Separator(tab3)

# ウィジェット（開始時間）
starttime_label3 = ttk.Label(tab3, text="開始時間:")
starttime_box3 = ttk.Entry(tab3, textvariable=start_time3)

# ウィジェット（終了時間）
endtime_label3 = ttk.Label(tab3, text="終了時間:")
endtime_box3 = ttk.Entry(tab3, textvariable=end_time3)

# ウィジェット（チェックボタン）
playVF_checkbutton3 = ttk.Checkbutton(tab3, text="変換終了後に出力ファイルを再生する", variable=is_playVF3, onvalue=YES, offvalue=NO)
is_playVF3.set(YES)

# ウィジェット（実行ボタン）
app_btn3 = ttk.Button(tab3, text="実行", command=cut)

# ウィジェットの配置
filename_label3_1.place(relx=0.05, rely=0.089, height=31, width=74)
filename_box3_1.place(relx=0.183, rely=0.089, height=31, relwidth=0.67)
filename_btn3_1.place(relx=0.867, rely=0.089, height=31, width=57)
filename_label3_2.place(relx=0.05, rely=0.178, height=31, width=74)
filename_box3_2.place(relx=0.183, rely=0.178, height=31, relwidth=0.67)
filename_btn3_2.place(relx=0.867, rely=0.178, height=31, width=57)
separator3.place(relx=0.05, rely=0.32,  relwidth=0.915)
starttime_label3.place(relx=0.067, rely=0.4, height=31, width=64)
starttime_box3.place(relx=0.183, rely=0.4, height=27, relwidth=0.173)
endtime_label3.place(relx=0.067, rely=0.489, height=31, width=64)
endtime_box3.place(relx=0.183, rely=0.489, height=27, relwidth=0.173)
playVF_checkbutton3.place(relx=0.1, rely=0.733, relheight=0.078, relwidth=0.4)
app_btn3.place(relx=0.417, rely=0.844, height=44, width=107)


###
#######  タブ４  ###############
###

# パラメータ
file_name4_1 = tkinter.StringVar()
file_name4_2 = tkinter.StringVar()
aspect4 = tkinter.StringVar()
is_playVF4 = tkinter.StringVar()

# ウィジェット（ファイル名）
filename_label4_1 = ttk.Label(tab4, text="入力ファイル:")
filename_box4_1 = ttk.Entry(tab4, textvariable=file_name4_1)
filename_box4_1.insert(0, "F:\DVD2MPG\input_file")
filename_btn4_1 = ttk.Button(tab4, text="参照", command=ask_filename4_1)

# ウィジェット（ファイル名）
filename_label4_2 = ttk.Label(tab4, text="出力ファイル:")
filename_box4_2 = ttk.Entry(tab4, textvariable=file_name4_2)
filename_box4_2.insert(0, "F:\DVD2MPG\output.mp4")
filename_btn4_2 = ttk.Button(tab4, text="参照", command=ask_filename4_2)

# ウィジェット（セパレータ）
separator4 = ttk.Separator(tab4)

# ウィジェット（アスペクト比変更）
aspectframe_labelframe4 = ttk.LabelFrame(tab4, relief='raised', text="アスペクト比")
aspect_16_9_radiobutton4 = ttk.Radiobutton(aspectframe_labelframe4, text="16:9", value=AR_16_9, variable=aspect4)
aspect_4_3_radiobutton4 = ttk.Radiobutton(aspectframe_labelframe4, text="4:3", value=AR_4_3, variable=aspect4)
aspect4.set(AR_16_9)

# ウィジェット（チェックボタン）
playVF_checkbutton4 = ttk.Checkbutton(tab4, text="変換終了後に出力ファイルを再生する", variable=is_playVF4, onvalue=YES, offvalue=NO)
is_playVF4.set(YES)

# ウィジェット（実行ボタン）
app_btn4 = ttk.Button(tab4, text="実行", command=change_aspect_ratio)

# ウィジェットの配置
filename_label4_1.place(relx=0.05, rely=0.089, height=31, width=74)
filename_box4_1.place(relx=0.183, rely=0.089, height=31, relwidth=0.67)
filename_btn4_1.place(relx=0.867, rely=0.089, height=31, width=57)
filename_label4_2.place(relx=0.05, rely=0.178, height=31, width=74)
filename_box4_2.place(relx=0.183, rely=0.178, height=31, relwidth=0.67)
filename_btn4_2.place(relx=0.867, rely=0.178, height=31, width=57)
separator4.place(relx=0.05, rely=0.32,  relwidth=0.915)
aspectframe_labelframe4.place(relx=0.517, rely=0.378, relheight=0.23, relwidth=0.367)
aspect_16_9_radiobutton4.place(relx=0.091, rely=0.24, relheight=0.28, relwidth=0.445, bordermode='ignore')
aspect_4_3_radiobutton4.place(relx=0.091, rely=0.54, relheight=0.28, relwidth=0.277, bordermode='ignore')
playVF_checkbutton4.place(relx=0.1, rely=0.733, relheight=0.078, relwidth=0.4)
app_btn4.place(relx=0.417, rely=0.844, height=44, width=107)


# 配置設定
main_win.columnconfigure(0, weight=1)
main_win.rowconfigure(0, weight=1)
tab1.columnconfigure(1, weight=1)
tab2.columnconfigure(1, weight=1)

main_win.mainloop()
