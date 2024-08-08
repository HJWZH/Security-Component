#编写环境 : Python 3.11.4 编写 : WZH
#!!! 此程序必须在大于Python 3.7.0 的环境下运行
#!!! 对于Windows10以下(不含)的系统推荐使用Python3.8.10
#!!! 对于Windows10及以上的系统推荐使用Python3.11.4
import sys
import os
import tkinter as tk
from tkinter import simpledialog
import os
import subprocess
import threading
import time
import psutil
from PIL import Image, ImageTk
from PyQt5.QtWidgets import *
import hashlib
import win32con,win32gui
from pystray import MenuItem as item
import pystray,pyautogui
from tkinter.messagebox import showerror,askyesno,showinfo,showwarning
import requests,bs4
import datetime
import webbrowser
#版本号
VERSION = 'V0.0.1'

# 获取临时运行时文件夹的路径
tmp_folder = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

# 构建图标文件的路径
icon_path = os.path.join(tmp_folder, "ICOs","KEY.ico")
LOCK_path = os.path.join(tmp_folder, "ICOs","LOCK.png")

#构建日志文件路径
log_path = os.path.join(tmp_folder, "main","running.log")

#构建日志文件
with open(log_path,'a') as log_write:
    log_write.write("")

#加载字体文件
Word_TTC = os.path.join(tmp_folder, "main","MSYHBD.TTC")
if os.path.exists(Word_TTC):
    pass
else:
    Word_TTC = "C:/Windows/Fonts/msyh.ttc" #如果字体文件被删除,使用系统字体文件
#print(icon_path)
#print(LOCK_path)

#TXT(UN&LOCK)地址
main_TXT_path = os.path.join(tmp_folder, "main")
LOCK_EXE = os.path.join(main_TXT_path, "lock-exe.txt")
WHITE_EXE = os.path.join(main_TXT_path, "white-exe.txt")
unlock_exe = []
WZH = "writer"
#UNLOCK_EXE = os.path.join(main_TXT_path, "unlock-exe.txt")
#加载密码文件
PW_KEY = os.path.join(main_TXT_path, "password-sha512.key")
#创建文件
with open(LOCK_path, 'a', encoding='UTF-8') as file:
    file.write("")
#with open(WHITE_EXE, 'a', encoding='UTF-8') as file:
#    file.write("")

#检查文件是否存在
if os.path.exists(PW_KEY):
    pass
else:#不存在则添加默认密码(000000)#SHA512加密,防止爆破
    with open(PW_KEY, 'a', encoding='UTF-8') as file:
        file.write(hashlib.sha512("000000".encode("utf-8")).hexdigest())
#with open(UNLOCK_EXE,"a", encoding='UTF-8') as file:
#    file.write("")

#获取禁用列表
with open(LOCK_EXE, 'r', encoding='UTF-8') as file:
    lock_exes_line = file.read().splitlines()
    if os.path.basename(__file__) in lock_exes_line:
        lock_exes_line.remove(os.path.basename(__file__)) #防止将自己添加在内
        lock_exes_line.append("#") #防止列表无内容发生错误
    #print(lock_exes_line)

#获取白名单,取消手动白名单,防止卡BUG
#with open(WHITE_EXE, 'r', encoding='UTF-8') as file:
#    unlock_exes_line = file.read().splitlines()
#    for unlock_exe_name in unlock_exes_line:
#        unlock_exe.append(unlock_exe_name)
unlock_exe.append(os.path.basename(__file__)) #将自己添加在白名单内
    #print(unlock_exe)
    #print(unlock_exes_line)

#日志写入
def logs_writting(level,thing):
    with open(log_path,'a') as log_write:
        log_write.write(f"{datetime.datetime.now()}\t[{level}]{thing}\n")

#获取密码SHA512值
def get_password():
    with open(PW_KEY, 'r', encoding='UTF-8') as file:
        pw_lines = file.read().splitlines()
        for pw_line in pw_lines:
            PASSWORD_SHA512 = pw_line
            return PASSWORD_SHA512
get_password()

"""#获取解禁列表
with open(UNLOCK_EXE, 'r', encoding='UTF-8') as file:
    unlock_exes_line = file.read().splitlines()
    #print(unlock_exes_line)"""

def check_process(process_name):
    """检查进程是否运行"""
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if process_name.lower() in proc.info['name'].lower():
            return proc
    return None

def kill_process(proc):
    """结束进程"""
    proc.terminate()

def start_application(app_path):
    """启动应用"""
    #subprocess.Popen(app_path, shell=True)
    process = subprocess.Popen(app_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # 监听程序执行直到结束
    return process
    
def listen_app(process,app_path,process_name):
    """监听程序"""
    stdout, stderr = process.communicate()
    #print(app_path,"\t关闭OK")
    update_unlock_exe(process_name,'remove')
    #os.system('pause')

def security_check(root, process_name, app_path):
    """安全验证界面和逻辑"""
    global LOCK_path
    password_attempts = 5
    remaining_time = 300  # 倒计时时间，单位为秒

    def verify_password():
        nonlocal password_attempts
        password = password_entry.get()
        PASSWORD_SHA512 = get_password()
        if hashlib.sha512(password.encode("utf-8")).hexdigest() == PASSWORD_SHA512:
            update_unlock_exe(process_name, 'add')
            process=start_application(app_path)
            root.destroy()
            listen_app(process,app_path,process_name)
        else:
            password_attempts -= 1
            if password_attempts <= 0:
                submit_button.config(state='disabled')
                password_entry.config(state=tk.DISABLED)
                password_entry.delete(0, tk.END)
                start_countdown()  # 启动倒计时
            else:
                password_attempts_label.config(text=f"密码错误，还有{password_attempts}次机会",fg='red')
                password_entry.delete(0, tk.END)

    def start_countdown():
        nonlocal remaining_time
        #remaining_time = 3
        submit_button.config(state='disabled')
        password_attempts_label.config(text=f"密码错误，请300秒后重试",fg='red')
        remaining_time_label.config(text=f"剩余时间：0{remaining_time // 60}:{remaining_time % 60}",fg='red')
        if remaining_time > 0:
            remaining_time -= 1
            root.after(1000, start_countdown)  # 每秒更新一次倒计时
        else:
            remaining_time = 300
            reset_button()
    
    def reset_button():
        global password_attempts
        submit_button.config(state='normal')
        password_attempts_label.config(text="")
        remaining_time_label.config(text="")
        password_entry.config(state=tk.NORMAL)
        password_attempts = 5
        #verify_password()

    title_name=f"解锁\"{process_name}\"[SC.exe]"
    root.title(title_name)
    try:
            hwnd = win32gui.FindWindow(None, title_name)  # 窗口
            # 将窗口置于最底层
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    except:
            pass
    width = 720
    height = 300
    root.geometry(f"{width}x{height}")
    # 获取屏幕宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # 计算窗口在屏幕中央的位置
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    # 将窗口移动到屏幕中央
    root.geometry("+%d+%d" % (x, y))

    left_frame = tk.Frame(root)
    left_frame.pack(side="left", fill="both")
    #left_frame.pack()
    #图像放置位置（此处代码需根据实际情况调整）
    # 加载图像
    try:
        image = Image.open(LOCK_path)
        image = image.resize((200, 200))
        photo = ImageTk.PhotoImage(image)

        # 在左侧放置Label控件显示图片
        image_label = tk.Label(left_frame, image=photo)
        image_label.image = photo  # 保持对图片的引用，避免被垃圾回收
        image_label.grid(row=0, column=0, padx=10, pady=10)
    except tk._tkinter.TclError:
        #防止无法放置图片,Bug以后解决
        pass
    
    top_label = tk.Label(root, text="此应用程序受密码保护", font=(Word_TTC, 24))
    top_label.pack()

    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    password_attempts_label = tk.Label(root, text="")
    password_attempts_label.pack()

    remaining_time_label = tk.Label(root, text="")
    remaining_time_label.pack()

    submit_button = tk.Button(root, text="确定", command=verify_password,width=10)
    submit_button.pack()

    cancel_button = tk.Button(root, text="取消", command=root.destroy,width=10)
    cancel_button.pack()

def update_unlock_exe(process_name, action):
    """更新unlock-exe.txt文件"""
    global unlock_exe
    if action == 'add':
        unlock_exe.append(process_name)
    elif action == 'remove':
        unlock_exe.remove(process_name)

def check_window(window_name):
    """检查窗口是否存在"""
    # 获取所有顶级窗口的句柄
    hwnds = []
    win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), hwnds)
    # 遍历窗口句柄，检查窗口标题是否匹配
    for hwnd in hwnds:
        if win32gui.GetWindowText(hwnd) == window_name:
            return True
    return False

def start_security_check(proc,process_name):
    app_path = proc.exe()
    kill_process(proc)
    window_name=f"解锁\"{process_name}\"[SC.exe]"
    if not check_window(window_name):
        root = tk.Tk()
        root.resizable(0,0) # 禁止拉伸窗口
        root.lift()
        root.iconbitmap(icon_path)
        root.wm_iconbitmap(icon_path)
        security_check(root, process_name, app_path)
        root.mainloop()
    else:
        pass

def monitor_processes():
    global lock_exes_line , unlock_exe
    while True:
        for process_name in lock_exes_line:
            proc = check_process(process_name)
            #print(proc)
            if proc and process_name not in unlock_exe:
                #start_security_check(proc,process_name)
                app = QApplication(sys.argv) #使用PyQt5校准窗口
                thread = threading.Thread(target=start_security_check, args=(proc, process_name))
                thread.start()
                #update_unlock_exe(process_name, 'remove')
        time.sleep(0.01)  # 等待1秒再次检查

def change_password():
    pw=pyautogui.password("请输入当前密码","SC")
    if pw=='' or pw==None:
        return 0 #空密码返回0
    else:
        hash_pw=hashlib.sha512(pw.encode("utf-8")).hexdigest()
        #获取当前密码SHA512值(更新)
        with open(PW_KEY, 'r', encoding='UTF-8') as file:
            pw_lines = file.read().splitlines()
            for pw_line in pw_lines:
                PASSWORD_SHA512 = pw_line
                break
        if hash_pw==PASSWORD_SHA512:
            rd_to_change_password=pyautogui.password("请输入要修改的密码","SC")
            rd_to_change_password_again=pyautogui.password("请再次输入要修改的密码","SC")
            if rd_to_change_password != rd_to_change_password_again:
                #apps = QApplication(sys.argv)
                #QMessageBox.critical(None, "SC提示","两次输入的密码不相同！请重试！\t\t\t\t\t")
                showerror("SC提示","两次输入的密码不相同！请重试！") #由于PyQt5在此使用容易出现线程中断,换为tk
            else :
                #清空密码文件
                with open(PW_KEY, 'w') as file:
                    file.truncate(0)
                with open(PW_KEY,'a') as file:
                    file.write(hashlib.sha512(rd_to_change_password.encode("utf-8")).hexdigest()) #写入SHA512值
                showinfo("SC提示","修改密码成果！")
            #close_program()
        else:
            #apps = QApplication(sys.argv)
            #QMessageBox.critical(None, "SC提示","密码错误！拒绝执行！\t\t\t\t\t")
            showerror("SC提示","密码错误！拒绝执行！") #由于PyQt5在此使用容易出现线程中断,换为tk
            #apps.processEvents()# 处理事件循环
            return 0  

def exit_program():
    pw=pyautogui.password("请输入密码","SC")
    if pw=='' or pw==None:
        return 0 #空密码返回0
    else:
        hash_pw=hashlib.sha512(pw.encode("utf-8")).hexdigest()
        #获取当前密码SHA512值(更新)
        PASSWORD_SHA512 = get_password()
        if hash_pw==PASSWORD_SHA512:
            ask_again=askyesno(title="SC提示", message="你确定要退出此程序吗？")
            if ask_again == True: # 选择确定为True
                os._exit(0) #使用_exit安全退出程序,防止线程崩溃以及内存溢出
            else:
                return 0

def check_update_vision():
    """更新组件"""
    try: #————————————
        res=requests.get("https://baboonassociation.pythonanywhere.com/versions/")
    except Exception as errors:
        with open(log_path,'a') as log_write:
            log_write.write(f"{datetime.datetime.now()}\t[error]{errors}\n")
        return False,errors
    else:
        res.encoding='UTF-8'
        resText=res.text
        resStr=bs4.BeautifulSoup(resText,'lxml')
        result=resStr.select('[class="SC_versions"]')
        for new in result:
            situation=new.string
            break
        return True,situation

def check_update():
    err,version_now = check_update_vision()
    if err == False:
        showerror("SC错误",f"出现错误!已记录到日志{log_path}中\n错误如下:\n{version_now}")
        yes_or_no = askyesno("SC提示",f"是否打开日志？")
        if yes_or_no == True:
            subprocess.run(['notepad.exe', log_path], shell=True) #打开日志
        else:
            return 0
    else:
        if VERSION != version_now:
            showwarning("SC警告",f"版本不匹配,可能是有新的版本发布,当前最新版本为{version_now}\n请前往(https://github.com/funnywzh/Security-Component/releases)下载")
            yes_or_no = askyesno("SC提示",f"是否前往更新网页？")
            if yes_or_no == True:
                webbrowser.open("https://github.com/funnywzh/Security-Component/releases") #打开更新网页
            else:
                return 0
        else:
            showinfo("SC提示",f"你正在使用最新版,版本号:{version_now}")
            #apps = QApplication(sys.argv)
            #QMessageBox.information(None,"SC提示",f"你正在使用最新版,版本号:{version_now}")
            #apps.processEvents()# 处理事件循环

#打开反馈网页
def bug_report():
    webbrowser.open("https://baboonassociation.pythonanywhere.com/topics/5/") #打开反馈网页

def add_exe():
    """添加永久禁用程序"""
    add_exe_name = pyautogui.prompt(text='请输入永久禁用程序名(包括后缀.exe):', title='SC添加禁用')
    if add_exe_name == None or add_exe_name == '' :
        return 0
    elif add_exe_name.endswith('.exe'): #判断后缀是否为.exe
        lock_exes_line.append(add_exe_name)
        with open(LOCK_EXE,'a') as add_lock_exe:
            add_lock_exe.write(f"\"{add_exe_name}\"\n")
        showinfo("SC提示","添加成功！")
    else:
        showerror("SC错误","无效的应用程序名！")

def remove_exe():
    """移除永久禁用程序"""
    all_lock_exes_name = "" #偷个懒,少用个.join
    for lock_exes_lines in lock_exes_line:
        all_lock_exes_name = all_lock_exes_name + "  " + lock_exes_lines 
    if lock_exes_line == [] :
        showinfo("SC提示","列表中没有禁用程序")
        return 0
    else:
        remove_exe_name = pyautogui.prompt(text=f'{all_lock_exes_name}\n请输入要解禁的应用程序(照上面写,有引号的加引号,不可一次写多项):', title='SC移除禁用')
        if remove_exe_name == None or remove_exe_name == '' :
            return 0
        elif f"{remove_exe_name}" not in lock_exes_line :
            showerror("SC错误","无效的应用程序名！")
        else:
            lock_exes_line.remove(remove_exe_name)
            all_lock_exes_name_rd_to_remove = "" #又偷个懒,少用个.join
            for lock_exes_lines in lock_exes_line:
                all_lock_exes_name_rd_to_remove = all_lock_exes_name_rd_to_remove + lock_exes_lines +"\n"
            with open(LOCK_EXE,'a') as lock_exe_write:
                lock_exe_write.truncate()
                lock_exe_write.write(all_lock_exes_name_rd_to_remove)
            showinfo("SC提示","移除成功！")

def add_temporary_exe():
    """添加临时禁用程序"""
    add_exe_name = pyautogui.prompt(text='请输入永久禁用程序名(包括后缀.exe):', title='SC添加禁用')
    if add_exe_name == None or add_exe_name == '' :
        return 0
    elif add_exe_name.endswith('.exe'): #判断后缀是否为.exe
        lock_exes_line.append(add_exe_name)
        showinfo("SC提示","添加成功！")
    else:
        showerror("SC错误","无效的应用程序名！")

def remove_temporary_exe():
    """移除临时禁用程序"""
    all_lock_exes_name = "" #偷个懒,少用个.join
    for lock_exes_lines in lock_exes_line:
        all_lock_exes_name = all_lock_exes_name + "  " + lock_exes_lines 
    if lock_exes_line == [] :
        showinfo("SC提示","列表中没有禁用程序")
        return 0
    else:
        remove_exe_name = pyautogui.prompt(text=f'{all_lock_exes_name}\n请输入要解禁的应用程序(不可一次写多项):', title='SC添加禁用')
        if remove_exe_name == None or remove_exe_name == '' :
            return 0
        elif remove_exe_name not in lock_exes_line :
            showerror("SC错误","无效的应用程序名！")
        else:
            lock_exes_line.remove(remove_exe_name)

def system_ico():
    """系统托盘图标"""
    # 创建菜单项
    menu = (item('SC核心控制台',None),
            item('更改密码',change_password),
            item('退出程序',exit_program),
            item('检查更新',check_update),
            item('BUG反馈',bug_report),
            item('添加永久禁用程序',add_exe),
            item('移除永久禁用程序',remove_exe),
            item('添加临时禁用程序',add_temporary_exe),
            item('移除临时禁用程序',remove_temporary_exe),)
    # 创建系统托盘图标
    icon = pystray.Icon("SC", Image.open(icon_path), "SC核心控制台", menu)
    # 运行系统托盘图标
    icon.run()

#system_ico()
threading.Thread(target=system_ico).start()
monitor_processes()
#threading.Thread(target=monitor_processes).start()
