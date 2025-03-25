import PySimpleGUI as sg
from PIL import Image, ImageGrab
import io

def save_canvas_to_png(canvas_key, filename="canvas.png"):
    """
    PySimpleGUIのCanvasの内容をPNG画像として保存します。

    Args:
        canvas_key (str): Canvas要素のキー。
        filename (str): 保存するPNGファイルのパスと名前。
    """
    canvas = window[canvas_key].TKCanvas
    x = root.winfo_rootx() + canvas.winfo_x()
    y = root.winfo_rooty() + canvas.winfo_y()
    x1 = x + canvas.winfo_width()
    y1 = y + canvas.winfo_height()

    try:
        image = ImageGrab.grab().crop((x, y, x1, y1))
        image.save(filename, "PNG")
        print(f"Canvasの内容を {filename} に保存しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# PySimpleGUIのレイアウト
layout = [
    [sg.Canvas(key="-CANVAS-", size=(300, 200))],
    [sg.Button("描画"), sg.Button("保存"), sg.Button("終了")]
]

window = sg.Window("Canvas to PNG", layout)
root = window.TKroot  # Tkinterのrootオブジェクトを取得

# Canvasに描画する例
# canvas = window["-CANVAS-"].TKCanvas
# canvas.create_rectangle(50, 50, 250, 150, fill="lightblue")
# canvas.create_text(150, 100, text="Hello Canvas!", font=("Arial", 20))

while True:
    event, values = window.read()
    root = window.TKroot

    if event == sg.WIN_CLOSED or event == "終了":
        break
    if event == "描画":
        # ここに描画処理を追加
        canvas = window["-CANVAS-"].TKCanvas
        canvas.create_rectangle(50, 50, 250, 150, fill="lightblue")
        canvas.create_text(150, 100, text="Hello Canvas!", font=("Arial", 20))
        x1 =  canvas.winfo_width()
        y1 =  canvas.winfo_height()
        print(x1,y1)
    if event == "保存":
        save_canvas_to_png("-CANVAS-")

window.close()