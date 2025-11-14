import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os


class ImageAnalyzerApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.master = master
        self.master.title('Лабораторная работа №1 — Анализ изображения')
        self.master.geometry('1000x700')
        self.grid(sticky='nsew')

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.current_image = None
        self.photo_image = None

        self._create_styles()
        self._create_topbar()
        self._create_main_panes()
        self._create_statusbar()

    def _create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', padding=6)
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Small.TLabel', font=('Segoe UI', 10))

    def _create_topbar(self):
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky='ew', pady=(0,8))
        top.columnconfigure(2, weight=1)

        title = ttk.Label(top, text='Анализатор изображения — Лабораторная №1', style='Header.TLabel')
        title.grid(row=0, column=0, sticky='w')

        btn_open = ttk.Button(top, text='Открыть изображение...', command=self.open_image)
        btn_open.grid(row=0, column=1, sticky='e', padx=6)

        samples = ttk.Frame(top)
        samples.grid(row=0, column=2, sticky='e')
        ttk.Button(samples, text='Пример 1', command=lambda: self.load_image_from_path('photo_2023-12-01_16-32-10.jpg')).grid(row=0, column=0, padx=4)
        ttk.Button(samples, text='Пример 2', command=lambda: self.load_image_from_path('photo_2023-12-16_16-28-34.jpg')).grid(row=0, column=1, padx=4)

    def _create_main_panes(self):
        main = ttk.Panedwindow(self, orient='horizontal')
        main.grid(row=1, column=0, sticky='nsew')

        left = ttk.Frame(main, width=420)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        lbl = ttk.Label(left, text='Превью', style='Small.TLabel')
        lbl.grid(row=0, column=0, sticky='w')

        self.canvas = tk.Canvas(left, background='#f2f2f2')
        self.canvas.grid(row=1, column=0, sticky='nsew', padx=6, pady=6)

        controls = ttk.Frame(left)
        controls.grid(row=2, column=0, sticky='ew', pady=(6,0))
        controls.columnconfigure(1, weight=1)

        self.btn_hist = ttk.Button(controls, text='Показать гистограммы RGB', command=self.show_rgb_hist, state='disabled')
        self.btn_hist.grid(row=0, column=0, padx=4)
        self.btn_dom = ttk.Button(controls, text='Показать преобладающие', command=self.show_dominant_chart, state='disabled')
        self.btn_dom.grid(row=0, column=1, padx=4)

        right = ttk.Frame(main, width=560)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        info = ttk.Frame(right)
        info.grid(row=0, column=0, sticky='ew')
        info.columnconfigure(1, weight=1)

        self.avg_label = ttk.Label(info, text='Средние значения: —', style='Small.TLabel')
        self.avg_label.grid(row=0, column=0, sticky='w')

        self.color_sample = ttk.Frame(info)
        self.color_sample.grid(row=0, column=1, sticky='e')

        self.fig = Figure(figsize=(6,4), dpi=100)
        self.ax_r = self.fig.add_subplot(131)
        self.ax_g = self.fig.add_subplot(132)
        self.ax_b = self.fig.add_subplot(133)
        self.fig.tight_layout()

        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas_fig.get_tk_widget().grid(row=1, column=0, sticky='nsew', padx=6, pady=6)

        main.add(left)
        main.add(right)

    def _create_statusbar(self):
        status = ttk.Frame(self)
        status.grid(row=2, column=0, sticky='ew', pady=(6,0))
        self.status_var = tk.StringVar(value='Готово')
        ttk.Label(status, textvariable=self.status_var, style='Small.TLabel').grid(row=0, column=0, sticky='w')

    def set_status(self, text):
        self.status_var.set(text)
        self.master.update_idletasks()

    def open_image(self):
        filetypes = [('Image files', '*.png *.jpg *.jpeg *.bmp *.gif'), ('All files', '*.*')]
        path = filedialog.askopenfilename(title='Выберите изображение', filetypes=filetypes)
        if path:
            self.load_image_from_path(path)

    def load_image_from_path(self, path):
        if not os.path.isfile(path):
            self.set_status(f'Файл не найден: {path} — выберите свой файл.')
            return
        try:
            img = Image.open(path)
        except Exception as e:
            messagebox.showerror('Ошибка', f'Невозможно открыть изображение:\n{e}')
            return

        self.current_image = img.convert('RGB')
        self.display_image()
        self.analyze_and_update()
        self.set_status(f'Открыт: {os.path.basename(path)}')

    def display_image(self):
        canvas_w = self.canvas.winfo_width() or 400
        canvas_h = self.canvas.winfo_height() or 300
        img = self.current_image.copy()
        img.thumbnail((canvas_w-10, canvas_h-10), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(img)
        self.canvas.delete('all')
        self.canvas.create_image(canvas_w//2, canvas_h//2, image=self.photo_image, anchor='center')

    def analyze_and_update(self):
        if self.current_image is None:
            return
        arr = np.array(self.current_image)
        pixels = arr.reshape(-1, 3)

        avg = pixels.mean(axis=0)
        avg_r, avg_g, avg_b = avg.tolist()

        self.avg_label.config(text=f'Средняя интенсивность — R: {avg_r:.2f}, G: {avg_g:.2f}, B: {avg_b:.2f}')

        for child in self.color_sample.winfo_children():
            child.destroy()
        frm = tk.Frame(self.color_sample, width=60, height=20, bg=f'#{int(avg_r):02x}{int(avg_g):02x}{int(avg_b):02x}', relief='sunken', bd=1)
        frm.pack(side='left', padx=2)

        self.btn_hist.config(state='normal')
        self.btn_dom.config(state='normal')

        self.hist_r, _ = np.histogram(pixels[:,0], bins=256, range=(0,255))
        self.hist_g, _ = np.histogram(pixels[:,1], bins=256, range=(0,255))
        self.hist_b, _ = np.histogram(pixels[:,2], bins=256, range=(0,255))

        self._draw_inline_histograms()

    def _draw_inline_histograms(self):
        self.ax_r.clear(); self.ax_g.clear(); self.ax_b.clear()
        x = np.arange(256)
        self.ax_r.bar(x, self.hist_r, width=1.0, color='red')
        self.ax_r.set_title('R')
        self.ax_r.set_xlabel('Интенсивность')

        self.ax_g.bar(x, self.hist_g, width=1.0, color='green')
        self.ax_g.set_title('G')
        self.ax_g.set_xlabel('Интенсивность')

        self.ax_b.bar(x, self.hist_b, width=1.0, color='blue')
        self.ax_b.set_title('B')
        self.ax_b.set_xlabel('Интенсивность')

        self.canvas_fig.draw()

    def show_rgb_hist(self):
        if self.current_image is None:
            return
        win = tk.Toplevel(self.master)
        win.title('Гистограммы RGB (подробно)')
        fig = Figure(figsize=(9,3), dpi=100)
        ax1 = fig.add_subplot(131)
        ax2 = fig.add_subplot(132)
        ax3 = fig.add_subplot(133)
        x = np.arange(256)
        ax1.bar(x, self.hist_r, width=1.0, color='red')
        ax1.set_title('Red')
        ax2.bar(x, self.hist_g, width=1.0, color='green')
        ax2.set_title('Green')
        ax3.bar(x, self.hist_b, width=1.0, color='blue')
        ax3.set_title('Blue')
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        canvas.draw()

    def show_dominant_chart(self):
        arr = np.array(self.current_image)
        pixels = arr.reshape(-1,3)
        r = pixels[:,0]; g = pixels[:,1]; b = pixels[:,2]
        count_r = np.sum((r>=g) & (r>=b))
        count_g = np.sum((g>r) & (g>=b))
        count_b = np.sum((b>r) & (b>g))

        win = tk.Toplevel(self.master)
        win.title('Преобладающие пиксели')
        fig = Figure(figsize=(6,3), dpi=100)

        ax = fig.add_subplot(121)
        ax.bar(['Red','Green','Blue'], [count_r, count_g, count_b], color=['red','green','blue'])
        ax.set_ylabel('Количество пикселей')
        ax.set_title('Преобладание (по цветам)')

        ax2 = fig.add_subplot(122)
        ax2.pie([count_r, count_g, count_b], labels=['Red','Green','Blue'], autopct='%1.1f%%', colors=['red','green','blue'])
        ax2.set_title('Процентное соотношение (по цветам)')

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        canvas.draw()


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageAnalyzerApp(root)

    def on_resize(event):
        if app.current_image is not None:
            app.display_image()
    root.bind('<Configure>', on_resize)

    root.mainloop()
