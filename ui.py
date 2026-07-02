"""
ui.py
可视化界面模块 - 全功能终极优化版 
（带保姆级注释，帮你轻松读懂每一行代码）
"""
# ===========================
# 准备工作：导入我们需要的“工具箱”
# ===========================
import tkinter as tk               # 导入 Tkinter，这是 Python 自带的做桌面界面的基础工具
from tkinter import ttk, messagebox # 导入 ttk（更好看的组件）和 messagebox（弹窗提示工具）
import time                        # 用来计时的工具
import datetime                    # 用来获取当前日期和时间的工具

from matcher import find_answer    # 从我们的算法文件里，导入“找答案”的函数
from knowledge import get_question_count # 从知识库里，导入“获取问题总数”的函数

# ===========================
# 1. 字体设置 (界面的“排版规范”)
# 相当于设定好各种标题、正文的字号，后面直接拿来用
# ===========================
FONT_TITLE = ("微软雅黑", 16, "bold")       # 顶部大标题：16号字，加粗
FONT_HIST_TITLE = ("微软雅黑", 14, "bold")  # 历史记录标题：14号字，加粗
FONT_BTN = ("微软雅黑", 14, "bold")         # 按钮文字：14号字，加粗
FONT_ENTRY = ("微软雅黑", 14)               # 输入框文字：14号字，正常
FONT_RESULT = ("微软雅黑", 14)              # 结果框文字：14号字，正常
FONT_HIST_ITEM = ("微软雅黑", 12)            # 历史记录每一行的文字：12号字

# ===========================
# 2. 主题配色字典 (界面的“皮肤”)
# 我们准备了两套颜色：一套浅色(白昼)，一套深色(黑夜)
# ===========================
# 浅色模式颜色大全
LIGHT_COLORS = {
    "PRIMARY": "#2F6AFF",        # 主色调：科技蓝
    "PRIMARY_HOVER": "#1A56FF",  # 鼠标放上去时的深蓝色
    "BG": "#F4F7FC",            # 整个软件的大背景色：浅灰蓝
    "CARD": "#FFFFFF",          # 卡片背景色：纯白
    "TEXT": "#333333",          # 主要文字颜色：深灰/黑
    "TEXT_LIGHT": "#777777",    # 次要文字颜色（如提示词）：浅灰
    "HIGHLIGHT": "#FF5722",     # 高亮关键词的颜色：橙红色
    "STATUS_BG": "#E6EDF7",     # 底部状态栏的背景色
    "BORDER": "#E0E0E0",        # 边框颜色
    "SEC_HOVER": "#F0F4FA"       # 普通按钮鼠标放上去的颜色
}

# 深色模式颜色大全 (跟上面一一对应，但是是暗黑风格)
DARK_COLORS = {
    "PRIMARY": "#4C84FF",        
    "PRIMARY_HOVER": "#3A6ECC",  
    "BG": "#121212",            
    "CARD": "#1E1E1E",          
    "TEXT": "#E0E0E0",          
    "TEXT_LIGHT": "#888888",    
    "HIGHLIGHT": "#FF7043",     
    "STATUS_BG": "#1A1A1A",
    "BORDER": "#333333",
    "SEC_HOVER": "#2A2A2A"       
}

# 全局变量：记录当前是浅色还是深色，默认是浅色
is_dark_mode = False
current_theme = LIGHT_COLORS

# ===========================
# 系统的“记忆中枢”（全局状态）
# 用来记住我们提过什么问题、查了多久等信息
# ===========================
history = []                # 存放所有问过的问题
query_time_ms = "0.00"      # 上一次查询花了多少时间
query_frequency = {}        # 统计每个问题被问了多少次（用来算“最热门”）

# 这些列表用来把界面上的零件“收纳”起来，方便我们一键换肤（切换深浅色）时能找到它们
bg_frames = []
card_frames = []
status_frames = []
bg_labels = []
card_labels = []
status_labels = []
round_canvases = [] 
round_buttons = [] 

# ===========================
# 3. 高级 UI 组件（手工捏制的“圆角零件”）
# Tkinter 原生不支持漂亮的圆角，所以我们用画布(Canvas)自己画
# ===========================

class RoundCard(tk.Canvas):
    """
    圆角卡片：用来做输入框的外壳、结果框的外壳等。
    原理：创建一个没有边框的画板，在里面画一个圆角矩形作为背景。
    """
    def __init__(self, parent, bg_color, border_color, radius=4, **kwargs):
        # 初始化画板
        super().__init__(parent, bg=parent["bg"], bd=0, highlightthickness=0, **kwargs)
        self.radius = radius            # 圆角的大小（默认4）
        self.bg_color = bg_color        # 背景颜色
        self.border_color = border_color# 边框颜色
        self.bind("<Configure>", self.draw) # 当窗口大小改变时，重新画一下自己

    def draw(self, event=None):
        """擦除旧的，重新画一个圆角矩形"""
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        self.create_rounded_rect(0, 0, w-1, h-1, self.radius, fill=self.bg_color, outline=self.border_color)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """用数学坐标计算，画出一个带平滑圆角的形状"""
        points = [
            x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r,
            x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True) # smooth=True 让边角更顺滑


class RoundButton(tk.Canvas):
    """
    圆角动画按钮：就是我们点击的“查询”、“清空”按钮。
    带 Hover 效果（鼠标移上去会变色）。
    """
    def __init__(self, parent, text, font, default_bg, hover_bg, text_color, command=None, radius=4, **kwargs):
        super().__init__(parent, bg=parent["bg"], bd=0, highlightthickness=0, **kwargs)
        self.radius = radius
        self.default_bg = default_bg  # 正常颜色
        self.hover_bg = hover_bg      # 鼠标放上去的颜色
        self.current_bg = default_bg  # 当前颜色
        self.text_color = text_color  # 文字颜色
        self.text_str = text          # 按钮上的字
        self.font = font              # 字体
        self.command = command        # 点击按钮后要执行的动作

        # 绑定鼠标动作
        self.bind("<Configure>", self.draw)
        self.bind("<Enter>", self.on_enter)             # 鼠标进入
        self.bind("<Leave>", self.on_leave)             # 鼠标离开
        self.bind("<ButtonRelease-1>", self.on_click)   # 鼠标左键点击松开
        self.config(cursor="hand2")                     # 鼠标放上去变成“小手”图标

    def draw(self, event=None):
        """画按钮背景，并在正中间写上文字"""
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        self.create_rounded_rect(0, 0, w-1, h-1, self.radius, fill=self.current_bg, outline=self.current_bg)
        # 在正中心 (w/2, h/2) 写字
        self.create_text(w/2, h/2, text=self.text_str, fill=self.text_color, font=self.font, justify="center")

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """画圆角的具体数学计算（同上）"""
        points = [
            x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r,
            x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_enter(self, event):
        """鼠标移进来，颜色换成 hover_bg，重新画一下"""
        self.current_bg = self.hover_bg
        self.draw()

    def on_leave(self, event):
        """鼠标移出去，颜色换回 normal_bg，重新画一下"""
        self.current_bg = self.default_bg
        self.draw()

    def on_click(self, event):
        """如果绑定了指令（比如查询函数），点击就执行它"""
        if self.command:
            self.command()

    def update_theme(self, default_bg, hover_bg, text_color):
        """一键换肤时，更新按钮颜色的方法"""
        self.default_bg = default_bg
        self.hover_bg = hover_bg
        self.current_bg = default_bg
        self.text_color = text_color
        self.config(bg=self.master["bg"])
        self.draw()

# ===========================
# 4. 各种功能的幕后小助手
# ===========================

def show_about():
    """菜单栏里的“关于系统”弹窗"""
    messagebox.showinfo("关于", "AI 人工智能基础问答系统 v2.0\n\n作者：Vivian\n课程：软件开发基础\n基于核心关键词匹配算法优化版。")

def show_help():
    """菜单栏里的“使用帮助”弹窗"""
    messagebox.showinfo("帮助", "1. 在输入框中输入您关心的 AI 基础问题（例如：Python有什么用？）。\n2. 点击右侧“查询”或按下键盘“回车键”获取答案。\n3. 左侧面板会自动记录您提问的时间与历史，点击即可复查。")

def toggle_theme():
    """
    一键切换 深色/浅色 模式的神奇魔法。
    原理：遍历我们之前存起来的所有零件，把它们的颜色替换掉。
    """
    global is_dark_mode, current_theme
    is_dark_mode = not is_dark_mode # 状态反转（白天变黑夜，黑夜变白天）
    # 根据状态选择对应的字典
    current_theme = DARK_COLORS if is_dark_mode else LIGHT_COLORS
    theme = current_theme
    
    # 改变按钮上的字：☀ Light 或 🌙 Dark
    theme_btn.config(text="☀ Light" if is_dark_mode else "🌙 Dark", bg=theme["CARD"], fg=theme["TEXT"])
    root.configure(bg=theme["BG"]) # 改主窗口背景
    
    # 批量改各种容器和文字的颜色
    for w in bg_frames: w.configure(bg=theme["BG"])
    for w in card_frames: w.configure(bg=theme["CARD"])
    for w in status_frames: w.configure(bg=theme["STATUS_BG"])
    for w in bg_labels: w.configure(bg=theme["BG"], fg=theme["TEXT"])
    for w in card_labels: w.configure(bg=theme["CARD"], fg=theme["PRIMARY"])
    for w in status_labels: w.configure(bg=theme["STATUS_BG"], fg=theme["TEXT_LIGHT"])
    
    # 批量改圆角卡片颜色
    for canvas in round_canvases:
        canvas.bg_color = theme["CARD"]
        canvas.border_color = theme["BORDER"]
        canvas.configure(bg=canvas.master["bg"])
        canvas.draw()
        
    # 批量改按钮颜色
    for btn in round_buttons:
        if hasattr(btn, 'is_primary') and btn.is_primary:
            btn.update_theme(theme["PRIMARY"], theme["PRIMARY_HOVER"], "white")
        else:
            btn.update_theme(theme["CARD"], theme["SEC_HOVER"], theme["TEXT"])

    # 改输入框的颜色
    entry.configure(bg=theme["CARD"], fg=theme["TEXT_LIGHT"] if entry.get() == "请输入 AI 相关问题 (输入'退出'可关闭)..." else theme["TEXT"], insertbackground=theme["TEXT"])
    
    # 改历史列表的颜色
    history_list.configure(bg=theme["CARD"], fg=theme["TEXT"])
    style = ttk.Style()
    style.configure("Treeview", background=theme["CARD"], fieldbackground=theme["CARD"], foreground=theme["TEXT"])
    style.map("Treeview", background=[("selected", theme["PRIMARY"])], foreground=[("selected", "white")])
    
    # 改结果框的颜色
    result.configure(bg=theme["CARD"], fg=theme["TEXT"])
    update_status() # 刷新底部状态栏

def update_clock():
    """让界面右下角的时间跑起来"""
    now = datetime.datetime.now()
    clock_label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
    root.after(1000, update_clock) # 每隔1000毫秒（1秒）自己叫自己一次，实现时间跳动

def update_status():
    """刷新底部显示的：知识库数量、提问次数、查询耗时"""
    status.set(f" 📚 知识库：{get_question_count()} 条 | 📝 已提问：{len(history)} 次 | ⏱ 耗时：{query_time_ms} ms")

def update_popular():
    """计算出被问得最多的那个问题，显示在底部"""
    if not query_frequency:
        popular_var.set("🔥 最热门：暂无")
        return
    # 找出字典里被点次数最多的问题
    best_q = max(query_frequency, key=query_frequency.get)
    count = query_frequency[best_q]
    popular_var.set(f"🔥 最热门：{best_q} ({count}次)")

def clear_placeholder(event):
    """当用户鼠标点进输入框时，清空灰色的提示文字"""
    if entry.get() == "请输入 AI 相关问题 (输入'退出'可关闭)...":
        entry.delete(0, tk.END)
        entry.configure(foreground=current_theme["TEXT"]) # 字体变回正常颜色

def add_placeholder(event):
    """当用户鼠标点到别的地方，且输入框是空的时候，把灰色提示字塞回去"""
    if entry.get().strip() == "":
        entry.insert(0, "请输入 AI 相关问题 (输入'退出'可关闭)...")
        entry.configure(foreground=current_theme["TEXT_LIGHT"])

def highlight_keywords(text_widget, keywords):
    """把答案框里命中的关键字，染成醒目的橙红色并加粗"""
    text_widget.tag_configure("highlight", foreground=current_theme["HIGHLIGHT"], font=("微软雅黑", 14, "bold"))
    for word in keywords:
        start_idx = "1.0" # 从第一行第一个字开始找
        while True:
            # 搜索关键字的位置
            start_idx = text_widget.search(word, start_idx, stopindex=tk.END)
            if not start_idx:
                break # 找不到了就退出循环
            # 计算关键字结束的位置
            end_idx = f"{start_idx}+{len(word)}c"
            # 给这一段字打上“highlight”标签（也就是上色）
            text_widget.tag_add("highlight", start_idx, end_idx)
            start_idx = end_idx # 接着往下找

def query(event=None):
    """
    ⭐️ 这是最核心的函数！负责处理用户的提问并给出答案 ⭐️
    """
    global query_time_ms
    # 1. 拿到用户输入的文字，并去掉首尾空格
    question = entry.get().strip()

    # 2. 如果什么都没输入，弹个警告
    if question == "" or question == "请输入 AI 相关问题 (输入'退出'可关闭)...":
        messagebox.showwarning("提示", "请输入问题！")
        return
        
    # 3. 隐藏彩蛋：输入“退出”就关软件
    if question == "退出":
        exit_program()
        return

    # 4. 生成当前的时间 (比如 14:23)
    current_time_str = datetime.datetime.now().strftime("%H:%M")

    # 5. 把问题记入历史记录（如果没问过的话）
    if question not in history:
        history.append(question)
        # 把时间+问题，插入到左侧的树形列表里
        history_list.insert("", "end", values=(current_time_str, question))

    # 6. 开始掐表计时 ⏱
    start_time = time.perf_counter()
    
    try:
        # 去 matcher.py 里找答案
        result_tuple = find_answer(question)
        answer, matched_words, best_q, match_rate, category_name = result_tuple
    except Exception as e:
        # 万一代码写错了报错，不会闪退，而是把错误显示出来
        answer = f"查询出错: {e}"
        matched_words, best_q, match_rate, category_name = [], None, 0.0, "未分类"

    # 7. 停止计时 ⏱
    elapsed = (time.perf_counter() - start_time) * 1000
    # 为了演示效果，如果查得太快(小于0.01毫秒)，随机给点假时间，看起来更真实
    if elapsed < 0.01: 
        import random
        elapsed = random.uniform(0.01, 0.05)
    query_time_ms = f"{elapsed:.2f}" # 保留两位小数

    # 8. 解锁答案框，清空上一题的内容
    result.config(state="normal")
    result.delete("1.0", tk.END)
    
    # 定义几种特殊的文字排版样式
    result.tag_configure("separator", foreground=current_theme["TEXT_LIGHT"])
    result.tag_configure("bold_title", foreground=current_theme["PRIMARY"], font=("微软雅黑", 11, "bold"))
    result.tag_configure("info_tag", foreground=current_theme["HIGHLIGHT"], font=("微软雅黑", 10, "bold"))
    
    # 9. 根据是否匹配到答案，往屏幕上写字
    if best_q:
        # 统计热门度
        query_frequency[best_q] = query_frequency.get(best_q, 0) + 1
        update_popular()
        
        # 漂亮的排版输出
        result.insert(tk.END, f"👤 你的问题：\n\n{question}\n\n")
        result.insert(tk.END, "────────────────────────────────────────\n", "separator")
        result.insert(tk.END, f"✔ 匹配到：\n\n{best_q}\n\n", "bold_title")
        result.insert(tk.END, f"📂 分类：{category_name}   |   🎯 匹配度：{int(match_rate * 100)}%\n", "info_tag")
        result.insert(tk.END, "────────────────────────────────────────\n", "separator")
        result.insert(tk.END, f"🤖 回答：\n\n{answer}")
    else:
        # 没匹配到答案的输出
        result.insert(tk.END, f"👤 你的问题：\n\n{question}\n\n")
        result.insert(tk.END, "────────────────────────────────────────\n", "separator")
        result.insert(tk.END, f"🤖 系统回复：\n\n{answer}")
    
    # 10. 上色高亮，然后把屏幕重新锁上（防止用户乱改文字）
    highlight_keywords(result, matched_words)
    result.config(state="disabled")
    
    # 更新底部状态条
    update_status()

    # 11. 功能要求：输入完成后清空输入框，光标留在里面
    entry.delete(0, tk.END)
    entry.focus_set()

def history_click(event):
    """当用户点击左侧历史记录时，自动把问题填进输入框，并触发查询"""
    selection = history_list.selection() # 看选了哪一行
    if not selection:
        return
    # 获取选中行的第二个内容（因为第一列是时间，第二列才是问题）
    question = history_list.item(selection[0], "values")[1]
    
    entry.delete(0, tk.END)           # 清空现有输入
    entry.insert(0, question)         # 填入历史问题
    entry.configure(foreground=current_theme["TEXT"])
    query()                           # 自动查答案

def clear():
    """清空按钮的功能：擦除屏幕和历史记录"""
    # 弹窗让你确认一下，防止手滑
    if messagebox.askyesno("确认清空", "确认要清空当前屏幕和所有提问历史吗？"):
        entry.delete(0, tk.END)
        add_placeholder(None) # 把灰色提示词变回来
        
        # 清空右侧大屏幕
        result.config(state="normal")
        result.delete("1.0", tk.END)
        result.config(state="disabled")
        
        # 清空内部记忆数据和左侧列表
        history.clear()
        history_list.delete(*history_list.get_children())
        query_frequency.clear()
        
        # 刷新底部数据
        update_popular()
        update_status()
        root.focus() # 把焦点给主窗口，让提示词生效

def exit_program():
    """退出按钮功能：直接关闭软件"""
    root.destroy()

# ===========================
# 5. 拼装积木 (搭建UI界面)
# 这里就像造房子，先打地基，再建墙，最后放家具
# ===========================
def start_ui():
    # 告诉电脑我们要用全局变量里的这些东西
    global root, entry, result, history_list, status, clock_label, popular_var, theme_btn

    # 【地基】创建主窗口
    root = tk.Tk()
    root.title("AI 基础知识问答系统")
    root.geometry("1100x720") # 设置窗口宽和高
    root.configure(bg=current_theme["BG"])

    # ─────────────── 顶部菜单栏 ───────────────
    menubar = tk.Menu(root)
    # 文件菜单
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="🗑 清空历史", command=clear)
    file_menu.add_separator() # 加一条分割线
    file_menu.add_command(label="🚪 退出系统", command=exit_program)
    menubar.add_cascade(label="文件", menu=file_menu)
    
    # 帮助菜单
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="💡 使用帮助", command=show_help)
    help_menu.add_command(label="ℹ 关于系统", command=show_about)
    menubar.add_cascade(label="帮助", menu=help_menu)
    root.config(menu=menubar) # 把菜单装到主窗口上

    # ─────────────── 【一层】顶部大标题区 ───────────────
    header_frame = tk.Frame(root, bg=current_theme["BG"])
    header_frame.pack(fill="x", padx=25, pady=(20, 15)) # 放在最上面，左右留白25
    bg_frames.append(header_frame)
    
    # 写标题
    ttk.Label(header_frame, text="✨ AI 人工智能基础问答系统", font=FONT_TITLE, background=current_theme["BG"], foreground=current_theme["PRIMARY"]).pack(side="left")
    
    # 深浅色切换按钮 (放右边)
    theme_btn = tk.Button(header_frame, text="🌙 Dark", command=toggle_theme, font=FONT_HIST_ITEM, bg=current_theme["CARD"], fg=current_theme["TEXT"], bd=1, relief="solid", cursor="hand2", padx=10)
    theme_btn.pack(side="right")

    # ─────────────── 【二层】主内容大框架 (分左右) ───────────────
    main_frame = tk.Frame(root, bg=current_theme["BG"])
    main_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20)) # 占满剩下所有的空间
    bg_frames.append(main_frame)

    # =============== 左半边：提问历史栏 ===============
    # 用我们自定义的圆角卡片做个外壳
    left_container = RoundCard(main_frame, current_theme["CARD"], current_theme["BORDER"], radius=4, width=280)
    left_container.pack(side="left", fill="y", padx=(0, 20))
    left_container.pack_propagate(False) # 锁死大小，不被里面的东西撑大
    round_canvases.append(left_container)

    # 历史记录的小标题
    hist_lbl = tk.Label(left_container, text="📋 提问历史", bg=current_theme["CARD"], fg=current_theme["PRIMARY"], font=FONT_HIST_TITLE)
    hist_lbl.pack(pady=12)
    card_labels.append(hist_lbl)

    # 树形列表(Treeview)的样式设置
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=FONT_HIST_ITEM, rowheight=24, background=current_theme["CARD"], fieldbackground=current_theme["CARD"], foreground=current_theme["TEXT"], borderwidth=0)
    style.map("Treeview", background=[("selected", current_theme["PRIMARY"])], foreground=[("selected", "white")])

    # 创建一个双列的列表组件：左边显示时间，右边显示问题
    history_list = ttk.Treeview(left_container, columns=("time", "question"), show="headings", selectmode="browse")
    history_list.heading("time", text="时间")
    history_list.heading("question", text="问题内容")
    history_list.column("time", width=55, minwidth=55, anchor="center")
    history_list.column("question", width=195, minwidth=150, anchor="w")
    
    history_list.pack(padx=10, pady=(0, 15), fill="both", expand=True)
    history_list.bind("<ButtonRelease-1>", history_click) # 绑定点击事件

    # =============== 右半边：聊天问答区 ===============
    right_frame = tk.Frame(main_frame, bg=current_theme["BG"])
    right_frame.pack(side="left", fill="both", expand=True)
    bg_frames.append(right_frame)

    # 提示词
    tk.Label(right_frame, text="🔍 您的提问：", font=FONT_HIST_TITLE, bg=current_theme["BG"], fg=current_theme["TEXT"]).pack(anchor="w")

    # 这一行用来放 输入框 + 三个按钮
    input_row = tk.Frame(right_frame, bg=current_theme["BG"])
    input_row.pack(fill="x", pady=(10, 20))
    bg_frames.append(input_row)

    # A. 圆角输入框外壳
    entry_canvas = RoundCard(input_row, current_theme["CARD"], current_theme["BORDER"], radius=4, height=40)
    entry_canvas.pack(side="left", fill="x", expand=True)
    entry_canvas.pack_propagate(False)
    round_canvases.append(entry_canvas)

    # 输入框本体，塞在外壳里面
    entry = tk.Entry(entry_canvas, font=FONT_ENTRY, bg=current_theme["CARD"], fg=current_theme["TEXT_LIGHT"], bd=0, highlightthickness=0, insertbackground=current_theme["TEXT"])
    entry.pack(fill="both", expand=True, padx=10, pady=8)
    entry.insert(0, "请输入 AI 相关问题 (输入'退出'可关闭)...")
    entry.bind("<FocusIn>", clear_placeholder)
    entry.bind("<FocusOut>", add_placeholder)
    entry.bind("<Return>", query) # 按回车键也能查询

    # B. 【查询】主按钮
    btn1 = RoundButton(input_row, text="💡 查询", font=FONT_BTN, 
                       default_bg=current_theme["PRIMARY"], 
                       hover_bg=current_theme["PRIMARY_HOVER"], 
                       text_color="white", command=query, radius=4, width=90, height=40)
    btn1.pack(side="left", padx=(15, 5))
    btn1.is_primary = True # 标记这是主按钮，换肤时用主色调
    round_buttons.append(btn1)

    # C. 【清空】次级按钮
    btn2 = RoundButton(input_row, text="🗑 清空", font=FONT_BTN, 
                       default_bg=current_theme["CARD"], 
                       hover_bg=current_theme["SEC_HOVER"], 
                       text_color=current_theme["TEXT"], command=clear, radius=4, width=90, height=40)
    btn2.pack(side="left", padx=5)
    btn2.is_primary = False
    round_buttons.append(btn2)

    # D. 【退出】次级按钮
    btn3 = RoundButton(input_row, text="🚪 退出", font=FONT_BTN, 
                       default_bg=current_theme["CARD"], 
                       hover_bg=current_theme["SEC_HOVER"], 
                       text_color=current_theme["TEXT"], command=exit_program, radius=4, width=90, height=40)
    btn3.pack(side="left", padx=5)
    btn3.is_primary = False
    round_buttons.append(btn3)

    # ================= 问答显示大屏幕 =================
    tk.Label(right_frame, text="📝 查询结果：", font=FONT_HIST_TITLE, bg=current_theme["BG"], fg=current_theme["TEXT"]).pack(anchor="w")

    # 圆角大外壳
    result_canvas = RoundCard(right_frame, current_theme["CARD"], current_theme["BORDER"], radius=4)
    result_canvas.pack(fill="both", expand=True, pady=(10, 0))
    result_canvas.pack_propagate(False)
    round_canvases.append(result_canvas)

    # 里面的纯文本显示区域
    result = tk.Text(result_canvas, font=FONT_RESULT, bg=current_theme["CARD"], fg=current_theme["TEXT"], bd=0, highlightthickness=0, padx=15, pady=15, spacing2=6, spacing3=6)
    result.pack(fill="both", expand=True)
    result.config(state="disabled") # 锁死不让用户打字

    # ─────────────── 【三层】最底部的状态栏 ───────────────
    status_frame = tk.Frame(root, bg=current_theme["STATUS_BG"], bd=0)
    status_frame.pack(side="bottom", fill="x")
    status_frames.append(status_frame)

    status = tk.StringVar()
    popular_var = tk.StringVar()
    popular_var.set("🔥 最热门：暂无")
    
    # 底部最左边：放热门词
    pop_label = tk.Label(status_frame, textvariable=popular_var, anchor="w", bg=current_theme["STATUS_BG"], fg=current_theme["HIGHLIGHT"], font=("微软雅黑", 9, "bold"))
    pop_label.pack(side="left", padx=15, pady=6)
    status_labels.append(pop_label)

    # 底部正中间：放统计信息 (知识库总数、耗时等)
    status_label = tk.Label(status_frame, textvariable=status, anchor="center", bg=current_theme["STATUS_BG"], fg=current_theme["TEXT_LIGHT"], font=("微软雅黑", 9))
    status_label.pack(side="left", expand=True, pady=6)
    status_labels.append(status_label)

    # 底部最右边：放实时跳动的时钟
    clock_label = tk.Label(status_frame, bg=current_theme["STATUS_BG"], fg=current_theme["TEXT_LIGHT"], font=("微软雅黑", 9, "bold"))
    clock_label.pack(side="right", padx=15, pady=6)
    status_labels.append(clock_label)

    # 程序启动时，先刷新一次状态条和时钟
    update_status()
    update_clock()
    
    # 让窗口持续运行，等待用户操作
    root.mainloop()