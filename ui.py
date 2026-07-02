import tkinter as tk
from tkinter import ttk, messagebox

from matcher import find_answer
from knowledge import get_question_count

# ===========================
# 配色
# ===========================

PRIMARY = "#2F6AFF"
PRIMARY_HOVER = "#1A56FF"

BG = "#F5F8FC"
CARD = "#FFFFFF"

TEXT = "#333333"

# ===========================
# 历史记录
# ===========================

history = []


def update_status():
    status.set(
        f"当前知识库：{get_question_count()} 条 | 已提问：{len(history)} 次"
    )


def query(event=None):

    question = entry.get().strip()

    if question == "":
        messagebox.showwarning("提示", "请输入问题！")
        return

    history.append(question)

    history_list.insert(tk.END, question)

    answer = find_answer(question)

    result.config(state="normal")

    result.delete("1.0", tk.END)

    result.insert(tk.END, answer)

    result.config(state="disabled")

    update_status()


def clear():

    entry.delete(0, tk.END)

    result.config(state="normal")
    result.delete("1.0", tk.END)
    result.config(state="disabled")


def exit_program():

    root.destroy()


def init_style():

    style = ttk.Style()

    style.theme_use("clam")

    style.configure(
        "Title.TLabel",
        background=BG,
        foreground=PRIMARY,
        font=("微软雅黑", 18, "bold")
    )

    style.configure(
        "TLabel",
        background=BG,
        foreground=TEXT,
        font=("微软雅黑", 10)
    )

    style.configure(
        "Primary.TButton",
        font=("微软雅黑", 10),
        padding=8
    )

    style.configure(
        "TEntry",
        padding=5
    )


def start_ui():

    global root
    global entry
    global result
    global history_list
    global status

    root = tk.Tk()

    root.title("AI人工智能基础问答系统")

    root.geometry("980x620")

    root.configure(bg=BG)

    init_style()

    # ===========================
    # 标题
    # ===========================

    ttk.Label(
        root,
        text="AI人工智能基础问答系统",
        style="Title.TLabel"
    ).pack(pady=20)

    # ===========================
    # 主区域
    # ===========================

    main_frame = tk.Frame(
        root,
        bg=BG
    )

    main_frame.pack(fill="both", expand=True, padx=20)

    # ===========================
    # 左侧历史
    # ===========================

    left = tk.Frame(
        main_frame,
        bg=CARD,
        bd=1,
        relief="solid"
    )

    left.pack(
        side="left",
        fill="y"
    )

    tk.Label(
        left,
        text="提问历史",
        bg=CARD,
        fg=PRIMARY,
        font=("微软雅黑", 12, "bold")
    ).pack(pady=10)

    history_list = tk.Listbox(

        left,

        width=28,

        height=25,

        font=("微软雅黑", 10),

        bd=0,

        highlightthickness=0

    )

    history_list.pack(
        padx=10,
        pady=10
    )

    # ===========================
    # 右侧
    # ===========================

    right = tk.Frame(
        main_frame,
        bg=BG
    )

    right.pack(
        side="left",
        fill="both",
        expand=True,
        padx=20
    )

    ttk.Label(
        right,
        text="请输入问题："
    ).pack(anchor="w")

    entry = ttk.Entry(
        right,
        font=("微软雅黑", 11)
    )

    entry.pack(
        fill="x",
        pady=10
    )

    entry.bind("<Return>", query)

    # ===========================
    # 按钮
    # ===========================

    button_frame = tk.Frame(
        right,
        bg=BG
    )

    button_frame.pack(anchor="w")

    ttk.Button(

        button_frame,

        text="查询",

        style="Primary.TButton",

        command=query

    ).grid(row=0, column=0, padx=5)

    ttk.Button(

        button_frame,

        text="清空",

        command=clear

    ).grid(row=0, column=1, padx=5)

    ttk.Button(

        button_frame,

        text="退出",

        command=exit_program

    ).grid(row=0, column=2, padx=5)

    # ===========================
    # 查询结果
    # ===========================

    ttk.Label(
        right,
        text="查询结果："
    ).pack(anchor="w", pady=(25, 10))

    result = tk.Text(

        right,

        height=15,

        font=("微软雅黑", 11),

        bg="white",

        fg=TEXT,

        bd=1,

        relief="solid"

    )

    result.pack(
        fill="both",
        expand=True
    )

    result.config(state="disabled")

    # ===========================
    # 状态栏
    # ===========================

    status = tk.StringVar()

    update_status()

    status_bar = tk.Label(

        root,

        textvariable=status,

        anchor="w",

        bg="#E9EEF8",

        fg="#555555",

        font=("微软雅黑", 10)

    )

    status_bar.pack(
        side="bottom",
        fill="x"
    )

    root.mainloop()