# -*- coding: utf-8 -*-
"""
2004/5/21 修正bug，合并视频时，如果直接输入 q 系统将会报错！用户仅输入一个文件时，也会报错。

"""

import tkinter as tk
from tkinter import ttk, messagebox,simpledialog
from PIL import ImageDraw, ImageTk, Image
import time
import pyautogui
import argparse  
import os
import subprocess
import sys
import re

#先通过下面代码显示版本信息
def get_version():
    version = "VideoEditor version 1.0. Published in May_20. 2024  \n Author: Michael Wang"
    return version
parser = argparse.ArgumentParser()
parser.add_argument('--version', '-v', action='version', version=get_version(), help='Display version information')
args = parser.parse_args()


def show_dialog(*args):  #这里处理的是 抠图选项
        global window
        if cropTF_var.get()==0: return
        if treatment_window.state()=="normal": treatment_window.withdraw()
        def on_ok():  
                global rect_width,rect_height,start_x,start_y, end_clicked, start_clicked, window
                selected_item = combobox.get()  
                sss=selected_item
                print("line 37 your slection is sss=",selected_item)
                root.destroy()  
                
                if sss == "自定义":
                        start_clicked = False
                        end_clicked = False
                        rect_width, rect_height = 50, 50
                        catch()
                else:
                        ss=sss.split(":")[1].split("x")
                        rect_width=int(ss[0].strip())
                        rect_height=int(ss[1].strip())
                        print(f"您选择的是{rect_width}x{rect_height}，实际在图中画的尺寸为：{int(rect_width/ratio)}x{int(rect_height/ratio)}")
                        start_clicked = False
                        end_clicked = None
                        catch()
        
        def on_cancel():  
                root.destroy()  
                window.deiconify()
        
        root = tk.Toplevel()  
        root.title("如何抠图")  
        crop_label=tk.Label(root,text="请选择抠图方式：")
        crop_label.pack(padx=10,pady=10,anchor="w")
        
        value=["1080p: 1920x1080", "720p: 1280x720", "480p: 640x480","自定义"]
        combobox = ttk.Combobox(root, values=value)  
        combobox.current(3)  # 设置默认选中的项  
        combobox.pack(padx=10, pady=0)  
        ok_button = tk.Button(root, text="确定", command=on_ok)  
        ok_button.pack(side=tk.RIGHT, padx=5, pady=10)  
                
def catch():
        window.bind('<Motion>', on_mouse_draw)  
        window.bind('<Button-1>', on_mouse_clicked)   
        window.deiconify()

def on_mouse_move(event):  
        global mouse_pos
        mouse_pos_lable.config(text=f"ratio={round(ratio,2)}，鼠标位置为：{event.x}x{event.y}")
                

def on_mouse_draw(event):  
        global start_x,start_y
        if start_clicked == False:  # 确定 矩形起始点
                xxx, yyy = event.x, event.y   
                draw_rect(xxx, yyy, 111, 111)  # 后两个参数用global值
        if start_clicked == True and end_clicked == False:  # 确定矩形结束点
                xxx, yyy = event.x, event.y
                if xxx<=start_x: xxx = start_x
                if yyy<= start_y: yyy = start_y
                draw_rect(start_x, start_y, xxx, yyy)
                
def draw_rect(xx, yy,xxx,yyy):  
        global image2
        frame_copy=image2.copy()
        #frame_copy = frame_image.copy()  
        # 在副本上绘制矩形  
        my_draw = ImageDraw.Draw(frame_copy)  
        if start_clicked == False:  # 确定 矩形起始点
                my_draw.rectangle((xx, yy, int(rect_width/ratio) + xx, int(rect_height/ratio) + yy), outline="blue", width=3)  #矩形需要按视频图片比例缩小 ratio
        if start_clicked == True and end_clicked == False:  # 确定矩形结束点
                my_draw.rectangle((xx, yy, xxx, yyy), outline="blue", width=3)  
        tk_image = ImageTk.PhotoImage(frame_copy)  
        image_label.config(image=tk_image)  
        image_label.image = tk_image 

def on_mouse_clicked(event):  
        global start_clicked, end_clicked, start_x, start_y,rect_width,rect_height,effective_rect_width,effective_rect_height,effective_start_x,effective_start_y

        if start_clicked == False and end_clicked == None:      # 非自定义 分辨率已经选定，满足此条件 鼠标第一次点击确定起始点，然后就结束画矩形动作。 
                mouse_x, mouse_y = event.x, event.y  
                draw_rect(mouse_x,mouse_y,111,111)                  # 画最后一次矩形，注意，此时，后两个参数用不到。
                start_x,start_y = mouse_x, mouse_y
                
                effective_start_x=int(start_x*ratio)
                effective_start_y=int(start_y*ratio)
                effective_rect_width=int(rect_width)
                effective_rect_height=int(rect_height)
                start_clicked = True
                stop_draw_rect()
                
        elif start_clicked == False and end_clicked == False:   # 自定义 分辨率模式，第一次鼠标点击，起始点坐标 start_x, _y 固定
                start_clicked = True  
                mouse_x, mouse_y = event.x, event.y    
                start_x,start_y = mouse_x, mouse_y
                
                effective_start_x=int(start_x*ratio)
                effective_start_y=int(start_y*ratio)
        elif start_clicked == True and end_clicked == False:    # 自定义 分辨率模式，第二次鼠标点击，矩形结束点坐标 end_x, _y 固定
                end_clicked = True
                mouse_x, mouse_y = event.x, event.y  
                end_x,end_y = mouse_x, mouse_y
                draw_rect(111,111,end_x,end_y)                  # 画最后一次矩形，注意，此时，前两个参数用不到。
                rect_width = end_x - start_x
                rect_height = end_y - start_y
                
                effective_rect_width=int(rect_width*ratio)
                effective_rect_height=int(rect_height*ratio)
                end_clicked = True
                stop_draw_rect()
        
def stop_draw_rect():    
        global effective_rect_height,effective_rect_width,effective_start_x,effective_start_y,tart_crop,effective_height,effective_width
        time.sleep(1)
        window.unbind('<Motion>')  
        window.unbind('<Button-1>')
        window.withdraw()
        
        if (effective_start_x+effective_rect_width)>video_width:
                effective_rect_width=video_width-effective_start_x
                str1="您的抠图宽度超出视频范围，为您取至边界"
        else:
                str1=""
        if effective_rect_width % 2 != 0:
                effective_rect_width = effective_rect_width - 1           
                
        if (effective_start_y+effective_rect_height)>video_height:
                effective_rect_height=video_height-effective_start_y
                str2="您的抠图高度超出视频范围，为您取至边界"  
        else:
                str2=""
        if effective_rect_height % 2 !=0:
                effective_rect_height = effective_rect_height - 1       
                
        response=messagebox.askquestion("请问：",str1+str2+f"\n最终抠图大小为：{effective_rect_width}x{effective_rect_height}；抠图起始点为：{effective_start_x}x{effective_start_y}; 是否继续？")    
        if response=="no":
                window.deiconify()
                return
        
        #抠图形成新视频(effective_start_x, effective_start_y,effective_rect_width,effective_rect_height,input_file, output_file)
        print("line 168, 扣图参数", effective_start_x, effective_start_y,effective_rect_width,effective_rect_height,input_file, output_file)
        effective_width=effective_rect_width
        effective_height=effective_rect_height
        print("line 172, effective width and height is: ",effective_width,effective_height)
        treatment_window.deiconify()

def create_show_window():
        global total_frames, duration, label0_show,JobOn_window,label2_show,exit_button,label1_show
        now = time.localtime()  
        # 获取时、分、秒  
        hour = now.tm_hour  
        minute = now.tm_min  
        second = now.tm_sec 
        JobOn_window=tk.Toplevel()
        
        label0_show=tk.Label(JobOn_window,justify="left")
        label0_show.pack(padx=15,pady=15)
        
        label1_show=tk.Label(JobOn_window,justify="left")
        label1_show.pack(padx=15,pady=15)
        
        label1_show.config(foreground="blue",text=f"视频共有 {total_frames} 帧, 播放时间：{int(duration)} 秒；现在时间是：{hour}:{minute}:{second}"
                        +"\n视频处理需要播放时间的：1/4--1/10, 具体取决于图片大小和计算机性能"
                        +"\n视频处理进行中，请不要关闭窗口.........")
        
        label2_show=tk.Label(JobOn_window,font=("Arial",30), foreground="green")
        label2_show.pack(padx=15,pady=30)
        
        exit_button=tk.Button(JobOn_window,text="退出",foreground="blue",background="yellow",command=window.destroy)
        exit_button.pack_forget()
        
        JobOn_window.update()
        
def treatment_method():
        global cropTF_var,size_entry,rotate_var,rotate_method_var,mirror_var,canvas_var,timing_var,canvas_size_entry,canvas_color_entry
        global size_entry,start_entry,duration_entry,rotate_method_radiobuttons,resizeTF_var,treatment_window,crf_entry,past_entry,size_label,canvas_label
        treatment_window=tk.Toplevel()
        treatment_window.title(f"视频文件处理---条件设定！")
        treatment_window.geometry("760x650+300+200")
        treatment_window.configure(bg="#004040") 

        cropTF_var = tk.IntVar(value=0)  # 初始化为0，表示未选择  读取结果：choice = cropTF_var.get() 
        cropTF_label = tk.Label(treatment_window, text="您是否要抠图？",foreground="blue")  
        cropTF_label.place(x=50,y=15)     
        # 添加Radiobutton  
        tk.Radiobutton(treatment_window, text="是", variable=cropTF_var, value=1).place(x=480,y=10)  
        tk.Radiobutton(treatment_window, text="否", variable=cropTF_var, value=0).place(x=600,y=10)   
        
        cropTF_var.trace("w",show_dialog)
        
        resizeTF_var=tk.IntVar(value=0)
        resizeTF_label = tk.Label(treatment_window, text="您是否改变输出分辨率？",foreground="blue")  
        resizeTF_label.place(x=50,y=55)     
        # 添加Radiobutton  
        tk.Radiobutton(treatment_window, text="是", variable=resizeTF_var, value=1).place(x=480,y=50)  
        tk.Radiobutton(treatment_window, text="否", variable=resizeTF_var, value=0).place(x=600,y=50) 
        
        size_label=tk.Label(treatment_window,font=("Segoe UI",8),text=f"*原视频分辨率为：{video_width}x{video_height}，请输入新分辨率：")
        size_label.place(x=100,y=87)
        size_entry=tk.Entry(treatment_window,disabledbackground="gray",font=("Segoe UI",8))
        size_entry.insert(tk.END, f"{video_width}x{video_height}")
        size_entry.config(state="disabled")
        size_entry.place(x=480,y=87)
        
        resizeTF_var.trace("w",update_resize_method)
        
        rotate_var = tk.IntVar(value=0)  
        rotate_label = tk.Label(treatment_window, text="输出是否需要旋转？",foreground="blue")  
        rotate_label.place(x=50,y=130)      
        tk.Radiobutton(treatment_window, text="是", variable=rotate_var, value=1).place(x=480,y=125)  
        tk.Radiobutton(treatment_window, text="否", variable=rotate_var, value=0).place(x=600,y=125)  
        
        # 创建标签和Radiobutton  
        rotate_method_label = tk.Label(treatment_window,font=("Segoe UI",8), text="选择旋转方式：")  
        rotate_method_label.place(x=100, y=168)  
        
        rotate_method_var = tk.IntVar(value=0)  
        # 创建四个Radiobutton，每个都关联到同一个IntVar变量但value不同  
        rotate_method_radiobuttons = [
                tk.Radiobutton(treatment_window,font=("Segoe UI",8), text="顺90+垂直翻转", variable=rotate_method_var, state="disabled",background="gray", value=0),
                tk.Radiobutton(treatment_window, font=("Segoe UI",8),text="顺90度", variable=rotate_method_var, state="disabled",background="gray", value=1),
                tk.Radiobutton(treatment_window, font=("Segoe UI",8),text="逆90度", variable=rotate_method_var, state="disabled",background="gray", value=2),
                tk.Radiobutton(treatment_window, font=("Segoe UI",8),text="逆90度+垂直翻转", variable=rotate_method_var, state="disabled",background="gray", value=3)
                ]
        
        # 将Radiobutton放置到窗口中
        for i, radiobutton in enumerate(rotate_method_radiobuttons):
                if i == 0: x = 225
                elif i == 1: x = 370
                elif i == 2: x = 460
                else: x = 550
                radiobutton.place(x=x, y=165)

        # 监听rotate_var变量的变化
        rotate_var.trace("w", lambda *args: update_rotate_method_state(rotate_method_radiobuttons))


        
        #transpose=0：顺时针旋转90度并垂直翻转。1：顺时针旋转90度。2：逆时针旋转90度。3：逆时针旋转90度并垂直翻转。
        
        mirror_var = tk.IntVar(value=0)  
        mirror_label = tk.Label(treatment_window, text="输出是否需要水平镜像？",foreground="blue")  
        mirror_label.place(x=50,y=208)     
        tk.Radiobutton(treatment_window, text="是", variable=mirror_var, value=1).place(x=480,y=203)  
        tk.Radiobutton(treatment_window, text="否", variable=mirror_var, value=0).place(x=600,y=203)  
        
        crf_label=tk.Label(treatment_window,text="请选择输出压缩比 (通常: 18-28，默认：23)",foreground="blue")
        crf_label.place(x=50,y=248)
        crf_entry=tk.Entry(treatment_window)
        crf_entry.insert(tk.END, "23")
        crf_entry.place(x=480,y=248)
        
        
        canvas_var = tk.IntVar(value=0)  
        canvas_label = tk.Label(treatment_window, text=f"是否贴入画布？(图片尺寸：{video_width}x{video_height})",foreground="blue")  
        canvas_label.place(x=50,y=288)     
        tk.Radiobutton(treatment_window, text="是", variable=canvas_var, value=1).place(x=480,y=285)  
        tk.Radiobutton(treatment_window, text="否", variable=canvas_var, value=0).place(x=600,y=285)  
        
        canvas_size_label=tk.Label(treatment_window,font=("Segoe UI",8),text="*画布尺寸：")
        canvas_size_label.place(x=100,y=323)
        canvas_size_entry=tk.Entry(treatment_window,font=("Segoe UI",8),disabledbackground="gray",width=10)
        canvas_size_entry.insert(tk.END, f"{video_width}x{video_height}")
        canvas_size_entry.config(state="disabled")
        canvas_size_entry.place(x=225,y=324)
        
        canvas_color_label=tk.Label(treatment_window,font=("Segoe UI",8),text="*画布颜色：")
        canvas_color_label.place(x=400,y=323)
        canvas_color_entry=tk.Entry(treatment_window,font=("Segoe UI",8),disabledbackground="gray",width=10)
        canvas_color_entry.insert(tk.END, f"000000")
        canvas_color_entry.config(state="disabled")
        canvas_color_entry.place(x=500,y=324)
        
        past_label = tk.Label(treatment_window,font=("Segoe UI",8), text="*贴入画布位置")  
        past_label.place(x=100,y=358)     
        past_entry=tk.Entry(treatment_window,font=("Segoe UI",8),disabledbackground="gray",width=10)
        past_entry.insert(tk.END,"中心粘贴")
        past_entry.config(state="disabled")
        past_entry.place(x=225,y=359)
        
        canvas_var.trace("w", update_canvas_property)
        
        timing_var = tk.IntVar(value=0)  
        timing_label = tk.Label(treatment_window, text=f"是否依时间裁切？(现视频：{round(duration,2)}) 秒",foreground="blue")  
        timing_label.place(x=50,y=398)     
        tk.Radiobutton(treatment_window, text="是", variable=timing_var, value=1).place(x=480,y=395)  
        tk.Radiobutton(treatment_window, text="否", variable=timing_var, value=0).place(x=600,y=395)  
        
        start_label=tk.Label(treatment_window,font=("Segoe UI",8),text="*开始时间：")
        start_label.place(x=100,y=433)
        start_entry=tk.Entry(treatment_window,font=("Segoe UI",8),disabledbackground="gray",width=12)
        start_entry.insert(tk.END, "00:00:00")
        start_entry.config(state="disabled")
        start_entry.place(x=225,y=434)
        duration_label=tk.Label(treatment_window,font=("Segoe UI",8),text="*持续时间：")
        duration_label.place(x=400,y=433)
        duration_entry=tk.Entry(treatment_window,font=("Segoe UI",8),disabledbackground="gray",width=12)
        duration_entry.insert(tk.END, f"{round(duration,2)}")
        duration_entry.config(state="disabled")
        duration_entry.place(x=500,y=434)
        
        timing_var.trace("w",update_time_cut)
        
        explain_text=tk.Text(treatment_window,height=5,width=124,relief="flat")
        #explain_text=tk.Text(treatment_window,height=5,width=94,relief="flat")        #高分辨率屏 width=94        
        explain_text.config(font=("Segoe UI",7),foreground="black",background="#EEEEEE")
        explain_text.insert(tk.END,"*分辨率输入格式：输入两个正整数以 ‘x’ 隔开。也可以只输入一个正整数和 ‘-1’，‘-1’ 维度将会由软件按比例自动设置！"
                        +"\n*画布尺寸：输入两个正整数以 ‘x’ 隔开。注意画布尺寸要大于图片尺寸加放置位置的偏移量！"
                        +"\n*画布颜色：输入六位十六进制数字（0-F），分别代表RGB颜色值，如黑：000000，白：FFFFFF，红：FF0000"
                        +"\n*贴入画布位置：如果想把视频图片贴入画布中央，请保留 ‘中心粘贴’；如果要自定义位置，请输入两个正整数以 ‘x’ 隔开。"
                        +"\n*开始时间 与 持续时间：输入时、分、秒以 ‘：’ 隔开。也可以只输入带有小数点的秒，此时无需 ‘：’。")
        explain_text.place(x=2,y=475)
        
        
        confirm_run_button=tk.Button(treatment_window,text="确认并运行",foreground="yellow",background="green",command=lambda: treatment_confirm())
        confirm_run_button.place(x=400,y=590)
        
        stop_run_button=tk.Button(treatment_window,text="退出",foreground="yellow",background="green",command=sys.exit)
        stop_run_button.place(x=620,y=590)
        

def update_rotate_method_state(rotate_method_radiobuttons):
        if rotate_var.get() == 1:
                for radiobutton in rotate_method_radiobuttons:
                        radiobutton.config(state="normal",background="white")
        else:
                for radiobutton in rotate_method_radiobuttons:
                        radiobutton.config(state="disabled",background="gray")
                
def update_canvas_property(*args):
        global effective_width,effective_height
        state = "normal" if canvas_var.get() == 1 else "disabled"
        if resizeTF_var.get()==1:
                scale_read=size_entry.get().split("x")
                resize_x,resize_y=int(scale_read[0]),int(scale_read[1])
                print("line 603 effective width height==",effective_width,effective_height,resize_x,resize_y,type(resize_x))
        #当有一个维度是 -1 时，计算另一个维度数字，给后面canvas_size 判断大小用
                if resize_x==-1:
                        effective_width=int(round((resize_y/effective_height*effective_width),0))        #四舍五入 用 round，四舍五入取整，int(round(x,0))
                        effective_height=resize_y
                elif resize_y==-1:
                        effective_height=int(round((resize_x/effective_width*effective_height),0))    
                        effective_width=resize_x
                else:
                        effective_width=resize_x
                        effective_height=resize_y
                print("line 614 effective width height==",effective_width,effective_height)        
        if rotate_var.get()==1:
                effective_width,effective_height=effective_height,effective_width
                print("line 617 effective width height==",effective_width,effective_height)
                
        canvas_label.config(text=f"是否贴入画布？(图片尺寸：{effective_width}x{effective_height})")
        canvas_size_entry.config(state=state)
        canvas_size_entry.delete(0,tk.END)
        canvas_size_entry.insert(tk.END, f"{effective_width}x{effective_height}")
        canvas_color_entry.config(state=state)
        canvas_color_entry.delete(0,tk.END)
        canvas_color_entry.insert(tk.END, f"000000")
        past_entry.config(state=state)
        past_entry.delete(0,tk.END)
        past_entry.insert(tk.END,"中心粘贴")
        treatment_window.update()
        
        
def update_time_cut(*args):
        state="normal" if timing_var.get()==1 else "disabled"
        start_entry.config(state=state)
        start_entry.delete(0,tk.END)
        start_entry.insert(tk.END, "00:00:00")
        duration_entry.config(state=state)
        duration_entry.delete(0,tk.END)
        duration_entry.insert(tk.END, f"{round(duration,2)}")
        
def update_resize_method(*args):
        state="normal" if resizeTF_var.get()==1 else "disabled"
        size_entry.config(state=state)
        size_entry.delete(0,tk.END)
        if cropTF_var.get()==1:
                size_label.config(text=f"*您抠图分辨率为：{effective_rect_width}x{effective_rect_height}，请输入新分辨率：")
                size_entry.insert(tk.END, f"{effective_rect_width}x{effective_rect_height}")
        else:
                size_entry.insert(tk.END, f"{video_width}x{video_height}")

def treatment_confirm():
        global cropTF_var,size_entry,rotate_var,rotate_method_var,mirror_var,canvas_var,timing_var,canvas_size_entry,canvas_color_entry,size_entry,start_entry
        global duration_entry,effective_width,effective_height
        treatment_window.withdraw()
        
        vf_code=""
        strings="您选择了：\n"
        crp=cropTF_var.get()
        if crp==1:
                strings+=f"抠图: 抠图大小：{effective_rect_width}x{effective_rect_height}；抠图起始点为：{effective_start_x}x{effective_start_y}\n"
                vf_code+=f"crop={effective_rect_width}:{effective_rect_height}:{effective_start_x}:{effective_start_y}"
        
        if resizeTF_var.get()==1:        
                scale_read=size_entry.get().split("x")
                resize_x,resize_y=int(scale_read[0]),int(scale_read[1])
                if resize_x != -1:
                        if resize_x % 2 != 0:
                                resize_x=resize_x-1
                if resize_y != -1:
                        if resize_y % 2 != 0:
                                resize_y=resize_y-1
                if resize_x == -1 and resize_y == -1:
                        messagebox.showinfo("输入不对！","宽和高不能同时取值 -1 ")
                        treatment_window.deiconify()
                        return
                if resize_y <-1 or resize_x< -1 or resize_x==0 or resize_y==0:
                        messagebox.showinfo("输入不对！","宽和高不能为 0 或负值 （只有一个维度可以是：-1 为自适应除外)")
                        treatment_window.deiconify()
                        return
                
                strings+=f"改变输出分辨率: 您定义的新分辨率为：{resize_x}x{resize_y}\n"
                if vf_code: 
                        vf_code+=","
                vf_code+=f"scale={resize_x}:{resize_y}"
                
        if rotate_var.get()==1:
                strings+="旋转输出图片："
                method=rotate_method_var.get()
                if method==0: rotate_str="顺时针旋转90度并垂直翻转"
                if method==1: rotate_str="顺时针旋转90度"
                if method==2: rotate_str="逆时针旋转90度"
                if method==3: rotate_str="逆时针旋转90度并垂直翻转"
                strings+=f"旋转方式为：{rotate_str}\n"
                if vf_code: vf_code+=","
                vf_code+=f"transpose={method}"
                
        if mirror_var.get()==1:
                strings+="水平镜像翻转输出图片\n"
                if vf_code: vf_code+=","
                vf_code+=f"hflip"
                
        crf=crf_entry.get()
        try:
                if int(crf) not in range(0,50):
                        messagebox.showinfo("您的输入无效！","crf 输入值必须是：0-50间的整数")
                        treatment_window.deiconify()
                        return
        except ValueError:
                        messagebox.showinfo("crf 输入错误！","请输入（0-50）间的正整数！")
                        treatment_window.deiconify()
                        return
        strings+=f"您选择的输出视频压缩 crf 值为：{crf}\n"
        
        if canvas_var.get()==1:
                strings+="视频图片贴入画布: "
                canvas_read=canvas_size_entry.get().split("x")
                try:
                        canvas_width=int(canvas_read[0].strip())
                        canvas_height=int(canvas_read[1].strip())
                except ValueError:
                        messagebox.showinfo("画布尺寸输入错误！","请输入正整数！")
                        treatment_window.deiconify()
                        return
                if canvas_width % 2 !=0: canvas_width +=1
                if canvas_height % 2 !=0: canvas_height +=1
                strings+=f"画布尺寸为：{canvas_width}x{canvas_height}，"
                past_read=past_entry.get()
                if past_read=="中心粘贴":
                        strings+="贴入位置为: 贴入画布中央，"
                        print("line 695 canvas_width, effective width:",canvas_width,effective_width,type(canvas_width),type(effective_width))
                        past_x=(canvas_width-effective_width)//2
                        past_y=(canvas_height-effective_height)//2 
                else:
                        past_read_list=past_entry.get().split("x")
                        try:
                                past_x=int(past_read_list[0].strip())
                                past_y=int(past_read_list[1].strip())
                        except ValueError:
                                messagebox.showinfo("图片贴入画布位置输入错误！","请输入正整数！")
                                treatment_window.deiconify()
                                return
                        strings+=f"贴入位置为：{past_x}x{past_y},"
                        
                if effective_width+past_x > canvas_width or effective_height+past_y > canvas_height:
                        messagebox.showinfo("画布与图片粘贴不匹配！","您的画布尺寸小于图片尺寸加粘贴偏移量！")
                        treatment_window.deiconify()
                        return
                canvas_color=canvas_color_entry.get().strip()
                if len(canvas_color)!=6:
                        messagebox.showinfo("输入错误！",f"画布颜色需要六位十六进制字符，您输入了 {len(canvas_color)} 位！")
                        treatment_window.deiconify()
                        return 
                for letter in canvas_color:
                        if letter not in '0123456789ABCDEFabcdef':
                                messagebox.showinfo("颜色字符串需要十六进制！",f"您输入的 ‘{letter}’ 不是十六进制字符！")
                                treatment_window.deiconify()
                                return 
                strings+=f"画布颜色为：{canvas_color}\n"
                
                if vf_code: vf_code+=","
                vf_code+=f"pad={canvas_width}:{canvas_height}:{past_x}:{past_y}:color={canvas_color},scale=iw:-2"
                
        if timing_var.get()==1:
                start_at=start_entry.get()
                lasted=duration_entry.get()
                strings+=f"裁切原视频: 输出起始点为：{start_at},  保留视频时长为：{lasted},  原视频时长为：{round(duration,1)}秒"
        else:
                start_at="00"
                lasted=str(round(duration,2))
                
                
        print("line 639  vf_code=",vf_code )   
        if vf_code:
                command = ['ffmpeg','-i', input_file,'-vf', vf_code,'-ss', start_at, '-t', lasted,'-c:v', 'libx264','-crf', crf,output_file] 
        else:
                command = ['ffmpeg','-i', input_file,'-ss', start_at, '-t', lasted,'-c:v', 'libx264','-crf', crf,output_file] 
        
        window.withdraw()
        create_show_window()
        label0_show.config(text=strings)
        JobOn_window.update()
        
        process_start=time.time()
        
        subprocess.run(command)  
        
        # 使用ffprobe获取输出视频的真实宽度和高度  
        ffprobe_cmd1 = ['ffprobe','-v', 'error','-select_streams', 'v:0','-show_entries', 'stream=width,height','-of', 'csv=s=x:p=0',output_file]  
        result1 = subprocess.run(ffprobe_cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  
	# 解析输出，获取宽度和高度  
        print("line 711: result1.stdout= ",result1.stdout)
        if result1.returncode == 0:  
                output_lines = result1.stdout.strip().split('x')  
                print("final output file size is: ", int(output_lines[0]) ,int(output_lines[1]) )
        else:
                print("Error occurred while getting video dimensions:", result1.stderr)  
                return 
        now = time.localtime()
        label1_show.config(foreground="blue",text=f"视频共有 {total_frames} 帧, 播放时间：{round(duration,2)} 秒；视频处理用时：{round((time.time()-process_start),2)} 秒"
                        +f"\n任务完成时间：{now.tm_hour}:{now.tm_min}:{now.tm_sec}")
        label2_show.config(text=f"Job done!")
        exit_button.pack(padx=20,pady=10,anchor="ne")
        JobOn_window.update()
        #window.destroy()


def input_output_file():
        global IO_window, input_entry, output_entry
        if os.path.exists("in_out.txt"):
                with open("in_out.txt","r",encoding="utf-8") as file:
                        in_f=file.readline().rstrip("\n")
                        out_f=file.readline()
                        
        IO_window=tk.Toplevel()
        IO_window.title("请输入文件名！")
        
        input_label=tk.Label(IO_window, text="请输入待转换文件名称及路径*",justify="left")
        input_label.grid(row=0,column=0,padx=30,pady=10,sticky="nw")
        input_entry=tk.Entry(IO_window, width=45)
        input_entry.insert(tk.END, in_f)
        input_entry.grid(row=0,column=1,padx=15,pady=10,sticky="nw")
        
        output_label=tk.Label(IO_window, text="请输入欲输出文件名称及路径\n(小心，如果文件已经存在会被覆盖！)",justify="left")
        output_label.grid(row=1,column=0,padx=30,pady=10,sticky="nw")
        output_entry=tk.Entry(IO_window, width=45)
        output_entry.insert(tk.END,out_f)
        output_entry.grid(row=1,column=1,padx=15,pady=10,sticky="nw")
        
        inout_text=tk.Text(IO_window,height=3,relief="flat")
        inout_text.config(font=("Segoe UI",10),foreground="blue",background="#EEEEEE")
        inout_text.insert(tk.END,"*如果您想合并多段视频，请输入包含所有视频文件名称的 'txt' 文件（每行一个视频文件）"
                        +"\n  您也可以输入'合并'两个字，然后在系统引导下，逐个输入待合并的视频文件！"
                        +"\n 请特别注意，被合并的视频文件名称及其路径尽可能用英文字符，用汉字有时会出错！")
        inout_text.grid(row=2,column=0,columnspan=2,padx=30,pady=10,sticky="nw")
        
        confirm_button=tk.Button(IO_window, text="输入确认",foreground="yellow", background="green",command=confirm_input)
        confirm_button.grid(row=3, column=0,padx=15,pady=10,sticky="ne")
        
        exit_button=tk.Button(IO_window, text="退出", foreground="yellow", background="green",command=sys.exit)
        exit_button.grid(row=3, column=1,padx=50,pady=10,sticky="ne")
        
def combine_video(in_file,out_file):
        if in_file[-3:].lower()=="txt":
                if not os.path.isfile(in_file):
                        messagebox.showinfo("文件不存在！",f"您输入的合并文件{in_file}不存在！请检查您输入的文件名称及路径是否准确！")
                        return

                with open(in_file,"r",encoding="utf-8") as f:
                        lines=f.readlines()
                        print(lines)
                        
                with open("input_txt.txt","w") as ff:
                        i=1
                        for line in lines:
                                line_content=line.strip()
                                if line_content !="": 
                                        if not os.path.isfile(line_content):
                                                messagebox.showinfo("文件不存在！",f"您要合并的文件{line_content}不存在！请检查您输入的文件名称及路径是否准确！")
                                                sys.exit()
                                        else:
                                                ff.write(f"file '{line_content}'\n")  # 为每个文件路径添加 'file' 关键字和换行符 
                                                i+=1
                
        if in_file[-3:]=="合并":
                with open("input_txt.txt","w",encoding="utf-8") as ff:
                        i=1
                        while True:
                                file=simpledialog.askstring("请输入！",f"请输入第 {i} 个欲合并视频文件名及路径, 输入 'q' 停止输入！")
                                if file == None:
                                        response=messagebox.askquestion("如何继续？","您要放弃执行文件合并任务吗？")
                                        if response == "yes":
                                                return
                                        else:
                                                continue
                                if file!="":
                                        if file.strip()!="q" and file.strip()!="Q":
                                                if os.path.isfile(file.strip()):
                                                        ff.write(f"file '{file.strip()}'\n")
                                                        i+=1
                                                else:
                                                        messagebox.showinfo("文件不存在！",f"您输入的文件 {file} 不存在！请检查您输入的文件名称及路径是否准确！")
                                                        continue
                                        else:
                                                break
                                else:
                                        messagebox.showerror("输入错误！",f"请输入第 {i} 个欲合并视频文件名及路径")
                                        continue
                if i==1:
                        messagebox.showerror("无输入！","您未输入欲合并文件！请重新选择输入！")
                        return
                if i==2:
                        messagebox.showerror("输入错误！","您仅输入一个文件，程序无法合并。请重新选择输入！")
                        return
        # 定义ffmpeg命令  
        try:
                ffmpeg_command = ['ffmpeg','-f', 'concat','-safe', '0','-i', 'input_txt.txt','-c', 'copy',out_file]  
                subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE) 
        except subprocess.CalledProcessError as e:  
                messagebox.showerror("出错了", "合并文件时出错！很可能文件名或路径包含非英文字符或文件损坏严重所致！")  
                sys.exit()
        IO_window.destroy()
        messagebox.showinfo("job finished!", f"合并文件完成！共合并 {i-1} 个文件，输出文件名为：{out_file}")  
        sys.exit()

def confirm_input():
        global input_file, output_file,window,video_width,video_height,frame_image,resize_x,resize_y,rect_width,rect_height
        global first_frame,total_frames,duration,effective_height,effective_width
        
        if output_entry.get().strip():
                output_file=output_entry.get().strip()
        else:
                messagebox.showinfo("请输入！","请输入欲输出文件名称及路径！")
                return
        if os.path.exists(output_file):
                response=messagebox.askquestion("文件重名！","您给出的输出文件名已经存在，是否覆盖？")
                if response=="yes":
                        os.remove(output_file)
                else:
                        return
                
        if input_entry.get().strip():
                input_file=input_entry.get().strip()
                if input_file[-3:].lower()=="txt" or input_file[-3:]=="合并":
                        combine_video(input_file,output_file)
                        return
                if not os.path.isfile(input_file):
                        messagebox.showinfo("文件不存在！","您输入的待转换文件不存在！请检查您输入的文件名称及路径是否准确！")
                        return
        else:
                messagebox.showinfo("请输入！","请输入待转换文件名称及路径！")
                return
        
        print("Input_file: ",input_file)
        print("Output_file: ",output_file)
        
        with open("in_out.txt","w",encoding="utf-8") as file:
                file.write(input_file+"\n")
                file.write(output_file)
        
        first_frame_file = 'first_frame.png'  
        if os.path.exists(first_frame_file):
                os.remove(first_frame_file)
                
        subprocess.run(["ffmpeg", "-i", input_file, "-ss", "00:00:00", "-vframes", "1", first_frame_file])  # 使用FFmpeg命令获取第一帧图片，并忽略输出  
        
        # 获取视频流信息  
        ffprobe_stream_output = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", input_file])  
        ffprobe_stream_output = ffprobe_stream_output.decode('utf-8')  
        
        # 获取视频格式信息（时长）  
        ffprobe_format_output = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file])  
        ffprobe_format_output = ffprobe_format_output.decode('utf-8').strip()  
        
        # 解析视频流信息，获取宽度、高度和帧率  
        width_height_fps = ffprobe_stream_output.strip().split()  
        print("line 499, xxx", width_height_fps)
        print("line 500, xxx", ffprobe_format_output)
        video_width = int(width_height_fps[0])  
        video_height = int(width_height_fps[1])  
        effective_width,effective_height = video_width,video_height
        print("line 503 video_width, video_height is: ", video_width, video_height)
        fps_str = width_height_fps[2]  
        fps = float(re.search(r'\d+(\.\d+)?', fps_str).group())  
        duration = float(ffprobe_format_output)  
        total_frames = int(duration * fps)  
        print("line 508 duration, fps and total_frames is:", duration, fps, total_frames)

        with Image.open(first_frame_file) as first_image:
                print("line 511 first_frame image size",first_image.size)
                frame_image=first_image.copy()
                
        os.remove(first_frame_file)
        
        show_main_window(frame_image)
        IO_window.destroy()
        window.deiconify()

def show_main_window(image1):
        global window, ratio, image2, action_combo, mouse_pos_lable,action_button
        image1_width, image1_height=image1.size
        print(f"line 331, 您的视频图像大小为：{image1_width}x{image1_height}")
        
        ratio1=image1_width/screen_width
        ratio2=image1_height/screen_height
        ratio=max(ratio1, ratio2)
        print(f"line 347, 为了最大化显示全图，显示图会被被缩放：{round(ratio,2)} 倍")
        
        image2_width, image2_height=int(image1_width/ratio),int(image1_height/ratio)
        image2=image1.resize((image2_width,image2_height))
        print(f"line 353 show_size:, {image2_width}, {image2_height}, ----ratio now is: {ratio}")
        
        tk_image = ImageTk.PhotoImage(image2)  
        window_x= int((screen_width-image2_width)/2)
        window_y= int((screen_height-image2_height)/2)
        window.geometry(f"{image2_width}x{image2_height}+{window_x}+{window_y}") 
        image_label.config(image=tk_image)  
        image_label.image2 = tk_image
        action_button.place(x=15,y=30)
        mouse_pos_lable.place(x=15, y=image2_height-50)
        close_test.place(x=image2_width-60,y=30)


# 加载视频  
input_file = None
output_file = None
frame_image = Image.new("RGB",(100,100),(0,0,0))  #转为PIL图片格式
screen_width,screen_height=pyautogui.size()     #获取屏幕大小
resize_x=0
resize_y=0
rect_width=10
rect_height=10
effective_rect_height=10
effective_rect_width=10
start_x=0
start_y=0
effective_start_x=0
effective_start_y=0
ratio=1
method=0
effective_width=0
effective_height=0

start_clicked = False 
end_clicked = None
final_mouse_pos = None  

window=tk.Tk()
window.title("视频转换设置！") 
window.wm_overrideredirect(True)

window.withdraw()
input_output_file()

image_label = tk.Label(window)  
tk_image = ImageTk.PhotoImage(frame_image)  
image_label.config(image=tk_image)  
image_label.image = tk_image
image_label.place(x=0,y=0)

action_button=tk.Button(window,text="请选择视频处理方式",foreground="blue", command=lambda: treatment_method())
action_button.place_forget()

mouse_pos_lable=tk.Label(window)
mouse_pos_lable.place_forget()
window.bind('<Motion>', on_mouse_move)

close_test=tk.Button(window, text="退出",foreground="white",background="red",command=window.destroy)
close_test.place_forget()

window.mainloop()



"""
一般来说，使用Nuitka将Python程序编译为可执行的C或C++代码可以获得最小的可执行文件体积和较快的运行速度。这是因为Nuitka通过编译Python代码为
C或C++代码，可以有效地优化程序的性能和体积。

PyInstaller和cx_Freeze也可以将Python程序转换为可执行的exe文件，但生成的可执行文件通常会比较大，因为它们会将Python解释器和程序的依赖项打包
到可执行文件中，这可能会导致体积较大。nuitka和pyoxidizer是两种不同的Python程序打包工具，它们各自具有一些特点.

pyoxidizer的特点如下：
内存加载：pyoxidizer可以将Python应用程序的字节码打包到可执行映像中，并直接从内存中加载，从而提高了程序的启动速度。
静态链接：pyoxidizer使用自定义的Python解释器，该解释器设计为静态链接并嵌入到另一个程序中，提高了可移植性和安全性。
支持Linux：pyoxidizer目前只能生成Linux二进制文件，因为它所依赖的上游项目之一目前仅在Linux构建中可用。

py2exe主要适用于Windows平台，它也可以将Python程序转换为可执行的exe文件，但在一般情况下，生成的可执行文件体积较大，且性能可能不如Nuitka优化得好。

总的来说，Nuitka通常可以生成体积较小、运行速度较快的可执行文件，但也需要根据具体的项目需求和个人偏好来选择合适的转换方法。

Nuitka:
是一个用于将Python程序编译成可执行的C或C++代码的工具。它的主要特点和使用方法如下：

特点：

性能优化：Nuitka能够通过编译Python代码为C或C++代码来提高程序的性能。编译后的程序通常比原始的Python程序执行速度更快。

平台支持：Nuitka支持多个平台，包括Windows、Linux和MacOS。这使得它成为一个跨平台的工具，可以在不同的操作系统上使用。

依赖管理：Nuitka能够处理Python程序的依赖关系，并将其打包到最终的可执行文件中，这样可以确保程序在其他计算机上也能够正常运行。

兼容性：Nuitka与Python的语法和标准库兼容，因此可以编译大部分的Python程序。

使用方法：

安装Nuitka：可以通过pip安装Nuitka，命令为pip install nuitka。

编译Python程序：使用nuitka命令来编译Python程序，例如nuitka my_program.py。

生成可执行文件：编译完成后，会生成一个可执行文件，可以直接运行该文件来执行Python程序。

优化选项：可以使用Nuitka的一些优化选项来提高编译后程序的性能，例如使用--clustering选项进行函数聚合，或者使用--standalone选项生成一个独立的可执行文件。

需要注意的是，Nuitka并不支持所有的Python特性，因此在使用时需要注意其兼容性。另外，编译后的可执行文件可能会比原始的Python程序
体积更大，因为它包含了编译后的C或C++代码以及程序的依赖项。

多次使用crf=23，h.264编码压缩，理论上视频文件的大小不会有显著变化，因为crf值决定了视频压缩的质量，而不是基于输入文件的大小或质量。
所以，即使你已经对视频进行了一次压缩，并且现在再次使用相同的crf值进行压缩，输出文件的大小应该大致相同。
"""
