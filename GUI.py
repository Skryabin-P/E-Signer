from  tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk
from func import run
import threading
import os

class App():
    def __init__(self):
        root = Tk()
        root.title("Подписание документов")
        root.iconbitmap('icon.ico')
        root.resizable(width=False,height=False)
        self.frame = Frame(root, padding="100 100 100 100",borderwidth=5)
        image = Image.open('coral.png')
        photo = ImageTk.PhotoImage(image)
        label = Label(self.frame, image=photo)
        label.grid(column=0,row=0)
        self.frame.grid(column=0,row=0, sticky="N W E S")
        self.checked = BooleanVar()
        root.columnconfigure(0, weight = 1)
        root.rowconfigure(0, weight = 1)
        header = Label(self.frame, text="Электронное подписание документов", font="Time 20", foreground='#383838')
        header.grid(column=1,row=0, sticky="W E")

        header = Label(self.frame, text="", font="Time 20", foreground='#383838')
        header.grid(column=1, row=1, sticky="W E")

        label1 = Label(self.frame, text="Выберете папку с файлами для подписания", font="Time 15")
        label1.grid(column=1, row=2, sticky="W E")

        browse1 = Button(self.frame, text='Выбрать', command=self.open_pdf_folder)
        browse1.grid(column=2, row=2, sticky="W E")

        label2 = Label(self.frame, text="Выберете папку с сертификатами", font="Time 15")
        label2.grid(column=1, row=3, sticky="W E")

        browse2 = Button(self.frame, text='Выбрать', command=self.open_cert_path)
        browse2.grid(column=2, row=3, sticky="W E")

        label3 = Label(self.frame, text="Выберете папку для сохранения подписанных файлов", font="Time 15")
        label3.grid(column=1, row=4, sticky="W E")

        browse3 = Button(self.frame, text='Выбрать', command=self.save_path)
        browse3.grid(column=2, row=4, sticky="W E")

        sign_all_button = Checkbutton(self.frame, text='Подписать все страницы в каждом документе', onvalue=True, offvalue=False, variable=self.checked)
        sign_all_button.grid(column=1, row=5)

        sign_button = Button(self.frame, text='Подписать', command=self.do_stuff)
        sign_button.grid(column=1, row=6, sticky="W E")


        root.mainloop()


    def open_pdf_folder(self):
        self.pdfpath = askdirectory()

    def open_cert_path(self):
        self.certpath = askdirectory()


    def save_path(self):
        self.savepath = askdirectory()

    def do_stuff(self):
        # threading signing process so Tkinter do not freeze
        threading.Thread(target=self.sign).start()

    def sign(self):
        pb = Progressbar(self.frame, orient=HORIZONTAL, length=300, mode='determinate')
        pb.grid(column=1, row=7)
        pb_label = Label(self.frame,text='0%')
        pb_label.grid(column=2,row=7)
        self.frame.update_idletasks()
        files = os.listdir(self.pdfpath)
        certs = os.listdir(self.certpath)
        self.cert_path = []
        step = 100 /len(files)

        for cert in certs:
            self.cert_path.append(os.path.abspath(f"{self.certpath}/{cert}"))

        for file in files:
            self.file_path = os.path.abspath(f"{self.pdfpath}/{file}")
            self.file_path_output = os.path.abspath(f"{self.savepath}/{file}")
            run(self.cert_path, '123', self.file_path, self.file_path_output, self.checked.get())
            pb['value'] += step
            pb_label['text'] = f"{round(pb['value'],1)}%"
            self.frame.update_idletasks()

        finished = Label(self.frame, text="Готово! Ваши файлы подписаны!", background='black', foreground='red', font='Times 14')
        finished.grid(column=1, row=8)




if __name__ == '__main__':
    App()










