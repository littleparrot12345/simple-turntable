"""
    Copyright (C) 2025  wangboyue

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from tkinter import *
from tkinter import messagebox
from time import sleep
from pickle import load, dump
from threading import Thread
from random import randint
from colorsys import hsv_to_rgb
from math import radians, cos, sin

running = True
window_should_close = False

def data_load():
    global data
    try:
        with open("data.st", "rb") as f:
            data = load(f)
        if 'projects' not in data:
            data['projects'] = {}
    except Exception:
        data = {'projects': {}}

def data_save():
    with open("data.st", "wb") as f:
        dump(data, f)

def edit_project():
    edit_win = Toplevel()
    edit_win.title("编辑项目")
    edit_win.geometry("500x400")
    edit_win.iconbitmap("icon.ico")

    Label(edit_win, text="选择现有项目:").pack()
    projects_listbox = Listbox(edit_win, height=4)
    projects_listbox.pack(fill=BOTH, expand=True)
    
    for project in data['projects']:
        projects_listbox.insert(END, project)
    
    def on_project_select(event):
        selected = projects_listbox.curselection()
        if selected:
            name = projects_listbox.get(selected[0])
            project_name_entry.delete(0, END)
            project_name_entry.insert(0, name)
    
    projects_listbox.bind('<<ListboxSelect>>', on_project_select)

    Label(edit_win, text="项目名称:").pack()
    project_name_entry = Entry(edit_win)
    project_name_entry.pack()

    def load_project():
        name = project_name_entry.get()
        if name in data['projects']:
            options_listbox.delete(0, END)
            for option in data['projects'][name]:
                options_listbox.insert(END, option)
        else:
            messagebox.showinfo("提示", "项目不存在，可创建新项目。")

    Button(edit_win, text="加载项目", command=load_project).pack()

    options_listbox = Listbox(edit_win, height=4)
    options_listbox.pack(fill=BOTH, expand=True)

    new_option_entry = Entry(edit_win)
    new_option_entry.pack()

    def add_option():
        option = new_option_entry.get()
        if option:
            options_listbox.insert(END, option)
            new_option_entry.delete(0, END)

    Button(edit_win, text="添加选项", command=add_option).pack()

    def delete_option():
        selected = options_listbox.curselection()
        if selected:
            options_listbox.delete(selected[0])

    Button(edit_win, text="删除选项", command=delete_option).pack()

    def save_project():
        name = project_name_entry.get()
        if not name:
            messagebox.showerror("错误", "请输入项目名称")
            return
        options = list(options_listbox.get(0, END))
        data['projects'][name] = options
        messagebox.showinfo("成功", "项目保存成功")

    Button(edit_win, text="保存项目", command=save_project).pack()

    def exit():
        name=project_name_entry.get()
        global data
        data['current_project'] = name
        edit_win.destroy()
    
    Button(edit_win, text="退出", command=exit).pack()

def set_speed():
    global speed
    speed = 12

def auto_save():
    global running
    count = 0
    while running:
        if count == 60:
            count = 0
            data_save()
        count += 1
        sleep(1)

def on_window_delete():
    global window_should_close
    window_should_close = True

def main():
    global speed, data, window_should_close
    speed = 0
    angle = randint(0, 359)
    data_load()
    auto_save_thread = Thread(target=auto_save)
    auto_save_thread.start()
    data.setdefault('current_project', None)

    root = Tk()
    root.title("转盘")
    root.geometry("1200x675")
    root.iconbitmap("icon.ico")
    root.protocol("WM_DELETE_WINDOW", lambda: on_window_delete())

    data.setdefault('gpl3', False)
    if not data['gpl3']:
        messagebox.showinfo("提示", """本软件遵循GPLv3协议开源，请阅读LICENSE文件。
GitHub: https://github.com/littleparrot12345/simple-turntable

SimpleTurntable 是自由软件。
- 自由软件是什么？为什么 SimpleTurntable 选择成为自由软件？
自由软件意味着使用者有运行、复制、发布、研究、修改和改进该软件的自由。
自由软件是权利问题，不是价格问题。
要理解这个概念，你应该考虑“free”是“言论自由（free speech）”中的“自由”，
而不是“免费啤酒（free beer）”中的“免费”。
更精确地说，自由软件赋予软件使用者四项基本自由：
• 不论目的为何，有运行该软件的自由（自由之零）。
• 有研究该软件如何工作以及按需改写该软件的自由（自由之一）。
• 有重新发布拷贝的自由，这样你可以借此来敦亲睦邻（自由之二）。
• 有向公众发布改进版软件的自由（自由之三），这样整个社群都可因此受惠。""")
        data['gpl3'] = True
    
    project_edit_button = Button(root, text="编辑项目", command=edit_project)
    project_edit_button.pack()

    canvas = Canvas(root, width=900, height=506)
    canvas.pack()

    start_button = Button(root, text="开始", command=set_speed)
    start_button.pack()

    Label(root, text="").pack()
    current_text_label = Label(root, text="项目为空", font=("Arial", 30))
    current_text_label.pack()

    while True:
        if window_should_close:
            root.destroy()
            break
        if speed > 0:
            angle += speed
            if angle >= 360:
                angle -= 360
            if randint(1,25)<=2:
                speed -= 1
        if data['current_project'] is None or len(data['projects'].get(
            data['current_project'], [])) == 0:
            current_text_label.config(text="项目为空")
            canvas.delete("all")
            canvas.create_text(450, 253, text="项目为空", font=("Arial", 40))
        else:
            n = len(data['projects'][data['current_project']])
            average_angle = 360 / n
            index = int(angle // average_angle) % n
            current_text = data['projects'][data['current_project']][index]
            current_text_label.config(text=current_text)
            canvas.delete("all")
            radius = 200
            center_x, center_y = 450, 253
            for i in range(n):
                start = i * average_angle - 90
                if n%2==1:
                    start+= average_angle/2
                rgb = hsv_to_rgb(i/n, 0.7, 0.9)
                color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), 
                                                     int(rgb[1]*255),
                                                     int(rgb[2]*255))
                canvas.create_arc(center_x - radius, center_y - radius,
                                  center_x + radius, center_y + radius,
                                  start=start, extent=average_angle,
                                  fill=color, outline="black")
            for i in range(n):
                start = i * average_angle - 90
                text_angle = start + average_angle/2
                text_radius = radius * 0.5
                text_x = center_x + text_radius * cos(radians(text_angle))
                text_y = center_y + text_radius * sin(radians(text_angle))
                rotation = 360-text_angle
                if rotation > 90 and rotation < 270:
                    rotation += 180
                canvas.create_text(text_x, text_y,
                                text=data['projects'][data['current_project']][i],
                                angle=rotation,
                                font=("Arial", 10),
                                fill="black",
                                anchor="center")
            pointer_angle = radians(angle - 90)
            end_x = center_x + radius * cos(pointer_angle)
            end_y = center_y + radius * sin(pointer_angle)
            canvas.create_line(center_x, center_y, end_x, end_y, fill="red", width=3)
            canvas.create_oval(center_x - 5, center_y - 5,
                               center_x + 5, center_y + 5,
                               fill="black")

        root.update_idletasks()
        root.update()
        sleep(1/30)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        messagebox.showerror("程序运行时发生错误", str(e))
        raise e
    finally:
        running = False
        data_save()