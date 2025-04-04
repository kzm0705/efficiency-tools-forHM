import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import ImageGrab, Image

# PDF情報を管理する変数
pdf_doc = None
current_page = 0
stamp_position = None  # 捺印位置（x, y）

# PDFのプレビューを表示する関数（サイズ調整済み）
def show_preview():
    global pdf_doc, current_page
    if pdf_doc is None:
        return
    try:
        # 現在のページの画像を取得（適切な拡大率で調整）
        pix = pdf_doc[current_page].get_pixmap()  # A4縦横対応 引数matrix=fitz.Matrix(0.55, 0.55)
        # print(pix)
        img_data = pix.tobytes("ppm")  # PPM形式に変換
        
        # Tkinterで表示
        img = tk.PhotoImage(data=img_data)
        preview_label.config(image=img)
        preview_label.image = img  # 参照を保持
        page_info_label.config(text=f"ページ {current_page + 1} / {len(pdf_doc)}")
    
    except Exception as e:
        messagebox.showerror("エラー", f"プレビュー表示に失敗しました: {e}")

#PDFファイルを画像に変換 (kzmのコード)
def pdf_to_image(pdf_file, page_count):
    pdf = fitz.open(pdf_file)
    pdf_page = pdf[page_count]
    pix = pdf_page.get_pixmap()
    # print(pix)
    data = pix.tobytes()
    pdf.close()
    return data

# 次のページを表示
def next_page():
    global current_page, pdf_doc
    if pdf_doc and current_page < len(pdf_doc) - 1:
        current_page += 1
        show_preview()

# 前のページを表示
def prev_page():
    global current_page, pdf_doc
    if pdf_doc and current_page > 0:
        current_page -= 1
        show_preview()

# PDFファイルを選択してプレビューを表示
def select_file():
    global pdf_doc, current_page
    file_path = filedialog.askopenfilename(filetypes=[("PDFファイル", "*.pdf")])
    if file_path:
        file_path_var.set(file_path)
        pdf_doc = fitz.open(file_path)  # PDFを開く
        current_page = 0
        show_preview()

# PDFを分割する関数
def split_pdf():
    global pdf_doc
    input_pdf = pdf_doc
    output_dir = output_dir_var.get()
    
    if not input_pdf:
        messagebox.showerror("エラー", "PDFファイルを選択してください")
        return
    if not output_dir:
        messagebox.showerror("エラー", "出力フォルダを選択してください")
        return

    try:
        doc = fitz.open(input_pdf)

        if doc.page_count != 4:
            messagebox.showerror("エラー", "PDFのページ数が4ではありません")
            return

        base_name = os.path.basename(input_pdf).replace(".pdf", "")
        if not base_name.startswith("注文書一式"):
            messagebox.showerror("エラー", "ファイル名が「注文書一式」で始まっていません")
            return
        custom_part = base_name.replace("注文書一式_", "")

        os.makedirs(output_dir, exist_ok=True)

        for i, prefix in enumerate(["A", "B", "C", "D"]):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)

            new_filename = f"{prefix}_{custom_part}.pdf"
            new_filepath = os.path.join(output_dir, new_filename)

            new_doc.save(new_filepath)
            new_doc.close()

        doc.close()
        messagebox.showinfo("完了", "PDFを4つに分割しました！")

    except Exception as e:
        messagebox.showerror("エラー", f"処理中にエラーが発生しました: {e}")

# 出力フォルダ選択
def select_output_dir():
    output_dir = filedialog.askdirectory()
    output_dir_var.set(output_dir)

# D&Dでファイルを受け取る
def drop(event):
    file_path = event.data.strip()
    if file_path.startswith("{") and file_path.endswith("}"):
        file_path = file_path[1:-1]
    
    if file_path.lower().endswith(".pdf"):
        file_path_var.set(file_path)
        global pdf_doc, current_page
        pdf_doc = fitz.open(file_path)
        current_page = 0
        show_preview()
    else:
        messagebox.showerror("エラー", "PDFファイルをドロップしてください")

#ハンコの名前を生成　（kzm's code)
def embedded_name(canvas, name='名前', size=15):
    create_circle(canvas)
    canvas.create_text(50,50, text=stamp_set_name(name), fill='red', font=('Helvetica', size), tag='text')

#（kzm's code)
def stamp_set_name(name):
    var_name = ""
    for i in range(len(name)):
        if i != len(name) -1 :
            var_name += f'{name[i]}\n'
        else: var_name += f'{name[i]}'
    return var_name

# （kzm's code)
def create_circle(canvas,radius=25):

    center_x = 50  # 円の中心のX座標
    center_y = 50  # 円の中心のY座標
    color = 'white'  # 円の色
    canvas.create_oval(center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        outline='red',width=2, tag='circle')
    
def create_stamp_png(canvas,canvas_widget, circle_radius):
    #画面上のcanvasの絶対位置
    abs_x = canvas.winfo_rootx()
    abs_y = canvas.winfo_rooty()

    #canvasのwidthとheight
    width =  canvas.winfo_width()
    height =  canvas.winfo_height()

    out_circle = 50 - int(circle_radius)

    left_x = abs_x + out_circle
    left_y = abs_y + out_circle

    right_x = left_x + width - 2*out_circle + 1
    right_y = left_y + height - 2*out_circle + 1

    #png画像を生成
    image = ImageGrab.grab().crop((left_x, left_y, right_x, right_y))
    image.save('temp/test.png')

#はまのコード
def set_stamp_position(event):
    global stamp_position, pdf_doc

    x,y = stamp_position = (event.x, event.y)
    stamp_label.config(text=f"捺印位置: x={event.x}, y={event.y}")
    pdf_doc = fitz.open(file_path_var.get())
    show_preview()
    pdf_path = stamp_in_viewer(x, y , file_path_var.get(), current_page, 25)
    pdf_doc = fitz.open(pdf_path)
    show_preview()

#俺のコード
def stamp_in_viewer(loc_x,loc_y,input_path, page_count, radius):
    doc = fitz.open(input_path)
    rect = (loc_x - radius ,loc_y - radius,loc_x + radius, loc_y + radius)
    if os.path.exists('temp/test.pdf'):
        os.remove('temp/test.pdf')
    img = open("temp/test.png", "rb").read()
    for i,page in enumerate(doc):
        if i == page_count:
            page.insert_image(rect, stream=img)
            doc.save(f'temp/test.pdf')
        else:pass
    return 'temp/test.pdf'

def four_split_pdf():
    global pdf_doc
    input_path = pdf_doc
    output_path = output_dir_var.get()

    for i in range(4):
        doc = fitz.open(input_path)
        doc.select([i])
        doc.save(f"{output_path}/test-page-copied{i}.pdf") 
        doc.close()


# GUIの作成---------------------------------------------------------
root = TkinterDnD.Tk()
root.title("PDF分割ツール")
root.geometry("700x770")  # GUIサイズを調整
root.configure(bg='#00AAAA')

# ファイル選択--------------------------------------------------------
label_1 = tk.Label(root, text="PDFファイルを選択（D&D可）:")
file_path_var = tk.StringVar()
file_entry = tk.Entry(root, textvariable=file_path_var, width=60)

file_entry.drop_target_register(DND_FILES)
file_entry.dnd_bind("<<Drop>>", drop)
input_file_btn = tk.Button(root, text="ファイルを選択", command=select_file)

print(file_path_var.get())
label_1.grid(row=0, column=0)
file_entry.grid(row=1, column=0, padx=10)
input_file_btn.grid(row=1, column=1)

# 出力フォルダ選択--------------------------------------------
label_2= tk.Label(root, text="出力フォルダ:")
output_dir_var = tk.StringVar()
output_dir = tk.Entry(root, textvariable=output_dir_var, width=60)
output_dir_btn = tk.Button(root, text="フォルダを選択", command=select_output_dir)    

label_2.grid(row=2, column=0)
output_dir.grid(row=3, column=0, padx=10)
output_dir_btn.grid(row=3, column=1)

#ハンコ生成------------------------------------------------------
label_3 = tk.Label(root, text='ハンコ')
input = tk.Entry(root, width=12)
canvas = tk.Canvas(root, width=100, height=100, bg='black')
stamp_set_btn = tk.Button(root, text='セット', command=lambda: embedded_name(canvas, input.get()))
stamp_gen_btn = tk.Button(root, text='生成', command=lambda: create_stamp_png(canvas,25, 25))


label_3.grid(row=4, column=0)
input.grid(row=5, column=0, columnspan=1)
stamp_set_btn.grid(row=5,column=1, sticky='w')
stamp_gen_btn.grid(row=5, column=1,sticky='e')
canvas.grid(row=5, column=2)


# 実行ボタン---------------------------------------------------------------
execute_btn = tk.Button(root, text="PDFを分割", command=four_split_pdf, bg="blue", fg="white")

execute_btn.grid(row=1, column=2, columnspan=2)


# ページ切り替えボタン----------------------------------------------------
nav_frame = tk.Frame(root)
prev_pg_btn = tk.Button(nav_frame, text="← 前のページ", command=prev_page)
page_info_label = tk.Label(nav_frame, text="ページ 0 / 0")
next_pg_btn = tk.Button(nav_frame, text="次のページ →", command=next_page)

# PDFプレビュー（ナビゲーションの下に配置）----------------------------------------
preview_label = tk.Label(root)


nav_frame.grid(row=6, column=0, columnspan=3)
prev_pg_btn.grid(row=0,column=0)
next_pg_btn.grid(row=0,column=2)
page_info_label.grid(row=0, column=3)

preview_label.grid(row=7, column=0,columnspan=3, padx=10, pady=20)

# プレビュー（クリックで捺印位置設定）
preview_label = tk.Label(root)
preview_label.grid(row=7, column=0)
preview_label.bind("<Button-1>",set_stamp_position)

# 捺印位置表示
stamp_label = tk.Label(root, text="捺印位置: 未設定")
stamp_label.grid(row=7, column=1)




# GUI起動-------------------------------------------------------------------------------------------------
root.mainloop()
