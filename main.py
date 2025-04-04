import PySimpleGUI as sg
import fitz
from PIL import Image, ImageGrab, ImageDraw
import os
import shutil

theme = sg.theme('DarkBlack1')

column_layout = [
                 [sg.Input(size=(10,2), key='-name-'), sg.Button('ハンコ生成', key='-generate-', button_color=('white','green'),enable_events=True,)],
                 [sg.Slider(range=(5,25), default_value=15, orientation="h",enable_events=True, key='-text_size-')]
                 ]

frame_1= [
          [sg.Text('入力ファイル: ')],
          [sg.Input(size=(45,1), key='-input-', enable_events=True),sg.FileBrowse(file_types=(('PDFファイル','*.pdf'),))],
          #出力ファイル
          [sg.Text('出力先フォルダ:', pad=((0,0),(20,5)))],
          [sg.Input(size=(45,1), key='-output-'),sg.FolderBrowse()],
          #ハンコ
          [sg.Text('捺印する名前を入力してください(最大で四文字まで):',pad=((0,0),(20,5)))],
          [sg.Column(column_layout)
           ,sg.VerticalSeparator(pad=((20,5),(5,5))),sg.Canvas(background_color='white', size=(100,100), key='-sample-'),
           sg.Slider(range=(10,50),enable_events=True, key='-slider-',default_value=25)],
           #保存
          [sg.Button('分割して保存',key='-save-', button_color=('white','red'), disabled=True)],
          [sg.Text('・PDF全体が表示されるようにウィンドウを拡げてください。\n捺印する際の座標がずれる可能性があります',text_color='red', key='-warning-')],
          [sg.Text('ページをスクロールすると捺印が取り消されるので\nもう一度捺印してください。', text_color='yellow')]
          ]

frame_2 = [
           [sg.Image(data=None, key='IMAGE',enable_events=True, )],
           [sg.Button('前へ',disabled=True), sg.Button('次へ',disabled=True), sg.Text('0 / 0',key='-page-',font=('Helvetica',15))],
           ]

#PDFファイルを画像に変換
def pdf_to_image(pdf_file, page_count):
    pdf = fitz.open(pdf_file)
    pdf_page = pdf[page_count]
    pix = pdf_page.get_pixmap()
    # print(pix)
    data = pix.tobytes()
    pdf.close()
    return data

#ページ数を取得
def get_page_PDF(pdf_file):
    pdf = fitz.open(pdf_file)
    page_num = len(pdf)
    pdf.close()
    return page_num

#pdfサイズを取得
def get_size_pdf(pdf_file):
    pdf = fitz.open(pdf_file)
    pdf_page = pdf[0]
    pix = pdf_page.get_pixmap()
    x = pix.width
    y = pix.height
    return x,y


#次のPDFページを表示
def get_next_page(pdf_file, page_num, page_count):
    if page_num -1 > page_count:
        page_count += 1
        data = pdf_to_image(pdf_file, page_count)
        return data, page_count
    else:
        page_count = 0
        data = pdf_to_image(pdf_file, page_count)
        return data, page_count


#前のPDFページを表示
def get_prev_page(pdf_file, page_num, page_count):
    if  page_count > 0:
        page_count -= 1
        data = pdf_to_image(pdf_file, page_count)
        return data, page_count
    else:
        page_count = page_num -1
        data = pdf_to_image(pdf_file, page_count)
        return data, page_count

#ハンコを描画
def create_circle(canvas,radius=25):

    center_x = 50  # 円の中心のX座標
    center_y = 50  # 円の中心のY座標
    color = 'white'  # 円の色
    canvas.create_oval(center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        outline='red',width=2, tag='circle')
#ハンコの中の名前を描画
def embedded_name(canvas, name='名前', size=15):
    canvas.create_text(50,50, text=stamp_set_name(name), fill='red', font=('Helvetica', size), tag='text')

#名前の文字を縦にする
def stamp_set_name(name):
    var_name = ""
    for i in range(len(name)):
        if i != len(name) -1 :
            var_name += f'{name[i]}\n'
        else: var_name += f'{name[i]}'
    return var_name

#pdfを分割して保存
def four_split_pdf(input_path, output_path, sep=4):
    for i in range(sep):
        doc = fitz.open(input_path)
        doc.select([i])
        doc.save(f"{output_path}/test-page-copied{i}.pdf") 
        doc.close()

#pdfファイルに捺印する
def stamp_in_viewer(loc_x,loc_y,input_path, page_count, radius):
    doc = fitz.open(input_path)
    rect = (loc_x - radius ,loc_y - radius,loc_x + radius, loc_y + radius)
    img = open("temp/test.png", "rb").read()
    for i,page in enumerate(doc):
        if i == page_count:
            page.insert_image(rect, stream=img)
            doc.save(f'temp/test.pdf')
        else:pass
    return 'temp/test.pdf'


#(仮)はんこの画像を作る
def create_stamp_png(canvas,canvas_widget, circle_radius):
    #画面上のcanvasの絶対位置
    abs_x = canvas_widget.winfo_rootx()
    abs_y = canvas_widget.winfo_rooty()

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


def embed_a_stamp_on_viewer(x, y, page_num, stamp_path:str, pdf_file:str):
    data = pdf_to_image(pdf_file, page_num)
    im1 = Image.open(data)
    im2 = Image.open(stamp_path)

    back_im = im1.copy()
    back_im.paste(im2, (x, y))
    back_im.save('temp/test0.png', quality=95)

    return 'temp/test0.png'

def check_input_file(input_file):
    file_name = os.path.basename(input_file)
    if file_name[:5] == '注文書一式':
        return True
    else: return False

def create_temp_folder():
    if not os.path.isdir('temp'):
        os.mkdir('temp')
    else: pass

def main():

    layout = [[sg.Frame('I/O',frame_1,size=(400,2000)),sg.Frame('preview', frame_2,size=(600,800), expand_x=True, expand_y=True, element_justification='center', key='-frame2-')]]

    window = sg.Window('PDF分割ツール1.0.0', layout, size=(1000,800), resizable=True, return_keyboard_events=True,)

    page_num = 0
    page_count = 0
    flag = False
    name = '名前'
    circle_text_init = True
    stamp_flag = False

    create_temp_folder()

    while True:
        event, values = window.read(timeout=100)
        canvas = window['-sample-'].tk_canvas
        root = window.TKroot
        frame_2_width, frame_2_height = window['-frame2-'].get_size()

        if circle_text_init:
            create_circle(canvas)
            embedded_name(canvas)
            circle_text_init = False

        if event == sg.WIN_CLOSED:
            break

        #pdfファイルをビューに表示
        if event =='-input-':
            input_path = values['-input-']
            if check_input_file(input_path):
                data = pdf_to_image(input_path, page_count)
                page_num = get_page_PDF(input_path)
                pdf_width, pdf_height = get_size_pdf(input_path)
                window['IMAGE'].update(data=data)

                window['-page-'].update(f'1 / {page_num}')
                window['前へ'].update(disabled=False)
                window['次へ'].update(disabled=False)
                flag = True
            else:sg.popup('入力されたファイルに問題があります。"注文書一式"からはじまるPDFファイルを選択してください')

        #ページをスクロール
        if event in ('次へ', "MouseWheel:Down") and flag:
            data, page_count = get_next_page(values['-input-'], page_num, page_count)
            window['IMAGE'].update(data=data)
            window['-page-'].update(f'{page_count+1}/ {page_num}')

        if event in ('前へ', 'MouseWheel:Up') and flag:
            data, page_count = get_prev_page(values['-input-'], page_num, page_count)
            window['IMAGE'].update(data=data)
            window['-page-'].update(f'{page_count+1}/ {page_num}')

        #pdfファイルに捺印し四つに分割し保存の処理
        if event == '-save-':
                if values['-output-']:
                    data = four_split_pdf('temp/test.pdf', values['-output-'])

                else:sg.popup('出力先のフォルダを選択してください')

        #ハンコ生成
        if event == '-generate-':
            name = values['-name-']
            name_size = int(values['-text_size-'])
            canvas.delete('circle')
            canvas.delete('text')
            create_circle(canvas, int(values['-slider-']))
            embedded_name(canvas, name if name != "" else '名前', name_size)
            circle_radius = values['-slider-'] + 1
            canvas_widget = window['-sample-'].Widget
            canvas.update()
            create_stamp_png(canvas, canvas_widget, circle_radius)
            stamp_flag = True

        if event == '-slider-':
            canvas.delete('circle')
            create_circle(canvas, int(values['-slider-']))

        if event == '-text_size-' :
            canvas.delete('text')
            embedded_name(canvas, name if name != "" else '名前', int(values['-text_size-']))

        if event == 'IMAGE' and flag:
            if stamp_flag:
                widget = window["IMAGE"].Widget
                x = widget.winfo_pointerx() - widget.winfo_rootx()
                y = widget.winfo_pointery() - widget.winfo_rooty()
                path = values['-input-']
                radius = int(values['-slider-'])
                viewer_path = stamp_in_viewer(x, y, path, page_count, radius)
                data = pdf_to_image(viewer_path, page_count)
                page_num = get_page_PDF(viewer_path)

                window['IMAGE'].update(data)
            else:
                sg.popup('先にハンコを作成してください')

        if flag and frame_2_width > pdf_width and frame_2_height > pdf_height:
            window['-warning-'].update(text_color='green')
            window['-save-'].update(disabled=False)

        else:
            window['-warning-'].update(text_color='red')
            window['-save-'].update(disabled=True)

        if event and not flag:
             continue

    #一時ファイル削除
    shutil.rmtree('temp')

    window.close()

if __name__ == "__main__":
    main()
