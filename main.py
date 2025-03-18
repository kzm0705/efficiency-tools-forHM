import PySimpleGUI as sg
import pypdf
import fitz
import PIL
import tkinter as tk

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
    print(pix)
    data = pix.tobytes()
    # width = pix.width
    # height = pix.height
    # print(width,height)
    pdf.close()
    return data

#ページ数を取得
def get_page_PDF(pdf_file):
    pdf = fitz.open(pdf_file)
    page_num = len(pdf)
    pdf.close()
    return page_num


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
def pdf(input_path, output_path, sep=4):
    for i in range(sep):
        doc = fitz.open(input_path) # open a document
        doc.select([i])
        doc.save(f"{output_path}/test-page-copied{i}.pdf") # save the document
        doc.close()
    # pix = selected_pdf.get_pixmap()
    # data = pix.tobytes()
    # return data


def main():
    
    layout = [[sg.Frame('I/O',frame_1,size=(400,800)),sg.Frame('preview', frame_2,size=(600,800), expand_x=True, expand_y=True, element_justification='center')]]
    
    window = sg.Window('PDF分割ツール1.0.0', layout, size=(1000,800), resizable=True, return_keyboard_events=True,)

    page_num = 0
    page_count = 0
    flag = False
    name = '名前'
    circle_text_init = True

    while True:
        event, values = window.read(timeout=100)
        canvas = window['-sample-'].tk_canvas

        if circle_text_init:
            create_circle(canvas)
            embedded_name(canvas)
            circle_text_init = False

        if event == sg.WIN_CLOSED:
            break

        #pdfファイルをビューに表示
        if event =='-input-':
            data = pdf_to_image(values['-input-'], page_count)
            page_num = get_page_PDF(values['-input-'])
            window['IMAGE'].update(data=data)

            window['-page-'].update(f'1 / {page_num}')
            window['前へ'].update(disabled=False)
            window['次へ'].update(disabled=False)
            window['-save-'].update(disabled=False)
            flag = True

        #ページをスクロール
        if event in ('次へ', "MouseWheel:Down") and flag:
            data, page_count = get_next_page(values['-input-'], page_num, page_count)
            # print(page_count)
            window['IMAGE'].update(data=data)
            window['-page-'].update(f'{page_count+1}/ {page_num}')

        if event in ('前へ', 'MouseWheel:Up') and flag:
            data, page_count = get_prev_page(values['-input-'], page_num, page_count)
            # print(page_count)
            window['IMAGE'].update(data=data)
            window['-page-'].update(f'{page_count+1}/ {page_num}')

        #pdfファイルに捺印し四つに分割し保存の処理
        if event == '-save-':
            data = pdf(values['-input-'], values['-output-'])

        #ハンコ生成
        if event == '-generate-':
            name = values['-name-']
            canvas.delete('circle')
            canvas.delete('text')
            create_circle(canvas)
            embedded_name(canvas, name)
        
        if event == '-slider-':
            canvas.delete('circle')
            create_circle(canvas, int(values['-slider-']))

        if event == '-text_size-' :
            canvas.delete('text')
            embedded_name(canvas, name, int(values['-text_size-']))
        
        if event == 'IMAGE' and flag:
            widget = window["IMAGE"].Widget
            x = widget.winfo_pointerx() - widget.winfo_rootx()
            y = widget.winfo_pointery() - widget.winfo_rooty()
            print(x,y)



        if event and not flag:
             continue


    window.close()

if __name__ == "__main__":
    main()