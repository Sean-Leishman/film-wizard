import tkinter as tk
from tkinter import *
import chatbot_class as cs


root=tk.Tk()
root.title(f"Chat Bot")
root.geometry('500x400')
text_contents = dict()

extracted_keywords = []
chatbot_frame = cs.MovieRecommender(extracted_keywords = extracted_keywords)

def widget_get():
    text_widget = root.nametowidget(textcon)
    return text_widget.get('1.0','end-1c')

def clear(event=None):
    textcon.delete('2.0', 'end-1c')
    content = widget_get()
    text_contents[str(textcon)] = hash(content)

def send(event=None):
    usr_input = message.get()
    usr_input = usr_input.lower()

    textcon.insert(END, f'User: {usr_input}'+'\n','usr')

    responses = chatbot_frame.get_input_respond_message_for_movie_recommender(usr_input)

    for response in responses:
        if isinstance(response, str):
            #If it's a string
            textcon.config(fg='yellow')
            textcon.insert(END, "BOT: " + response + "\n")
        else:
            #If it detects a method called
            result = response()
            textcon.config(fg='yellow')
            textcon.insert(END, "BOT: " + result + "\n")

root.resizable(False, False)
main_menu=Menu(root)
edit_menu=Menu(root)
edit_menu.add_command(label='Clear  <Delete>',command=clear)
main_menu.add_cascade(label="Edit",menu=edit_menu)
main_menu.add_command(label="Quit",command=root.destroy)
root.config(menu=main_menu)
message=tk.StringVar()
chat_win=Frame(root,bd=1,bg='black',width=50,height=8)
chat_win.place(x=6,y=6,height=300,width=480)
textcon=tk.Text(chat_win,bd=1,bg='black',width=50,height=8)
textcon.pack(fill="both",expand=True)
mes_win=Entry(root,width=30,xscrollcommand=True,textvariable=message)
mes_win.place(x=6,y=310,height=60,width=366)
mes_win.focus()
textcon.config(fg='yellow')
textcon.tag_config('usr',foreground='white')
textcon.insert(END,"Bot: This is your chat bot to assist you about Machine Learning!\n\n")
mssg=mes_win.get()
button=Button(root,text='Send',bg='yellow',activebackground='orange',command=send,width=12,height=5,font=('Arial'))
button.place(x=376,y=310,height=60,width=110)
scrollbar=tk.Scrollbar(textcon)
scrollbar.pack(fill='y')
scrollbar.place(relheight = 1,relx = 1)
scrollbar.config(command = textcon.yview)
content = widget_get()
text_contents[str(textcon)] = hash(content)
root.bind('<Delete>', clear,edit_menu)
root.mainloop()