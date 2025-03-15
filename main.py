import PySimpleGUI as sg
import pypdf
import fitz
theme = sg.theme('DarkBlack1')

frame_1= [[sg.Text('入力ファイル: ')],
          [sg.Input(size=(45,1), key='-input-', enable_events=True),sg.FileBrowse(file_types=(('PDFファイル','*.pdf'),))],
          [sg.Text('出力先フォルダ:', pad=((0,0),(20,5)))],
          [sg.Input(size=(45,1), key='output'),sg.FolderBrowse()]
          ]

frame_2 = [[sg.Image(data=None, key='IMAGE',expand_x=True,expand_y=True)],
           [sg.Button('前へ',disabled=True), sg.Button('次へ',disabled=True), sg.Text('0 / 0',key='-page-',font=('Helvetica',15))],
           ]

#PDFファイルを画像に変換
def pdf_to_image(pdf_file, page_count):
    pdf = fitz.open(pdf_file)
    pdf_page = pdf[page_count]
    pix = pdf_page.get_pixmap()
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



def main():
    
    layout = [[sg.Frame('I/O',frame_1,size=(400,800)),sg.Frame('preview',frame_2,size=(600,800),expand_x=True,expand_y=True,element_justification='center')]]
    
    window = sg.Window('PDF分割ツール', layout, size=(1000,800), resizable=True, return_keyboard_events=True,)

    page_num = 0
    page_count = 0

    while True:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED:
            break

        if event and not values['-input-']:
            continue

        #pdfファイルをビューに表示
        if event =='-input-':
            data = pdf_to_image(values['-input-'], page_count)
            page_num = get_page_PDF(values['-input-'])
            window['IMAGE'].update(data=data)
            window['-page-'].update(f'1 / {page_num}')
            window['前へ'].update(disabled=False)
            window['次へ'].update(disabled=False)

        #ページをスクロール
        if event in ('次へ', "MouseWheel:Down"):
            data, page_count = get_next_page(values['-input-'], page_num, page_count)
            # print(page_count)
            window['IMAGE'].update(data=data)
            window['-page-'].update(f'{page_count+1}/ {page_num}')

        if event in ('前へ', 'MouseWheel:Up'):
            data, page_count = get_prev_page(values['-input-'], page_num, page_count)
            # print(page_count)
            window['IMAGE'].update(data=data)
            window['-page-'].update(f'{page_count+1}/ {page_num}')







    window.close()


if __name__ == "__main__":
    main()