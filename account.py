import tkinter as tk


class Account(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.build()


    def build(self):
        self.title('New Account')
        self.geometry('400x300')

        #rajouter toutes les entrées nécessaires afin de sauvegarder la personne dans le domaine et lier le docteur à la personne

        self.mainloop() 


