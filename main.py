from tkinter import *
from tkinter import messagebox
from time import sleep
from pickle import load, dump
from threading import Thread
from random import randint
from colorsys import hsv_to_rgb
from math import radians, cos, sin

current_project = None
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
    edit_win.geometry("400x400")
    edit_win.iconbitmap("icon.ico")

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

    options_listbox = Listbox(edit_win)
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
        global current_project
        current_project = name
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
    global speed, data, current_project, window_should_close
    speed = 0
    angle = randint(0, 359)
    data_load()
    auto_save_thread = Thread(target=auto_save)
    auto_save_thread.start()

    root = Tk()
    root.title("转盘")
    root.geometry("1200x675")
    root.iconbitmap("icon.ico")
    root.protocol("WM_DELETE_WINDOW", lambda: on_window_delete())
    
    project_edit_button = Button(root, text="编辑项目", command=edit_project)
    project_edit_button.pack()

    canvas = Canvas(root, width=900, height=506)
    canvas.pack()

    start_button = Button(root, text="开始", command=set_speed)
    start_button.pack()

    current_text_label = Label(root, text="项目为空", font=("Arial", 40))
    current_text_label.pack()

    while True:
        if window_should_close:
            root.destroy()
            break
        if speed < 4:
            speed = 0
        if speed > 0:
            angle += speed
            if angle >= 360:
                angle -= 360
            if randint(1,25)<=2:
                speed -= 1
        if current_project is None or len(data['projects'].get(current_project, [])) == 0:
            current_text_label.config(text="项目为空")
            canvas.delete("all")
            canvas.create_text(450, 253, text="项目为空", font=("Arial", 40))
        else:
            n = len(data['projects'][current_project])
            average_angle = 360 / n
            index = int(angle // average_angle) % n
            current_text = data['projects'][current_project][index]
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
                # if n%2==0:
                text_angle = start + average_angle/2
                # else:
                    # text_angle = start+average_angle
                text_radius = radius * 0.6
                text_x = center_x + text_radius * cos(radians(text_angle))
                text_y = center_y + text_radius * sin(radians(text_angle))
                rotation = 360-text_angle
                if rotation > 90 and rotation < 270:
                    rotation += 180
                canvas.create_text(text_x, text_y,
                                text=data['projects'][current_project][i],
                                angle=rotation,
                                font=("Arial", 14, "bold"),
                                fill="black",
                                anchor="center")
            pointer_angle = radians(angle - 90)
            end_x = center_x + radius * cos(pointer_angle)
            end_y = center_y + radius * sin(pointer_angle)
            canvas.create_line(center_x, center_y, end_x, end_y, fill="red", width=3)

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