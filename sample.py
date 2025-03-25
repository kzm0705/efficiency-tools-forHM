import PySimpleGUI as sg
import fitz
from PIL import Image, ImageDraw
import io

theme = sg.theme('DarkBlack1')

column_layout = [
    [sg.Input(size=(10, 2), key='-name-'), sg.Button('ハンコ生成', key='-generate-', button_color=('white', 'green'), enable_events=True, )],
    [sg.Slider(range=(5, 25), default_value=15, orientation="h", enable_events=True, key='-text_size-')]
]

frame_1 = [
    [sg.Text('入力ファイル: ')],
    [sg.Input(size=(45, 1), key='-input-', enable_events=True), sg.FileBrowse(file_types=(('PDFファイル', '*.pdf'),))],
    # 出力ファイル
    [sg.Text('出力先フォルダ:', pad=((0, 0), (20, 5)))],
    [sg.Input(size=(45, 1), key='-output-'), sg.FolderBrowse()],
    # ハンコ
    [sg.Text('捺印する名前を入力してください(最大で四文字まで):', pad=((0, 0), (20, 5)))],
    [sg.Column(column_layout)
     , sg.VerticalSeparator(pad=((20, 5), (5, 5))), sg.Canvas(background_color='white', size=(100, 100), key='-sample-'),
     sg.Slider(range=(10, 50), enable_events=True, key='-slider-', default_value=25)],
    # 保存
    [sg.Button('分割して保存', key='-save-', button_color=('white', 'red'), disabled=True)],
    [sg.Button('保存', key='-stamp')]
]

frame_2 = [
    [sg.Image(data=None, key='IMAGE', enable_events=True, )],
    [sg.Button('前へ', key='-prev-', disabled=True), sg.Button('次へ', key='-next-', disabled=True), sg.Text('0 / 0', key='-page-', font=('Helvetica', 15))],
]

# PDFファイルをPIL Imageに変換
def pdf_to_pil_image(pdf_file, page_count):
    try:
        pdf = fitz.open(pdf_file)
        pdf_page = pdf[page_count]
        pix = pdf_page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    except Exception as e:
        sg.popup_error(f"PDFファイルの読み込みに失敗しました: {e}")
        return None

# PIL Imageをバイトデータに変換
def pil_image_to_bytes(img):
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

# ページ数を取得
def get_page_PDF(pdf_file):
    try:
        pdf = fitz.open(pdf_file)
        page_num = len(pdf)
        pdf.close()
        return page_num
    except Exception as e:
        sg.popup_error(f"PDFファイルのページ数取得に失敗しました: {e}")
        return 0

# 次のPDFページを表示
def get_next_page(pdf_file, page_num, page_count):
    if page_num > 0 and page_count < page_num - 1:
        page_count += 1
        img = pdf_to_pil_image(pdf_file, page_count)
        data = pil_image_to_bytes(img) if img else None
        return data, page_count, img
    else:
        img = pdf_to_pil_image(pdf_file, page_count)
        data = pil_image_to_bytes(img) if img else None
        return data, page_count, img

# 前のPDFページを表示
def get_prev_page(pdf_file, page_num, page_count):
    if page_count > 0:
        page_count -= 1
        img = pdf_to_pil_image(pdf_file, page_count)
        data = pil_image_to_bytes(img) if img else None
        return data, page_count, img
    else:
        img = pdf_to_pil_image(pdf_file, page_count)
        data = pil_image_to_bytes(img) if img else None
        return data, page_count, img

# ハンコを描画
def create_circle(canvas, radius=25):
    center_x = 50  # 円の中心のX座標
    center_y = 50  # 円の中心のY座標
    color = 'white'  # 円の色
    canvas.create_oval(center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        outline='red', width=2, tag='circle')

# ハンコの中の名前を描画
def embedded_name(canvas, name='名前', size=15):
    canvas.create_text(50, 50, text=stamp_set_name(name), fill='red', font=('Helvetica', size), tag='text')

# 名前の文字を縦にする
def stamp_set_name(name):
    var_name = ""
    for i in range(len(name)):
        if i != len(name) - 1:
            var_name += f'{name[i]}\n'
        else:
            var_name += f'{name[i]}'
    return var_name

# pdfを分割して保存
def pdf(input_path, output_path, sep=4):
    try:
        doc = fitz.open(input_path)  # open a document
        num_pages = len(doc)
        base_name = "split_page"
        for i in range(num_pages):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
            new_doc.save(f"{output_path}/{base_name}{i+1}.pdf")  # save the document
            new_doc.close()
        doc.close()
        sg.popup('分割完了', f'PDFファイルを {output_path} に分割保存しました。')
    except Exception as e:
        sg.popup_error(f"PDFファイルの分割に失敗しました: {e}")

# pdfファイルに捺印する
def stamp_pdf(loc_x, loc_y, input_path, output_pdf):
    try:
        doc = fitz.open(input_path)
        rect = (loc_x - 50, loc_y - 50, loc_x + 50, loc_y + 50)  # ハンコのサイズに合わせて調整
        img_bytes = open("ダウンロード.jpg", "rb").read()
        for page in doc:
            page.insert_image(rect, stream=img_bytes)
        output_file = f'{output_pdf}/stamped_{sg.user_settings_get_entry("-input-", "").split("/")[-1]}'
        doc.save(output_file)
        doc.close()
        sg.popup('捺印完了', f'PDFファイルに捺印し、{output_file} に保存しました。')
    except Exception as e:
        sg.popup_error(f"PDFファイルへの捺印に失敗しました: {e}")

def main():
    layout = [[sg.Frame('I/O', frame_1, size=(400, 800)), sg.Frame('preview', frame_2, size=(600, 800), expand_x=True, expand_y=True, element_justification='center')]]

    window = sg.Window('PDF分割ツール1.0.0', layout, size=(1000, 800), resizable=True, return_keyboard_events=True, )

    page_num = 0
    page_count = 0
    flag = False
    name = '名前'
    circle_text_init = True
    last_click_x = None
    last_click_y = None
    current_pil_image = None  # 現在表示しているPIL Imageを保存

    while True:
        event, values = window.read(timeout=100)
        canvas = window['-sample-'].tk_canvas

        if circle_text_init:
            create_circle(canvas)
            embedded_name(canvas)
            circle_text_init = False

        if event == sg.WIN_CLOSED:
            break

        # pdfファイルをビューに表示
        if event == '-input-':
            input_pdf_path = values['-input-']
            if input_pdf_path:
                current_pil_image = pdf_to_pil_image(input_pdf_path, page_count)
                data = pil_image_to_bytes(current_pil_image) if current_pil_image else None
                if data:
                    page_num = get_page_PDF(input_pdf_path)
                    window['IMAGE'].update(data=data)
                    window['-page-'].update(f'1 / {page_num}')
                    window['-prev-'].update(disabled=True)
                    window['-next-'].update(disabled=page_num <= 1)
                    window['-save-'].update(disabled=False)
                    flag = True
                    last_click_x = None
                    last_click_y = None
                else:
                    window['IMAGE'].update(data=None)
                    window['-page-'].update(f'0 / 0')
                    window['-prev-'].update(disabled=True)
                    window['-next-'].update(disabled=True)
                    window['-save-'].update(disabled=True)
                    flag = False
                    current_pil_image = None

        # ページをスクロール
        if event == '-next-' and flag:
            data, page_count, current_pil_image = get_next_page(values['-input-'], page_num, page_count)
            if data:
                window['IMAGE'].update(data=data)
                window['-page-'].update(f'{page_count + 1}/ {page_num}')
                window['-prev-'].update(disabled=False)
                window['-next-'].update(disabled=page_count == page_num - 1)
                last_click_x = None
                last_click_y = None

        if event == '-prev-' and flag:
            data, page_count, current_pil_image = get_prev_page(values['-input-'], page_num, page_count)
            if data:
                window['IMAGE'].update(data=data)
                window['-page-'].update(f'{page_count + 1}/ {page_num}')
                window['-next-'].update(disabled=False)
                window['-prev-'].update(disabled=page_count == 0)
                last_click_x = None
                last_click_y = None

        # pdfファイルに捺印し四つに分割し保存の処理
        if event == '-save-':
            input_path = values['-input-']
            output_path = values['-output-']
            if input_path and output_path:
                pdf(input_path, output_path)
            else:
                sg.popup_error("入力ファイルと出力先フォルダを選択してください。")

        # ハンコ生成
        if event == '-generate-':
            name = values['-name-']
            canvas.delete('circle')
            canvas.delete('text')
            create_circle(canvas)
            embedded_name(canvas, name)

        if event == '-slider-':
            canvas.delete('circle')
            create_circle(canvas, int(values['-slider-']))

        if event == '-text_size-':
            canvas.delete('text')
            embedded_name(canvas, name, int(values['-text_size-']))

        if event == 'IMAGE' and flag and current_pil_image:
            widget = window["IMAGE"].Widget
            x = widget.winfo_pointerx() - widget.winfo_rootx()
            y = widget.winfo_pointery() - widget.winfo_rooty()
            print(f"クリック座標: x={x}, y={y}")
            last_click_x = x
            last_click_y = y

            # PIL Imageに描画
            draw = ImageDraw.Draw(current_pil_image)
            marker_size = 10
            draw.ellipse((x - marker_size // 2, y - marker_size // 2, x + marker_size // 2, y + marker_size // 2), fill='red')

            # 描画後のImageをPySimpleGUIで表示
            data = pil_image_to_bytes(current_pil_image)
            window['IMAGE'].update(data=data)

        if event == '-stamp':
            input_path = values['-input-']
            output_path = values['-output-']
            if last_click_x is not None and last_click_y is not None and input_path and output_path:
                stamp_pdf(last_click_x, last_click_y, input_path, output_path)
                # 捺印後、プレビューを元の画像に戻す (必要であれば)
                current_pil_image = pdf_to_pil_image(input_path, page_count)
                data = pil_image_to_bytes(current_pil_image) if current_pil_image else None
                if data:
                    window['IMAGE'].update(data=data)
                last_click_x = None
                last_click_y = None
            elif not input_path or not output_path:
                sg.popup_error("入力ファイルと出力先フォルダを選択してください。")
            else:
                sg.popup_error("プレビュー画像をクリックして捺印位置を設定してください。")

        if event and not flag and event not in ('-input-'):
            continue

    window.close()

if __name__ == "__main__":
    main()