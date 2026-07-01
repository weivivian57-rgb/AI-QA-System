import tkinter as tk
from tkinter import messagebox

from matcher import find_answer

# 保存历史记录
history = []


def query():

    question = entry.get().strip()

    if question == "":
        messagebox.showwarning("提示", "请输入问题！")
        return

    history.append(question)

    answer = find_answer(question)

    result.delete("1.0", tk.END)
    result.insert(tk.END, answer)


def clear():

    entry.delete(0, tk.END)

    result.delete("1.0", tk.END)


def exit_program():

    print("用户提问历史：")

    for item in history:
        print(item)

    root.destroy()


def start_ui():

    global root
    global entry
    global result

    root = tk.Tk()

    root.title("AI人工智能基础问答系统")

    root.geometry("700x500")

    root.configure(bg="#F5F8FC")

    # 标题
    title = tk.Label(
        root,
        text="AI人工智能基础问答系统",
        font=("微软雅黑", 18, "bold"),
        bg="#F5F8FC",
        fg="#2F6AFF"
    )

    title.pack(pady=20)

    # 输入框说明
    tk.Label(
        root,
        text="请输入问题：",
        font=("微软雅黑", 11),
        bg="#F5F8FC"
    ).pack()

    entry = tk.Entry(
        root,
        width=60,
        font=("微软雅黑", 12)
    )

    entry.pack(pady=10)

    # 按钮区域
    frame = tk.Frame(root, bg="#F5F8FC")

    frame.pack()

    tk.Button(
        frame,
        text="查询答案",
        width=12,
        command=query
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        frame,
        text="清空",
        width=12,
        command=clear
    ).grid(row=0, column=1, padx=10)

    tk.Button(
        frame,
        text="退出",
        width=12,
        command=exit_program
    ).grid(row=0, column=2, padx=10)

    # 答案区域
    tk.Label(
        root,
        text="查询结果：",
        font=("微软雅黑", 11),
        bg="#F5F8FC"
    ).pack(pady=20)

    result = tk.Text(
        root,
        width=70,
        height=10,
        font=("微软雅黑", 11)
    )

    result.pack()

    root.mainloop()