# -*- coding: utf-8 -*-
"""
Created on Sun May 17 21:38:40 2020

@author: User
"""


import sys
import pygame
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

# class main_window():
    
#     def __init__(self):
#         super(main_window, self).__init__()
#         self.init_ui()

#     def init_ui(self):
#         self.setWindowTitle('Hello world')
#         self.resize(400, 400)
#         my_button =  QPushButton('Push Me', self)
#         self.show()


def main():
   #  app = QApplication(sys.argv)
   # # app_window = main_window()
   #  win = QMainWindow()
   #  win.setGeometry(200, 200, 300, 300)
   #  win.setWindowTitle('Hello world')
   #  win.show()
   #  sys.exit(app.exec_())
   pygame.init() 
   screen = pygame.display.set_mode((800, 600))
   running = True
   while running:
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False

if __name__ == '__main__':
    main()
