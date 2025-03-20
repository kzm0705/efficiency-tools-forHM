import fitz
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

class PDFViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF分割ツール")
        self.root.geometry("700x650")

        self.pdf_path = None
        self.output_dir = None
        self.page_count = 0
        self.current_page = 0
        self.pdf_doc = None
        self.hanko_name = "名前"
        self.hanko_size = 15
        self.hanko_position = (50, 50)  # デフォルト座標

        self.setup_ui()

    def setup_ui(self):
        # PDF選択ボタン
        self.btn_select_pdf = tk.Button(self.root, text="PDFを選択", command=self.select_pdf)
        self.btn_select_pdf.pack(pady=5)

        # PDFプレビュー (小さめ)
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="gray")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.set_hanko_position)  # クリックでハンコ座標設定

        # ページコントロール
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        self.btn_prev = tk.Button(control_frame, text="前へ", command=self.prev_page, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, padx=10)

        self.page_label = tk.Label(control_frame, text="0 / 0")
        self.page_label.pack(side=tk.LEFT)

        self.btn_next = tk.Button(control_frame, text="次へ", command=self.next_page, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT, padx=10)

        # ハンコ設定
        self.hanko_frame = tk.Frame(self.root)
        self.hanko_frame.pack(pady=5)

        tk.Label(self.hanko_frame, text="捺印名 (最大4文字):").grid(row=0, column=0)
        self.hanko_entry = tk.Entry(self.hanko_frame, width=5)
        self.hanko_entry.grid(row=0, column=1)
        self.hanko_entry.insert(0, self.hanko_name)

        self.hanko_size_slider = tk.Scale(self.hanko_frame, from_=10, to=50, orient=tk.HORIZONTAL, label="サイズ")
        self.hanko_size_slider.set(self.hanko_size)
        self.hanko_size_slider.grid(row=1, column=0, columnspan=2)

        self.btn_generate_hanko = tk.Button(self.hanko_frame, text="ハンコ生成", command=self.generate_hanko)
        self.btn_generate_hanko.grid(row=2, column=0, columnspan=2)

        # 出力フォルダ選択 & PDF保存
        self.btn_select_output = tk.Button(self.root, text="出力フォルダ選択", command=self.select_output)
        self.btn_select_output.pack(pady=5)

        self.btn_save_pdf = tk.Button(self.root, text="PDF分割保存", command=self.split_and_save_pdf, state=tk.DISABLED)
        self.btn_save_pdf.pack(pady=5)

    def select_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.pdf_path:
            self.load_pdf()

    def load_pdf(self):
        try:
            self.pdf_doc = fitz.open(self.pdf_path)
            self.page_count = len(self.pdf_doc)
            self.current_page = 0
            self.update_page()
            self.btn_next.config(state=tk.NORMAL if self.page_count > 1 else tk.DISABLED)
            self.btn_save_pdf.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("エラー", f"PDFの読み込みに失敗しました: {e}")

    def update_page(self):
        if not self.pdf_doc:
            return

        pix = self.pdf_doc[self.current_page].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.thumbnail((400, 400))  # サイズ調整
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(200, 200, image=self.photo)  # キャンバス中央

        self.page_label.config(text=f"{self.current_page + 1} / {self.page_count}")

    def next_page(self):
        if self.current_page < self.page_count - 1:
            self.current_page += 1
            self.update_page()
        self.btn_prev.config(state=tk.NORMAL)
        if self.current_page == self.page_count - 1:
            self.btn_next.config(state=tk.DISABLED)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()
        self.btn_next.config(state=tk.NORMAL)
        if self.current_page == 0:
            self.btn_prev.config(state=tk.DISABLED)

    def select_output(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            messagebox.showinfo("フォルダ選択", f"出力フォルダ: {self.output_dir}")

    def split_and_save_pdf(self):
        if not self.pdf_doc or not self.output_dir:
            messagebox.showwarning("警告", "PDFまたは出力フォルダが選択されていません")
            return

        try:
            for i in range(min(4, self.page_count)):  # 4ページに分割
                doc = fitz.open()
                doc.insert_pdf(self.pdf_doc, from_page=i, to_page=i)

                # ハンコを押す
                page = doc[0]
                page.insert_textbox(self.hanko_position, self.hanko_name, fontsize=self.hanko_size, color=(1, 0, 0))

                output_path = os.path.join(self.output_dir, f"split_page_{i + 1}.pdf")
                doc.save(output_path)
                doc.close()
            messagebox.showinfo("完了", "PDFを分割して保存しました")
        except Exception as e:
            messagebox.showerror("エラー", f"PDFの保存に失敗しました: {e}")

    def generate_hanko(self):
        self.hanko_name = self.hanko_entry.get()[:4]
        self.hanko_size = self.hanko_size_slider.get()

        hanko_img = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(hanko_img)
        draw.ellipse((5, 5, 95, 95), outline="red", width=3)

        try:
            font = ImageFont.truetype("arial.ttf", self.hanko_size)
        except:
            font = ImageFont.load_default()

        text_x = 50 - (self.hanko_size // 2)
        text_y = 30
        for char in self.hanko_name:
            draw.text((text_x, text_y), char, fill="red", font=font)
            text_y += self.hanko_size

        self.hanko_photo = ImageTk.PhotoImage(hanko_img)
        self.canvas.create_image(*self.hanko_position, image=self.hanko_photo)  # クリック座標に表示

    def set_hanko_position(self, event):
        self.hanko_position = (event.x, event.y)
        self.generate_hanko()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewerApp(root)
    root.mainloop()
