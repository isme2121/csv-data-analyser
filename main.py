import customtkinter
from read_excel import *
from tkinter import ttk, PhotoImage
from __settings__ import *
from paths import *
from datetime import datetime
from knn_class import *
from PIL import Image
import time
import threading
'''
this program was integrated in an embedded format, most methods are hardly usable outside of it's proper environment
progress: 60%
to do list:
>>> add help message to knn, regression
>>> add column scalling

questions:
difference between create_tree and reanimate?
>>>idfk
difference between modified parametre flag and updateflag?
>>>idfk
'''
themes = os.listdir('themes')
a = customtkinter.ThemeManager()
customtkinter.set_appearance_mode(appearance_color[curr_appearance_mode])
class app(customtkinter.CTk, read_data, modify_data, directory, knn_create):
    Load_name : str = '' #name of the loaded file
    save_name : str = '' #name of the saved file
    memo : list = [] #used to store previous commands in commands prompt window, cleared automatically
    memo_index : int = 0 #used with memo to retrieve commands
    updateflag : bool = False #data saving flag, set to true to save data in the app
    exitflag : bool = True #data table's exit flag, set to True if the window is closed
    exitflag2 : bool = True #save confirmation window's exit flag, set to True if the window is closed
    exitflagML : bool = True #data configuration window's exit flag, set to True if the window is closed
    learningmode : str = 'knn' #set to algorithm in configuration frame, can be changed dynamically
    readvalue : str = 'single' #set to algorithm of input reading, can be changed dynamically
    parametres : dict[bool]= {
        'Data_available': False, #set to True if the data has successfully loaded
        'table_available': False, #set to True if the data table is not closed
        'modified': False, #set to True if a modification occurred in the data table
        'extend_1': False, #set to true if the extend button in main menu is clicked
        'cmd_window': False, #set to true if command prompt is not closed
        'default_color': 1 #default widget colors, set to 0 and 1
    } #parametres work with UI methods and disabling functions when necessary
    settings = {
        'Logs_file': '_LOGS.txt', #file that contains all logs messages, cleared automatically
        'enable_time': True, #displays time in command prompt if set to True, can be cleared dynamically
        'Load_from' : 'xlsx', #file type of the loaded file, used in load method
        'Save_to' : 'xlsx',  #file type of saved file, used in save method
        'mode': 'write', #allows data modifications if set to write, else set to read mode
    } #settings that can be changed in command prompt
    def __init__(self) -> None:
        #initializing inherited classes
        super().__init__()
        read_data.__init__(self, self.Load_name + f'.{self.settings['Load_from']}')
        directory.__init__(self)
        knn_create.__init__(self,title='data',n=5)
        image = Image.open('images//bg.jpg')
        bg = customtkinter.CTkImage(image, image,(520,600))
        bg_image = customtkinter.CTkLabel(self, image=bg, text='')
        # self.after(250, lambda : self.iconbitmap(default='icon1.ico'))
        # self.iconify()
        # self.after(250, lambda : self.deiconify())
        # icon = PhotoImage(file='icon.png')
        self.iconbitmap(default='images//icon1.ico')
        self.title("Data Analyser") #title
        self.geometry(f"{240}x{520}") #setting size
        self.resizable(0,0) #blocking the resizing of the screen
        bg_image.place(x=0, y=0)
        self.main_widget() #launching main widget
        self.configuration_frame() #launching configuration widget
        self.help_update('default')
        open(f'LOGS//{self.settings.get('Logs_file')}', 'a').close() #creates logs file if it's not found
    
    #create widgets
    def main_widget(self) -> None:
        """
        main frame setup
        """
        #buttons frame
        self.main_frame = customtkinter.CTkScrollableFrame(self,  border_width=1, width=200, height=470)
        self.main_frame.grid(row=0, column=0, padx=(10,0), pady=(20,25),sticky='nw')
        
        #opening command prompt button
        self.m_button1 = customtkinter.CTkButton(self.main_frame,width=120,height=20,text='Command Window',corner_radius=0, border_width=1,command=self.command_window)
        self.m_button1.grid(row=0,column=0, padx=(40,0),pady=10)
        #extending the screen button
        self.m_button2 = customtkinter.CTkButton(self.main_frame,width=120,height=20,text='expand',corner_radius=0, border_width=1)
        self.m_button2.grid(row=1,column=0, padx=(40,0),pady=10)
        #loaded file label
        self.m_text = customtkinter.CTkLabel(self.main_frame,font=('Courier', 10,'bold'),text=f'loaded file: {self.Load_name}',)
        self.m_text.grid(row=2,column=0, padx=(0,0),pady=(10,0),sticky='w')
        #loading data button
        self.m_button3 = customtkinter.CTkButton(self.main_frame,width=120,height=20,text='Load Data',corner_radius=0, border_width=1,command=self.show_data_table)
        self.m_button3.grid(row=3,column=0, padx=(40,0), pady=(0,10),)
        #launching empty table button
        self.m_button4 = customtkinter.CTkButton(self.main_frame,width=120,height=20,text='Load empty table',corner_radius=0, border_width=1,command=self.empty_table)
        self.m_button4.grid(row=4,column=0, padx=(40,0), pady=(0,10),)
        self.m_button1.bind('<Double-3>',lambda event : self.help_update(event = 'cmd_button'))
        self.m_button2.bind('<Double-3>',lambda event : self.help_update(event = 'maximize_button'))
        self.m_button3.bind('<Double-3>',lambda event : self.help_update(event = 'load_button'))
        self.m_button4.bind('<Double-3>',lambda event : self.help_update(event = 'empty_button'))

    def configuration_frame(self)->None:
        """
        creates configuration widget and the help textbox widget in the main screen
        """
        #textbox frame
        self.config_text_frame = customtkinter.CTkFrame(self,width=240,height=200)
        self.config_text_frame.grid(row=0,column=1,sticky='n',padx=(5,10), pady=(20,0))
        #help textbox
        self.config_help_box = customtkinter.CTkTextbox(self.config_text_frame,width=260,height=150,border_width=1,corner_radius=10,)
        self.config_help_box.grid(row=0,column=0)
        #configuration frame
        self.config_frame = customtkinter.CTkScrollableFrame(self, width=240, height=310, border_width=1)
        self.config_frame.grid(row=0,column=1, sticky='sw',padx=(5,10),pady=(0,26))
        #Value box entry value
        self.entry_text = customtkinter.StringVar()
        #not used yet
        self.var = customtkinter.IntVar()
        #modify text label
        self.text1 = customtkinter.CTkLabel(self.config_frame,width=100,height=20,text='modify',font=('Courier', 12, 'bold'),anchor='w',)
        #first row
        self.row05 = customtkinter.CTkTextbox(self.config_frame,width=120,height=20,corner_radius=0, border_width=1)
        self.column05 = customtkinter.CTkComboBox(self.config_frame,width=120,height=26,corner_radius=0, border_width=1,values=['single','multiple'], command=lambda val : self.set_read_config(val))
        #second row
        self.row1 = customtkinter.CTkTextbox(self.config_frame,width=120,height=20,corner_radius=0, border_width=1)
        self.column1 = customtkinter.CTkTextbox(self.config_frame,width=120,height=20,corner_radius=0, border_width=1)
        #third row
        self.row2 = customtkinter.CTkTextbox(self.config_frame, width=120,height=20,corner_radius=0, border_width=1)
        self.column2 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,corner_radius=0, border_width=1)
        #fourth row
        self.row3 = customtkinter.CTkTextbox(self.config_frame, width=120,height=20,corner_radius=0, border_width=1)
        self.column3 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,corner_radius=0, border_width=1)
        #fifth row
        self.row4 = customtkinter.CTkTextbox(self.config_frame, width=120,height=20,corner_radius=0, border_width=1)
        self.column4 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,placeholder_text='input',corner_radius=0, border_width=1,textvariable=self.entry_text)
        #add/remove text label
        self.text2 = customtkinter.CTkLabel(self.config_frame,width=100,height=20,text='add/remove',font=('Courier', 12, 'bold'),anchor='w',)
        #sixth row
        self.row5 = customtkinter.CTkButton(self.config_frame, width=120,height=26,text='add row',corner_radius=0, border_width=1,anchor='w',command=self.addrow)
        self.column5 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,placeholder_text='1',corner_radius=0, border_width=1)
        #seventh row
        self.row6 = customtkinter.CTkButton(self.config_frame, width=120,height=26,text='add column',corner_radius=0, border_width=1,anchor='w',command=self.addcolumn)
        self.column6 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,placeholder_text='new column\'s name',corner_radius=0, border_width=1)
        #eighth row
        self.row7 = customtkinter.CTkButton(self.config_frame, width=120,height=26,text='remove row',corner_radius=0, border_width=1,anchor='w',command=self.removerow)
        self.column7 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,corner_radius=0, border_width=1)
        #ninth row
        self.row8 = customtkinter.CTkButton(self.config_frame, width=120,height=26,text='remove column',corner_radius=0, border_width=1,anchor='w',command=self.removecolumn)
        self.column8 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,corner_radius=0, border_width=1)
       
        #column scale text label
        self.text3 = customtkinter.CTkLabel(self.config_frame,width=100,height=20,text='column scale',font=('Courier', 12, 'bold'),anchor='w',)
        self.row9 = customtkinter.CTkTextbox(self.config_frame, width=120,height=20,corner_radius=0, border_width=1)
        self.column9 = customtkinter.CTkCheckBox(self.config_frame, text='false', corner_radius=0, border_width=1, command=self.set_scale_config, onvalue=True, offvalue=False, variable=self.var)

        self.row85 = customtkinter.CTkButton(self.config_frame, width=120,height=26,text='replace column',corner_radius=0, border_width=1,anchor='w',command=self.replace_column)
        self.column85 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,placeholder_text='old->new',corner_radius=0, border_width=1)

        self.row95 = customtkinter.CTkButton(self.config_frame, width=120,height=26,text='replace value',corner_radius=0, border_width=1,anchor='w',command=self.replace_value)
        self.column95 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,placeholder_text='key:index:old:new',corner_radius=0, border_width=1)
        #tenth row
        self.row10 = customtkinter.CTkTextbox(self.config_frame, width=120,height=20,corner_radius=0, border_width=1)
        self.column10 = customtkinter.CTkEntry(self.config_frame, width=120,height=26,placeholder_text='input',corner_radius=0, border_width=1) #get columns
        #plot text label
        self.text4 = customtkinter.CTkLabel(self.config_frame,width=100,height=20,text='plot',font=('Courier', 12, 'bold'),anchor='w',)
        #eleventh row
        self.row11 = customtkinter.CTkButton(self.config_frame, width=120,height=26,text='configure',corner_radius=0, border_width=1,anchor='w',command=self.plot_configure)
        self.column11 = customtkinter.CTkComboBox(self.config_frame,width=120,height=26,corner_radius=0, border_width=1,values=['knn','regression'], command=lambda mode : self.set_plot(mode))

        self.config_help_box.bind('<Double-3>',lambda event : self.help_update(event='default'))
        self.column05.bind('<Double-3>',lambda event : self.help_update(event='read_mode'))
        self.column2.bind('<Double-3>',lambda event : self.help_update(event='select_row'))
        self.column3.bind('<Double-3>',lambda event : self.help_update(event='select_column'))
        self.column4.bind('<Double-3>',lambda event : self.help_update(event='value'))
        self.column5.bind('<Double-3>',lambda event : self.help_update(event='add_row'))
        self.column6.bind('<Double-3>',lambda event : self.help_update(event='add_column'))
        self.column7.bind('<Double-3>',lambda event : self.help_update(event='remove_row'))
        self.column8.bind('<Double-3>',lambda event : self.help_update(event='remove_column'))
        self.column85.bind('<Double-3>',lambda event : self.help_update(event='replace_column'))
        self.column9.bind('<Double-3>',lambda event : self.help_update(event='soon'))
        self.column95.bind('<Double-3>',lambda event : self.help_update(event='replace_value'))
        self.column10.bind('<Double-3>',lambda event : self.help_update(event='soon'))
        self.column11.bind('<Double-3>',lambda event : self.help_update(event='ML'))
        #placing rows
        self.text1.grid(row=0,column=0,sticky='w',padx=(5,0))
        self.row1.grid(row=1,column=0,sticky='n')
        self.column1.grid(row=1,column=1,sticky='n')
        self.row05.grid(row=2,column=0,sticky='n')
        self.column05.grid(row=2,column=1,sticky='n')
        self.row2.grid(row=3,column=0,sticky='n')
        self.column2.grid(row=3,column=1,sticky='n')
        self.row3.grid(row=4,column=0,sticky='n')
        self.column3.grid(row=4,column=1,sticky='n')
        self.row4.grid(row=5,column=0,sticky='n')
        self.column4.grid(row=5,column=1,sticky='n')
        self.text2.grid(row=6,column=0,sticky='w',padx=(5,0))
        self.row5.grid(row=7,column=0,sticky='n')
        self.column5.grid(row=7,column=1,sticky='n')
        self.row6.grid(row=8,column=0,sticky='n')
        self.column6.grid(row=8,column=1,sticky='n')
        self.row7.grid(row=9,column=0,sticky='n')
        self.column7.grid(row=9,column=1,sticky='n')
        self.row8.grid(row=10,column=0,sticky='n')
        self.column8.grid(row=10,column=1,sticky='n')
        self.text3.grid(row=11,column=0,sticky='w',padx=(5,0))
        self.row9.grid(row=12,column=0,sticky='n')
        self.column9.grid(row=12,column=1,sticky='n')
        self.row85.grid(row=13,column=0,sticky='n')
        self.column85.grid(row=13,column=1,sticky='n')
        self.row95.grid(row=14,column=0,sticky='n')
        self.column95.grid(row=14,column=1,sticky='n')
        self.row10.grid(row=15,column=0,sticky='n')
        self.column10.grid(row=15,column=1,sticky='n')
        self.text4.grid(row=16,column=0,sticky='w',padx=(5,0))
        self.row11.grid(row=17,column=0,sticky='n')
        self.column11.grid(row=17,column=1,sticky='n')
        self.set_conf_values()
        self.replace_placeholder()
        self.UI_update_all()

    def plot_configure(self)->None:
        """
        configure button's method (row11), creates a new window with widgets based on learningmode
        """
        #to prevent creating more than one window
        if not self.exitflagML:
            self.quit_ML()
        #dropping ML window's exit flag as creating it
        self.exitflagML = False
        #main window
        self.configure_ML = customtkinter.CTkToplevel(self)
        self.configure_ML.protocol("WM_DELETE_WINDOW", self.quit_ML)
        self.configure_ML.title('configurations')
        self.configure_ML.resizable(0,0)
        self.configure_ML.attributes('-topmost', 'true')

        #creating widgets based on learningmode variable
        match self.learningmode:
            case 'knn':
                self.configure_ML.geometry(f'{550}x{380}')
                #frames
                self.frame_ML = customtkinter.CTkFrame(self.configure_ML,border_width=0,width=300,height=225)
                self.frame_ML.grid(row=0,column=0,sticky='w')
                self.frame_ML2 = customtkinter.CTkFrame(self.configure_ML, border_width=0, width=300, height=225)
                self.frame_ML2.grid(row=1,column=0,sticky='w')
                #plot label
                self.MLrow0 = customtkinter.CTkLabel(self.frame_ML,width=80,height=20,text='Train',font=('Courier', 16, 'bold'),anchor='w',)
                #X column's textbox and entry
                self.MLrow1 = customtkinter.CTkTextbox(self.frame_ML, width=120,height=20,corner_radius=0, border_width=1)
                self.MLcolumn1 = customtkinter.CTkEntry(self.frame_ML,  width=120,height=26,placeholder_text='X:',corner_radius=0, border_width=1) 
                #new X point textbox and entry
                self.MLrow15 = customtkinter.CTkTextbox(self.frame_ML2, width=120,height=20,corner_radius=0, border_width=1)
                self.MLcolumn15 = customtkinter.CTkEntry(self.frame_ML2,  width=120,height=26,placeholder_text='X:',corner_radius=0, border_width=1) 
                #Y column's textbox and entry
                self.MLrow2 = customtkinter.CTkTextbox(self.frame_ML, width=120,height=20,corner_radius=0, border_width=1)
                self.MLcolumn2 = customtkinter.CTkEntry(self.frame_ML,  width=120,height=26,placeholder_text='Y:',corner_radius=0, border_width=1) 
                #new Y point textbox and entry
                self.MLrow25 = customtkinter.CTkTextbox(self.frame_ML2, width=120,height=20,corner_radius=0, border_width=1)
                self.MLcolumn25 = customtkinter.CTkEntry(self.frame_ML2,  width=120,height=26,placeholder_text='Y:',corner_radius=0, border_width=1) 
                #add point text label
                self.MLrow00 = customtkinter.CTkLabel(self.frame_ML2,width=80,height=20,text='Test',font=('Courier', 16, 'bold'),anchor='w',)
                #class column textbox and label
                self.MLrow3 = customtkinter.CTkTextbox(self.frame_ML, width=120,height=20,corner_radius=0, border_width=1)
                self.MLcolumn3 = customtkinter.CTkEntry(self.frame_ML,  width=120,height=26,placeholder_text='CLASS:',corner_radius=0, border_width=1) 
                #neighbors count's textbox and entry
                self.MLrow4 = customtkinter.CTkTextbox(self.frame_ML, width=120,height=20,corner_radius=0, border_width=1)
                self.MLcolumn4 = customtkinter.CTkEntry(self.frame_ML,  width=120,height=26,placeholder_text='N:',corner_radius=0, border_width=1) 
                #normalize button
                self.MLcolumn45 = customtkinter.CTkButton(self.frame_ML2, width=120,height=26,text='normalize',corner_radius=0, border_width=1,anchor='w',command=self.normalization)
                #predict button
                self.MLcolumn35 = customtkinter.CTkButton(self.frame_ML2, width=120,height=26,text='predict',corner_radius=0, border_width=1,anchor='w',command=lambda : self.predict(self.new_x, self.new_y))
                #plot button
                self.MLplot = customtkinter.CTkButton(self.frame_ML2, width=120,height=26,text='plot',corner_radius=0, border_width=1,anchor='w',command=self.plot_knn)

                #placing widgets
                #textbox
                self.MLrow1.insert('0.0',text='X column:')
                self.MLrow15.insert('0.0',text='new X point(s)')
                self.MLrow2.insert('0.0',text='Y column:')
                self.MLrow25.insert('0.0',text='new Y point(s)')
                self.MLrow3.insert('0.0',text='Class column:')
                self.MLrow4.insert('0.0',text='neighbors count:')
                self.MLrow1.configure(state='disabled', )
                self.MLrow15.configure(state='disabled', )
                self.MLrow2.configure(state='disabled', )
                self.MLrow25.configure(state='disabled', )
                self.MLrow3.configure(state='disabled', )
                self.MLrow4.configure(state='disabled', )
                #entry
                self.MLcolumn1.configure()
                self.MLcolumn15.configure()
                self.MLcolumn2.configure()
                self.MLcolumn25.configure()
                self.MLcolumn3.configure()
                self.MLcolumn4.configure()
                self.MLcolumn1.bind('<Return>',command=self.get_x)
                self.MLcolumn15.bind('<Return>',command=self.get_new_x)
                self.MLcolumn2.bind('<Return>',command=self.get_y)
                self.MLcolumn25.bind('<Return>',command=self.get_new_y)
                self.MLcolumn3.bind('<Return>',command=self.get_c)
                self.MLcolumn4.bind('<Return>',command=self.get_n)
                #button
                self.MLcolumn45.configure()
                self.MLcolumn35.configure()
                self.MLplot.configure()
                #place
                self.MLrow0.grid(row=0, column=0, padx=(30,0), pady=20)
                self.MLrow1.grid(row=1, column=0, padx=(30,0), pady=(10,15))
                self.MLcolumn1.grid(row=1, column=1, pady=(10,15))
                self.MLrow2.grid(row=2, column=0, padx=(30,0), pady=(10,15))
                self.MLcolumn2.grid(row=2, column=1, pady=(10,15))
                self.MLrow3.grid(row=1, column=2, padx=(20,0), pady=(10,15))
                self.MLcolumn3.grid(row=1, column=3, pady=(10,15))
                self.MLrow4.grid(row=2, column=2, padx=(20,0), pady=(10,15))
                self.MLcolumn4.grid(row=2, column=3, pady=(10,15))

                self.MLrow00.grid(row=0, column=0, padx=(30,0), pady=20)
                self.MLrow15.grid(row=1, column=0, padx=(30,0), pady=(10,15))
                self.MLcolumn15.grid(row=1, column=1, pady=(10,15))
                self.MLrow25.grid(row=2, column=0, padx=(30,0), pady=(10,15))
                self.MLcolumn25.grid(row=2, column=1, pady=(10,15))

                self.MLcolumn45.grid(row=3, column=1, padx=(40,0), pady=(10,15))
                self.MLcolumn35.grid(row=3, column=2, padx=(10,0), pady=(10,15))
                self.MLplot.grid(row=3, column=3,padx=(10,0), pady=(10,15))
                self.normalize = False
            case 'regression':
                #train: x, y - plot, new point, add result column, point
                self.configure_ML.geometry(f'{220}x{370}')
                self.Reg_model = Regression1()
                self.frame_ML = customtkinter.CTkScrollableFrame(self.configure_ML,border_width=0,width=220,height=350)
                self.frame_ML.grid(row=0,column=0,sticky='w')
                #train label
                self.MLrow0 = customtkinter.CTkLabel(self.frame_ML,width=80,height=20,text='Train',font=('Courier', 16, 'bold'),anchor='w',)
                #train X textbox and entry
                self.MLrow1 = customtkinter.CTkTextbox(self.frame_ML, width=100,height=20,corner_radius=0, border_width=1)
                self.MLcolumn1 = customtkinter.CTkEntry(self.frame_ML,  width=100,height=26,placeholder_text='X:start:end:step',corner_radius=0, border_width=1) 
                #test X textbox and entry
                self.MLrow15 = customtkinter.CTkTextbox(self.frame_ML, width=100,height=20,corner_radius=0, border_width=1)
                self.MLcolumn15 = customtkinter.CTkEntry(self.frame_ML,  width=100,height=26,placeholder_text='X',corner_radius=0, border_width=1) 
                #Y column's textbox and entry
                self.MLrow2 = customtkinter.CTkTextbox(self.frame_ML, width=100,height=20,corner_radius=0, border_width=1)
                self.MLcolumn2 = customtkinter.CTkEntry(self.frame_ML,  width=100,height=26,placeholder_text='Y:start:end:step',corner_radius=0, border_width=1) 
                #get degree textbox and entry
                self.MLrow3 = customtkinter.CTkTextbox(self.frame_ML, width=100,height=20,corner_radius=0, border_width=1)
                self.MLcolumn3 = customtkinter.CTkEntry(self.frame_ML,  width=100,height=26,placeholder_text='1|2|....',corner_radius=0, border_width=1) 
                #test result
                self.MLrow25 = customtkinter.CTkTextbox(self.frame_ML, width=150,height=20,corner_radius=0, border_width=1)
                self.MLcolumn25 = customtkinter.CTkTextbox(self.frame_ML, width=150,height=20,corner_radius=0, border_width=1)
                #test text label
                self.MLrow00 = customtkinter.CTkLabel(self.frame_ML,width=80,height=20,text='Test',font=('Courier', 16, 'bold'),anchor='w',)
                #plot button
                self.MLplot = customtkinter.CTkButton(self.frame_ML, width=100,height=26,text='plot',corner_radius=0, border_width=1,anchor='w',command=self.Reg_model.plot)
                self.MLplot2 = customtkinter.CTkButton(self.frame_ML, width=100,height=26,text='plot new point',corner_radius=0, border_width=1,anchor='w',command=self.Reg_model.plot_new_point)
                #result text label
                self.MLrow000 = customtkinter.CTkLabel(self.frame_ML,width=80,height=20,text='Output',font=('Courier', 16, 'bold'),anchor='w',)

                self.MLrow1.insert('0.0',text='X column:')
                self.MLrow15.insert('0.0',text='new X point:')
                self.MLrow2.insert('0.0',text='Y column:')
                self.MLrow3.insert('0.0',text='Degree:')
                self.MLrow25.insert('0.0',text='predicted Y')
                self.MLcolumn25.insert('0.0',text='rmse')
                self.MLrow1.configure(state='disabled', )
                self.MLrow15.configure(state='disabled', )
                self.MLrow2.configure(state='disabled', )
                self.MLrow25.configure(state='disabled', )
                self.MLcolumn25.configure(state='disabled', )
                self.MLrow3.configure(state='disabled', )

                self.MLcolumn1.bind('<Return>',command=self.get_x1)
                self.MLcolumn15.bind('<Return>',command=self.get_new_x1)
                self.MLcolumn2.bind('<Return>',command=self.get_y1)
                self.MLcolumn3.bind('<Return>',command=self.get_degree)
                #place
                #text
                self.MLrow0.grid(row=0, column=0, padx=0, pady=5,sticky='w')
                #get x list
                self.MLrow1.grid(row=1, column=0, padx=0, pady=5,sticky='w')
                self.MLcolumn1.grid(row=1, column=1,padx=0, pady=5,sticky='w')
                #get y list
                self.MLrow2.grid(row=2, column=0, padx=0,pady=5,sticky='w')
                self.MLcolumn2.grid(row=2, column=1, pady=5,sticky='w')
                #get degree
                self.MLrow3.grid(row=3, column=0,padx=0, pady=5,sticky='w')
                self.MLcolumn3.grid(row=3, column=1, padx=0,pady=5,sticky='w')
                #text
                self.MLrow00.grid(row=4, column=0, padx=0,pady=5,sticky='w')
                #enter new x
                self.MLrow15.grid(row=5, column=0, padx=0,pady=5,sticky='w')
                self.MLcolumn15.grid(row=5, column=1, padx=0,pady=5,sticky='w')
                #result
                self.MLrow000.grid(row=6, column=0, padx=0,pady=5,sticky='w')
                self.MLrow25.grid(row=7, column=0, padx=0,pady=(5,0),sticky='w',columnspan=2)
                #rmse
                self.MLcolumn25.grid(row=8, column=0, padx=0,pady=(0,5),sticky='w',columnspan=2)
                #plot
                self.MLplot.grid(row=9, column=1, padx=0,pady=(5,0),sticky='e')
                #plot new point
                self.MLplot2.grid(row=10, column=1,padx=0, pady=(0,5),sticky='e')

                self.MLplot.configure()
                self.MLplot2.configure()
            case 'SVM':
                """
                1)when opened, svm class dataframe is created
                2)options:
                >>> choose columns
                >>> choose class col
                >>> choose to sample
                >>> choose to optimize
                """
        self.UI_update_all()
        
    def command_window(self)->None:
        """
        command window method, creates a new cmd window
        """
        #checking cmd_window flag if it's already True
        if self.parametres['cmd_window']:
            return
        #creating a new window
        self.c_window = customtkinter.CTkToplevel(master=self)
        self.c_window.protocol("WM_DELETE_WINDOW", self.on_quit2)
        self.c_window.title('cmd')
        self.c_window.configure(width=500,height=300)
        self.c_window.resizable(0,0)
        # self.c_window.after(205, lambda : self.iconbitmap('icon1.ico'))
        #creating frame
        self.c_frame = customtkinter.CTkFrame(self.c_window)
        self.c_frame.pack(expand=True)
        #creating widgets
        #LOGS frame
        self.c_output = customtkinter.CTkTextbox(self.c_frame,width=500,height=250, border_width=0,corner_radius=0)
        self.c_output.grid(row=0,column=0)
        self.c_output.configure(state='disabled')
        #input frame
        self.c_input = customtkinter.CTkEntry(self.c_frame,width=500,height=50, border_width=1, corner_radius=0)
        self.c_input.grid(row=1,column=0)
        #loading past messages to logs channel
        self.Open_Logs_channel()
        #binding arrow keys and enter key
        self.c_input.bind('<Return>',command=self.get_commands)
        self.c_input.bind('<Up>', self.increment_index)
        self.c_input.bind('<Down>', self.decrement_index)
        #color

        self.c_input.configure(fg_color=BLACK, text_color=WHITE)
        self.c_output.configure(fg_color=BLACK, text_color=WHITE)
        #raising cmd flag
        self.parametres['cmd_window'] = True
  
    def show_data_table(self) -> None:
        """
        Load Data button's method, creates data table and window
        """
        #prevents creating a second data table if one is opened
        if not self.exitflag: 
            return
        #dropping the data window's exit flag
        self.exitflag = False 
        #creating new window
        self.input_window = customtkinter.CTkToplevel(self)
        #binding closing the window event with on_quit method, it will execute whenever the close button is clicked
        self.input_window.protocol("WM_DELETE_WINDOW", self.on_quit)
        self.input_window.title('Data Table')
        self.input_window.resizable(0,0)
        #main table frame, it's a scrollable frame cuz normal frames are whiny bitches
        self.input_frame = customtkinter.CTkScrollableFrame(self.input_window,height=460)
        #creating the tree from the loaded data
        self.create_tree(self.loaded_data)
        #adding scroll bars to the frame
        self.scroll_databaseV = customtkinter.CTkScrollbar(self.input_frame, orientation="vertical", command=self.tree.yview, width=20, height=450)
        self.scroll_databaseV.pack(side=customtkinter.LEFT)
        self.tree.configure(yscrollcommand=self.scroll_databaseV.set)
        self.scroll_databaseH = customtkinter.CTkScrollbar(self.input_frame, orientation="horizontal", command=self.tree.xview, width=650, height=20)
        self.scroll_databaseH.pack(side=customtkinter.BOTTOM)
        self.tree.configure(xscrollcommand=self.scroll_databaseH.set)
        #setting up the table's style and colors
        self.configure_tree()
        #placing the frame and the table
        self.input_frame.configure(width=650)
        self.input_frame.grid(row=1, column=0,sticky='s',padx=(0,10),pady=(20,25))
        self.tree.pack(expand=True)
        #once it's done we tell the program that the data table is ready and call UI_update_all method to enable functions
        self.parametres['table_available'] = True
        self.UI_update_all()
    
    #create tree
    def create_tree(self, data : list[list]) -> None:
        """
        method responsible for creating the data table
        accepts a list of lists as the data argument and uses the first index as the column titles
        it will always show based on the length of the first index and the length of the data array itself, 
        if there is a row that is longer than the first titles row it'll be loaded but it won't show on the table
        """
        #creating the tree 
        self.tree=ttk.Treeview(self.input_frame, column=tuple(data[0]), show='headings', height=21) 
        #setting up columns
        for i in range(1, len(data[0]) + 1):
            self.tree.column(f"# {i}",anchor=customtkinter.CENTER, stretch=customtkinter.NO)
            self.tree.heading(f"# {i}", text=data[0][i - 1])
        #setting up rows
        for ind in range(1, len(data)):
            #checking if the row can't fill all columns
            if len(data[0]) > len(data[ind]):
                #to avoid errors, the empty slot will be filled with empty string
                for i in range(len(data[ind]), len(data[0])):
                    data[ind].append('')
            #inserting the row to the tree
            self.tree.insert('', 'end',text=str(ind), iid=ind-1, values=(data[ind]))
        #checking if the table is modifiable
        if self.settings.get('mode') == 'write':
            self.tree.bind("<Double-1>", lambda event: self.onDoubleClick(event))
            self.tree.bind("<Button-2>", lambda event: self.clearnode(event))
            self.tree.bind("<Double-3>", lambda event: self.clearrow(event))
            self.tree.bind("<MouseWheel>", self.scrolled)
    
    def empty_table(self) -> None:
        """
        Load empty data's method, creates a table with no data and 4 empty columns that can be removed or renamed
        """
        #in case of a rare error, old data can be saved
        try:
            self.on_quit()
        except:
            pass
        #set up only the first row as empty columns
        self.loaded_data = [[''] * 4]
        #creating the data window
        self.show_data_table()
        self.parametres['Data_available'] = True
        self.UI_update_all()

    def reanimate(self, col : str = '', cols : list[str] = [''], mode : str = 'add', column : int|list[int] = 0)->None:
        """
        re-creates tree in order to modify columns
        possible arguments:
        >>> col: specified one column to add, necessary in 'add' mode
        >>> cols: new list of columns that are still present, necessary in 'remove' mode
        >>> mode: 'add'|'remove' 
        >>> column: specified column or range of columns to remove from rows
        now why are col and cols 2 different arguments when they could've served different purposes as one argument? only god knows.
        """
        #in add mode, col argument is added to the current list of columns in the tree
        if mode == 'add':
            new_tree = ttk.Treeview(self.input_frame, column=list(self.tree['columns']) + [col], show='headings', height=21) 
        #but in remove mode, cols argument is the new list of columns
        elif mode == 'remove':
            new_tree = ttk.Treeview(self.input_frame, column=cols, show='headings', height=21) 
        #adding headings
        for i in range(1, len(new_tree['columns']) + 1):
            new_tree.column(f"# {i}",anchor=customtkinter.CENTER, stretch=customtkinter.NO)
            new_tree.heading(f"# {i}", text=new_tree['columns'][i-1])

        #adding rows
        for ind in range(0, len(self.tree.get_children())):
            #in remove mode, specified columns must be removed from the table with their row values
            if mode == 'remove':
                #creates temporary result list called val
                temp = list(self.tree.item(ind, 'values'))  
                val = []
                for _ in range(len(temp)):
                        #removes specified column index from all rows
                        if self.readvalue == 'multiple':
                            if _ in range(column[0], column[1]):
                                continue
                            else:
                                val.append(temp[_])
                        else:
                            if _ == column:
                                continue
                            else:
                                val.append(temp[_])
            #in case of adding a column
            else:
                #copies the table's data and pastes it to a list
                val = list(self.tree.item(ind, 'values'))  
            #adds an empty string in non filled nodes to avoid errors
            if len(new_tree['columns']) > len(self.tree.item(ind, 'values')):
                for i in range(len(self.tree.item(ind, 'values')), len(new_tree['columns'])):
                    val.append('')
            #adds row to the new tree
            new_tree.insert('', 'end',text=str(ind), iid=ind, values=val)
        #creating the new tree widget
        self.tree.destroy()
        self.tree = new_tree
        self.scroll_databaseV.configure(command=self.tree.yview)
        self.scroll_databaseH.configure(command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.scroll_databaseV.set)
        self.tree.configure(xscrollcommand=self.scroll_databaseH.set)
        self.configure_tree()
        if self.settings.get('mode') == 'write':
            self.tree.bind("<Double-1>", lambda event: self.onDoubleClick(event))
            self.tree.bind("<Button-2>", lambda event: self.clearnode(event))
            self.tree.bind("<Double-3>", lambda event: self.clearrow(event))
            self.tree.bind("<MouseWheel>", self.scrolled)
        self.tree.pack(expand=True)
    #quit methods
    def on_quit(self) -> None:
        """
        method executed when closing the data window, used to give saving data option(Note:data is only saved in the app and not locally)
        """
        #checking if data was modified otherwise no point executing
        if self.parametres['modified']:
            #to avoid opening more than one confirmation window
            if not self.exitflag2:
                return
            #dropping the confirmation window flag
            self.exitflag2 = False
            #creating the confirmation window 
            self.confirm = customtkinter.CTkToplevel(self.input_frame)
            #window size
            self.confirm.geometry(f'{300}x{150}')
            #binding closing event with on_quit3 method
            self.confirm.protocol("WM_DELETE_WINDOW", self.on_quit3)
            #title
            self.confirm.title('Save Changes?')
            #disabling resizing
            self.confirm.resizable(0,0)
            #forcing the window to always pop up on top
            self.confirm.attributes('-topmost', 'true')
            #confirmation window frames
            self.confirm_frame = customtkinter.CTkFrame(self.confirm,border_width=0)
            self.confirm_frame2 = customtkinter.CTkFrame(self.confirm,border_width=0)
            #yes button
            self.yes = customtkinter.CTkButton(self.confirm_frame2,text='Yes',command=lambda : self.confirm_choice('y'),width=100,corner_radius=0,border_width=1,)
            #cancel button
            self.no = customtkinter.CTkButton(self.confirm_frame2,text='Cancel',command=lambda : self.confirm_choice('n'),width=100,corner_radius=0,border_width=1,)
            #label
            self.label = customtkinter.CTkLabel(self.confirm_frame, text='do you wanna save changes?',width=100)
            #placing all widgets
            self.confirm_frame.grid(row=0,column=0)
            self.confirm_frame2.grid(row=1,column=0)
            self.label.grid(row=0,column=1,pady=(40,10),padx=(30,20))
            self.yes.grid(row=1,column=0,padx=25)
            self.no.grid(row=1,column=1,padx=25)
        else:
            #executed if no changes were made to the table
            self.on_quit3()

    def on_quit2(self)->None:
        """
        method to close command prompt window and dropping cmd_window flag
        """
        self.c_window.destroy()
        self.parametres['cmd_window'] = False
 
    def on_quit3(self) ->None:
        """
        closing confirmation window method, drops the saving flag and closes data window
        """  
        self.updateflag = False
        #closing data window
        self.exit()

    def exit(self) -> None:
        """
        saves and closes data table's window
        """
        
        #checking if Yes button was clicked or not
        if not self.updateflag:
            #executes if data is discarded
            try:
                self.loaded_data = self.old_data
            except:
                pass

        else:
            #executes to save data
            self.loaded_data = self.convert_tree_to_list()
            #dropping the update flag
            self.updateflag = False
        #closing data table's window
        self.input_window.destroy()
        #setting data window's exit flag to True
        self.exitflag = True
        try:
            #closes machine learning configuration window if it's open
            self.quit_ML()
        except:
            pass
        #dropping parametre flags
        self.parametres['table_available'] = False
        self.parametres['modified'] = False
        #confirming the closing of confirmation window
        self.exitflag2 = True
        try:
            self.confirm.destroy()
        except AttributeError:
            pass
        self.UI_update_all()
  
    def quit_ML(self)->None:
        """
        destroys configuration window and raises exitflagML
        """
        self.exitflagML = True
        self.configure_ML.destroy()
        try:
            del self.Reg_model
        except:
            pass
 
    #widget methods
    #main widgets
    def minimize_1(self)->None:
        """
        minimizes main window
        """
        self.change_geo(240,520)

    def maximize_1(self)->None:
        """
        maximizes main window
        """
        self.change_geo(510,520)

    #configuration frame
    def help_update(self, event):
        match event:
            case 'cmd_button':
                message = ('creates command prompt window\n'
                'with the command prompt window you can archieve many tasks with a few commands which are listed below\n'
                'it also show the logs of the important updates happening while using the app.\n'
                'possible commands list:\n'
                '+------------------------------------------+\n'
                'data -> shows random info about selected file\n'
                'data clear -> clears data from the app\n'
                '+------------------------------------------+\n'
                'cd -> shows current working directory, current directory is considered when saving or loading\n'
                'cd - -> jumps down one directory\n'
                'cd -n -> jumps down n directories\n'
                'cd dirname ->jumps up to a directory\n'
                '+------------------------------------------+\n'
                'color theme -> shows current theme\n'
                'color theme (green|blue|dark-blue) -> changes theme\n'
                'color appearance -> shows current appearance mode\n'
                'color appearance (light|dark)-> changes appearance mode\n'
                'color button -> shows current buttons theme\n'
                'color button (0|1) -> changes buttons theme\n'
                '+------------------------------------------+\n'
                'mode -> shows current edit mode\n'
                'mode (read|write) -> changes current edit mode\n'
                '+------------------------------------------+\n'
                'time (normal|disable) -> disables date text in logs channel\n'
                '+------------------------------------------+\n'
                'type -> shows loaded file type\n'
                '+------------------------------------------+\n'
                'file (load|save) -> opens a file explorer to select a file to use\n')
            case 'maximize_button':
                if self.parametres['extend_1']:
                    message = '''minimizes the screen'''
                else:
                    message = '''maximizes the screen'''
            case 'load_button':
                message = '''disabled when no file data is loaded, when data is present the table window will open when clicking the button'''
            case 'empty_button':
                message = '''creates an empty table when no data is present'''

            case 'default':
                message = ('type help in command prompt or double right click on a widget to gain information about the integration of the program\n'
                '+------------------------------------------+\n'
                'basic guide:\n'
                '1): click command prompt button to open the commands window\n'
                '2): type "file load" and select the excel file you want to analyse\n'
                '3): once it successfully loads the data you can then click Load data button to open a table with all data, you can edit, analyse and save the data after\n'
                '+------------------------------------------+\n'
                'IF NO LOCAL DATA IS AVAILABLE:\n'
                'click create empty table and you can insert data and analyse it\n')
            case 'read_mode':
                message = ('single mode: accepts an integer as input as it searches for a single index to select\n'
                'multiple mode: can select multiple rows/columns or the entire table\n'
                '+------------------------------------------+\n'
                'syntax examples: \n'
                '0:5:1 -> selects from range 0 to 5 while moving one step (0,1,2,3,4,5 are selected)\n'
                '4:10:2 -> selects from range 4 to 10 while moving two steps instead of one (4,6,8,10 are selected)\n'
                '::3 -> selects from first index to last while moving three steps (0,3,6,9... are selected)\n'
                '1:: -> selects from range 1 to last while moving one step (1,2,3... are selected)\n'
                ':: -> selects entire table\n'
                '+------------------------------------------+\n'
                'widgets included:\n'
                'row\n'
                'column\n'
                'remove row\n'
                'remove column')
            case 'select_row':
                message = '''selects a row or multiple rows to assign a value to in value column'''
            case 'select_column':
                message = '''selects a column or multiple columns to assign a value to in value column\ncan take the column's index or column's name as input\nNote:columns with integer names are not prioritized over index'''
            case 'value':
                message = '''enter a value to replace all selected nodes'''
            case 'add_row':
                message = '''adds empty rows at the last index\nenter the number of rows you want to add'''
            case 'add_column':
                message = '''adds a new column at the last index\nenter the new column's name as input\nNote:existing column names are passed'''
            case 'remove_row':
                message = '''removes a row or multiple rows from specified index or a range of indexes'''
            case 'remove_column':
                message = '''removes a selected heading or a range of headings with their descendant nodes from the table\naccepts column's index or name as input'''
            case 'replace_column':
                message = '''replaces selected heading's text name without deleting it's descendants' content'''
            case 'soon':
                message = '''not implemented yet'''
            case  'replace_value':
                message = ('searches for specified value in a range of nodes and replaces it with a new value\n'
                'syntax:\n'
                'key:index:oldvalue:newvalue\n'
                '+------------------------------------------+\n'
                'key : row|column|'' \n'
                'row->selects row with selected index to replace in\n'
                'column->selects column with selected index to replace in\n'
                ' ''->selects all table\n'
                '+------------------------------------------+\n'
                'index : selected row/column index, not used if table is selected\n'
                '+------------------------------------------+\n'
                'oldvalue : searched for value to replace with newvalue\n'
                '+------------------------------------------+\n'
                'newvalue : replacement for oldvalue\n'
                '+------------------------------------------+\n'
                'examples:\n'
                'row:1:None:''\n'
                'column:3:True:1\n'
                '::L:W\n')
            case 'ML':
                message = '''(machine learning) selected algorithm'''
            case 'table':
                message = ('data table guide:\n'
                'double left click: selects the hovered node to edit\n'
                'double right click: clears hovered row from data\n'
                'middle click: clears hovered node\n')

        self.change_help(message)

    def change_help(self, text):
        self.config_help_box.configure(state='normal')
        self.config_help_box.delete('0.0', customtkinter.END)
        self.config_help_box.insert('0.0',text)
        self.config_help_box.configure(state='disabled')
    
    def set_read_config(self, val)->None:
        """
        sets readvalue
        """
        self.readvalue = val
        self.replace_placeholder()
    
    def set_plot(self, mode)->None:
        """
        combobox method (column11), sets learning mode to knn,...
        """
        self.learningmode = mode

    def set_scale_config(self)->None:
        """
        not used yet
        """
        self.column9.configure(text='true' if self.var.get() else 'false')

    def return_row(self, event)->None:
        """
        (column2)accepts integer input of row id or array type input on multiple reading mode, selects row or a range of rows
        examples:
        >>> firstrow:lastrow
        >>> firstrow:lastrow:step
        >>> firstrow::step
        >>> firstrow::
        >>> :lastrow
        >>> :lastrow:step
        >>> ::step
        >>> ::
        Note:if an integer is entered on multiple reading mode, it will select all rows
        """
        try:
            #checks read value
            if self.readvalue == 'single':
                #takes row id as input
                self.rowid = int(self.column2.get())
                self.update_value()
            else:
                #takes array type indexing as input
                self.rowid = self.decode_input('row',self.column2.get())
            #clearing entry
            self.column2.delete(0,customtkinter.END)
            self.create_Log_message(event='config',key='row',sign='positive',text=str(self.rowid))
        except:
            self.create_Log_message(event='config',key='row',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.column2])
            t.start()

    def return_column(self, event)->None:
        """
        (column3)accepts integer input of column index or array type input on multiple reading mode or column name, selects column or a range of columns
        examples:
        >>> firstcolumn:lastcolumn
        >>> firstcolumn:lastcolumn:step
        >>> firstcolumn::step
        >>> firstcolumn::
        >>> :lastcolumn
        >>> :lastcolumn:step
        >>> ::step
        >>> ::
        Note:if an integer is entered on multiple reading mode, it will select all columns
        """
        try:
            #checks read value
            if self.readvalue == 'single':
                try:
                    #takes column index as input
                    self.column = int(self.column3.get())
                    self.update_value()
                except:
                    #takes column name as input
                    self.column = self.tree['columns'].index(self.column3.get())
            else:
                #takes array type indexing as input
                self.column = self.decode_input('column',self.column3.get())
            
            self.column3.delete(0,customtkinter.END)
            self.create_Log_message(event='config',key='column',sign='positive',text=str(self.column))
        except:
            self.create_Log_message(event='config',key='column',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.column3])
            t.start()

    def write_value(self, event)->None: 
        """
        (column4)analyses and writes entered value in column4 on all selected nodes based on column2 and column3
        """
        try:
            #writes a single node
            if type(self.rowid) == int and type(self.column) == int:
                val = self.tree.item(self.rowid, 'values')
                val = list(val)
                val[self.column] = self.entry_text.get()
                self.tree.item(self.rowid,values=val)
            #writes an array of nodes in a column
            elif type(self.rowid) == list and type(self.column) == int:
                if not self.rowid[1]:
                    self.rowid[1] = len(self.tree.get_children())
                for _ in range(self.rowid[0], self.rowid[1] + 1, self.rowid[2]):
                    val = self.tree.item(_, 'values')
                    val = list(val)
                    val[self.column] = self.entry_text.get()
                    self.tree.item(_,values=val)
            #writes an array of nodes in a row
            elif type(self.rowid) == int and type(self.column) == list:
                if not self.column[1]:
                    self.column[1] = len(self.tree['columns'])
                val = self.tree.item(self.rowid, 'values')
                val = list(val)
                for _ in range(self.column[0], self.column[1] + 1, self.column[2]):
                    val[_] = self.entry_text.get()
                    self.tree.item(self.rowid,values=val)
            #writes a 2d array of nodes
            else:
                self.selected(row=self.rowid,column=self.column,value=self.entry_text.get())
            #raises modified flag
            self.parametres['modified'] = True
            self.create_Log_message(event='config',key='value',text=self.entry_text.get())
            #clearing column4
            self.entry_text.set('')
        except:
            t = threading.Thread(target=self.red_alert, args=[self.column4])
            t.start()

    def addrow(self)->None:
        """
        (column5)add empty row(s) to the tree, accepts integer count as the number of rows added
        """
        try:
            #getting input
            count = int(self.column5.get())
            
            #case of 0
            if not count:
                return
            #inserting empty rows with length based off the number of columns
            for _ in range(count):
                self.tree.insert('','end',text=str(_),iid=len(self.tree.get_children()),values=[''] * len(self.tree['columns']))
            #raising modified flag
            self.parametres['modified'] = True
            self.create_Log_message(event='config',key='addrow',sign='positive',text=str(count))
            #clearing entry
            self.column5.delete(0,customtkinter.END)
        except:
            self.create_Log_message(event='config',key='addrow',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.column5])
            t.start()

    def removerow(self)->None:
        """
        (column7)removes a row or a range of rows from the tree, accepts row id or a range of row ids as input
        """
        try:
            #case of one row selected
            if self.readvalue == 'single':
                rowid = int(self.column7.get())
                
                #deletes row and it's content from the table
                self.tree.delete(rowid)
            #case of a range of rows
            else:
                rowids = self.decode_input('row',self.column7.get())
                
                #replaces 0 with children count in end index case
                if not rowids[1]:
                    rowids[1] = len(self.tree.get_children())
                for id in range(rowids[0], rowids[1] + 1):
                    self.tree.delete(id)
            #copying the tree's data and recreating it to re-order row ids correctly
            data = self.convert_tree_to_list()
            self.tree.destroy()
            self.create_tree(data)
            self.scroll_databaseV.configure(command=self.tree.yview)
            self.scroll_databaseH.configure(command=self.tree.xview)
            self.tree.configure(yscrollcommand=self.scroll_databaseV.set)
            self.tree.configure(xscrollcommand=self.scroll_databaseH.set)
            self.configure_tree()
            self.tree.pack(expand=True)
            #raising modified flag
            self.parametres['modified'] = True
            self.create_Log_message(event='config',key='removerow',sign='positive')
            self.column7.delete(0,customtkinter.END)
        except:
            self.create_Log_message(event='config',key='removerow',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.column7])
            t.start()

    def addcolumn(self)->None:
        """
        (column6)adds a new column to the table, accepts column's name as input as long as it's not present already
        """
        try:
            #getting input
            column = self.column6.get()
            
            #returns if input is empty or already exists
            if not column or column in self.tree['columns']:
                return
            #raising modified flag
            self.parametres['modified'] = True
            #re-creating the tree with the new column
            self.reanimate(column)
            self.create_Log_message(event='config',key='addcolumn',sign='positive',text=column)
            #clearing entry
            self.column6.delete(0,customtkinter.END)
        except:
            self.create_Log_message(event='config',key='addcolumn',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.column6])
            t.start()
    
    def removecolumn(self)->None:
        """
        (column8)remove a column from the tree, accepts column's index or name as input and deletes it with it's descendant rows completly
        """
        try:
            #checks read value
            if self.readvalue == 'single':
                #getting input
                try:
                    column = int(self.column8.get())
                except:
                    column = list(self.tree['columns']).index(self.column8.get())
                #creates a temporary list and removes specified column
                temp = list(self.tree['columns']) 
                temp.pop(column)
            else:
                #gets a range of columns to delete
                columns = self.decode_input('column', self.column8.get())
                #replaces end value with number of columns in case of 0
                if not columns[1]:
                    columns[1] = len(self.tree['columns'])
                #condition where the specified end index is out of range
                elif columns[1] > len(self.tree['columns']):
                    raise ValueError
                temp = []
                for col in range(len(list(self.tree['columns']))):
                    if col in range(columns[0], columns[1]+1):
                        continue
                    else:
                        temp.append(list(self.tree['columns'])[col])
            #re-creates the tree with the new temporary data
            self.reanimate(cols=temp, mode='remove', column=columns)
            #clearing entry
            self.column8.delete(0,customtkinter.END)
            #raising modified flag
            self.parametres['modified'] = True
            self.create_Log_message(event='config',key='removecolumn',sign='positive')
        except:
            self.create_Log_message(event='config',key='removecolumn',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.column8])
            t.start()

    def column_scale(self): #not implemented
        """
        1)assume column exist
        2)all rows in that column are affected
        3)can scale based on other column or scale dependantly
        4)specify if its a string or a number
        5)input first value if its dependant
        """
        if self.var.get():
            try:
                column = int(self.column10.get())
            except:
                column = self.tree['columns'].index(self.column10.get())
  
    def replace_column(self)->None:
        """
        (row85)changes a column's name
        >>> syntax : oldname->newname | columnindex->newname
        """
        try:
            #get input
            inp = self.column85.get()
            
            #decode input
            inp = inp.split(sep='->')
            #get column index
            try:
                old = int(inp[0])
            except ValueError:
                old = list(self.tree['columns']).index(inp[0])
            #get new name
            new = inp[1]
            if new in self.tree['columns']:
                raise ValueError
            new_data = self.convert_tree_to_list()
            new_data[0][old] = new
            self.tree.destroy()
            self.create_tree(new_data)
            self.scroll_databaseV.configure(command=self.tree.yview)
            self.scroll_databaseH.configure(command=self.tree.xview)
            self.tree.configure(yscrollcommand=self.scroll_databaseV.set)
            self.tree.configure(xscrollcommand=self.scroll_databaseH.set)
            self.configure_tree()
            self.tree.pack(expand=True)
            #raising modified flag
            self.parametres['modified'] = True
            self.create_Log_message(event='replacecolumn',sign='positive',text1=str(old),text2=new)
            self.column85.delete(0, customtkinter.END)
        except:
            self.create_Log_message(event='replacecolumn',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.column85])
            t.start()
   
    def replace_value(self)->None:
        """
        (row95)replaces common values in a row|column|table with a new entered value
        >>> syntax: row|col:index:old:new
        """
        try:
            key, index, old, new = self.column95.get().split(sep=':')
            
            id_count = len(self.tree.get_children())
            count = 0
            if key == '':
                #updates value in the entire tree
                for id in range(id_count):
                    temp = list(self.tree.item(id,'values')) 
                    res = []
                    for item in temp:
                        if item != old:
                            res.append(item)
                        else:
                            res.append(new)
                            count += 1
                    self.tree.item(id,values=res)
                
            elif key == 'col':
                #updates the value in one column
                try:
                    index = int(index)
                except ValueError:
                    index = list(self.tree['columns']).index(index)

                for id in range(id_count):
                    temp = list(self.tree.item(id,'values')) 
                    if temp[index] == old:
                        temp[index] = new
                        count += 1
                    self.tree.item(id, values=temp)
            elif key == 'row':
                #updates value in one row
                index = int(index)
                temp = list(self.tree.item(index,'values'))
                res = []
                for item in temp:
                    if item == old:
                        res.append(new)
                        count += 1
                    else:
                        res.append(item)
                self.tree.item(index, values=res)
                self.create_Log_message(event='replace',sign='positive',text1=old,text2=new,text3=str(count))
                self.parametres['modified'] = True
                self.column95.delete(0, customtkinter.END)
        except:
            self.create_Log_message(event='replace',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.column95])
            t.start()
        
    #table
    def confirm_choice(self, choice : str)->None:
        """
        Yes and cancel buttons method, main method to set update flag and execute closing the window
        """
        if choice == 'y':
            self.updateflag = True
            self.exit()
        else:
            self.updateflag = False
            self.exit()

    def clearrow(self, event)->None: 
        """
        clears a row without deleting it
        """
        try:
            #gets rowid of selected row
            rowid = self.tree.identify_row(event.y)
            #returns if id was not found
            if not rowid:
                return
            #replaces values in that row with empty strings
            self.tree.item(rowid, values=[''] * len(self.tree['columns']))
            self.parametres['modified'] = True
        except:
            pass

    def clearnode(self, event)->None:
        """
        clears a single node from the tree
        """
        try:
            #gets row id and column from event
            rowid = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)
            #returns if id is out of range
            if not rowid:
                return
            #create a copy of that row and modify it
            temp = list(self.tree.item(rowid,'values'))
            temp[int(column[1:])-1] = ''   
            #assign the specified row with the new values         
            self.tree.item(rowid, values=temp)
            self.parametres['modified'] = True
        except:
            pass

    def scrolled(self, event)->None:
        """
        destroys custom entry pop up when scrolling 
        """
        try:
            self.entryPopup.destroy()
        except AttributeError:
            pass
    
    def onDoubleClick(self, event)->None:
        '''Executed, when a row is double-clicked'''
        # close previous popups
        try:  # in case there was no previous popup
            self.entryPopup.destroy()
        except AttributeError:
            pass
        # what row and column was clicked on
        rowid = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        # return if the header was double clicked
        if not rowid:
            return
        try:
            # get cell position and cell dimensions
            x, y, width, height = self.tree.bbox(rowid, column)
        except ValueError:
            return
        pady = height // 2
        # place Entry Widget
        text = self.tree.item(rowid, 'values')[int(column[1:])-1]
        self.entryPopup = EntryPopup(self.tree, rowid, int(column[1:])-1, text)
        self.entryPopup.place(x=x, y=y+pady, width=width, height=height, anchor='w')
        self.parametres['modified'] = True
    #ML window
    #knn
    def get_x(self, event)->None:
        """
        (MLcolumn1)accepts an integer or an existing column's name as input, sets the column as x coordinates as long as y and class column are also the same length with x
        """
        try:
            #getting input
            x = self.get_input(self.MLcolumn1)
            res : list = []
            #creating a list with all values in x column
            for _ in range(len(self.tree.get_children())):
                res.append(float(self.tree.item(_,'values')[x]))
            self.x = res
            self.normalize = False
            self.UI_update_all()
            self.create_Log_message(event='knn',key='base_point',sign='positive')
            #clearing entry
            self.MLcolumn1.delete(0, customtkinter.END)
        except:
            self.create_Log_message(event='knn',key='base_point',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn1])
            t.start()

            
    def get_y(self, event)->None:
        """
        (MLcolumn2)accepts an integer or an existing column's name as input, sets the column as y coordinates as long as x and class column are also the same length with y
        """
        try:
            #getting input
            y = self.get_input(self.MLcolumn2)
            
            res : list = []
            #creating a list with all values in y column
            for _ in range(len(self.tree.get_children())):
                res.append(float(self.tree.item(_,'values')[y]))
            self.y = res
            self.normalize = False
            self.UI_update_all()
            self.create_Log_message(event='knn',key='base_point',sign='positive')
            #clearing entry
            self.MLcolumn2.delete(0, customtkinter.END)
        except:
            self.create_Log_message(event='knn',key='base_point',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn2])
            t.start()
    
    def get_c(self, event)->None:
        """
        (MLcolumn3)accepts an integer or an existing column's name as input, sets the column as points' classes as long as x and y column are also the same length with the class column
        """
        try:
            #getting input
            c = self.get_input(self.MLcolumn3)
            res : list = []
             #creating a list with all values in class column
            for _ in range(len(self.tree.get_children())):
                res.append(float(self.tree.item(_,'values')[c]))
            self.c = res
            self.UI_update_all()
            self.create_Log_message(event='knn',key='base_point',sign='positive')
            #clearing entry
            self.MLcolumn3.delete(0, customtkinter.END)
        except:
            self.create_Log_message(event='knn',key='base_point',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn3])
            t.start()

    def get_new_x(self, event) -> None:
        """
        (MLcolumn15)getting new x coordinates to test with K-nearest neighbors method, can take one point or n amount of points and accepts if new Y has n points as well
        """
        try:
            #getting input
            val = self.MLcolumn15.get()
            #checking if the input is a column name and returning column's index
            if val.isalpha():
                val = self.get_input(self.MLcolumn15)
                res : list = []
                for _ in range(len(self.tree.get_children())):
                    res.append(float(self.tree.item(_,'values')[val]))
                val = res

            #checking if the input is a string of numbers and returning a list
            elif not val.isnumeric():
                val = val.split(sep=',')
                val = [float(i) for i in val]
            #normal case with one number input
            else:
                val = [float(val)]

            if self.normalize:
                for _ in range(len(val)):
                    val[_] = (val[_] / self.max_x)
            
            self.new_x = val
            #clearing the entry
            self.MLcolumn15.delete(0, customtkinter.END)
            self.UI_update_all()
            #calling for a print in command prompt
            self.create_Log_message(event='knn',key='new_point',sign='positive')
        except:
            #case of an error in the input
            self.create_Log_message(event='knn',key='new_point',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn15])
            t.start()
        
    def get_new_y(self, event) -> None:
        """
        (MLcolumn25)getting new y coordinates to test with K-nearest neighbors method, can take one point or n amount of points and accepts if new x has n points as well
        """
        try:
            #getting input
            val = self.MLcolumn25.get()
            #checking if the input is a column name and returning column's index
            if val.isalpha():
                val = self.get_input(self.MLcolumn25)
                res : list = []
                for _ in range(len(self.tree.get_children())):
                    res.append(float(self.tree.item(_,'values')[val]))
                val = res
            #checking if the input is a string of numbers and returning a list
            elif not val.isnumeric():
                val = val.split(sep=',')
                val = [float(i) for i in val]
            #normal case with one number input
            else:
                val = [float(val)]
            
            if self.normalize:
                for _ in range(len(val)):
                    val[_] = (val[_] / self.max_y)
                
            #clearing the entry
            self.MLcolumn25.delete(0, customtkinter.END)
          
            self.new_y = val
            self.UI_update_all()
            #calling for a print in command prompt
            self.create_Log_message(event='knn',key='new_point',sign='positive')
        except:
            #case of an error in the input
            self.create_Log_message(event='knn',key='new_point',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn25])
            t.start()
    
    def get_n(self, event) -> None:
        """
        (MLcolumn4)getting number of neighbors considered
        """
        try:
            #getting input
            n = int(self.MLcolumn4.get())
            #setting the new number of neighbors considered in the algorithm
            self.set_neighbors(n)
            self.UI_update_all()
            #printing into the command prompt
            self.create_Log_message(event='knn',key='neighbor',sign='positive',text=n)
            #clearing entry
            self.MLcolumn4.delete(0, customtkinter.END)
        except ValueError:
            #in case of an input error
            self.create_Log_message(event='knn',key='neighbor',sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn4])
            t.start()
  
    def normalization(self)-> None:
        """normalize x and y columns in case of a large difference between column values"""
        try:
            x = self.x
            y = self.y
            self.max_x = max(x)
            self.max_y = max(y)
            new_x = []
            new_y = []
            for _ in range(len(self.x)):
                new_x.append((x[_]-min(x))/(max(x) - min(x)))
                new_y.append((y[_]-min(y))/(max(y) - min(y)))
            self.normalize = True
            self.x = new_x
            self.y = new_y
            self.UI_update_all()
        except:
            pass
    #regression
    def get_x1(self, event):
        try:
            res= self.get_input(self.MLcolumn1)
            self.Reg_model.set_x(res)
            self.create_Log_message(event='regression', key='X', sign='positive', text=res)
        except:
            self.create_Log_message(event='regression', key='X', sign='negative')
        try:
            self.Reg_model.create_model()
            self.UI_update_all()
            self.update_textbox(self.MLcolumn25, self.Reg_model.get_rmse())
            self.create_Log_message(event='regression', key='rmse', sign='positive', text=self.Reg_model.get_rmse())
        except:
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn1])
            t.start()
    
    def get_y1(self, event):
        try:
            res= self.get_input(self.MLcolumn2)
            self.Reg_model.set_y(res)
            self.create_Log_message(event='regression', key='Y', sign='positive', text=res)
        except:
            self.create_Log_message(event='regression', key='Y', sign='negative')
        try:
            self.Reg_model.create_model()
            self.UI_update_all()
            self.update_textbox(self.MLcolumn25, self.Reg_model.get_rmse())
            self.create_Log_message(event='regression', key='rmse', sign='positive', text=self.Reg_model.get_rmse())
        except:
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn2])
            t.start()

    def get_new_x1(self, event):
        try:
            res= float(self.MLcolumn15.get())
            self.create_Log_message(event='regression', key='newX', sign='positive', text=res)
        except:
            self.create_Log_message(event='regression', key='newX', sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn15])
            t.start()
        self.MLcolumn15.delete(0, customtkinter.END)
        self.Reg_model.predict_new_point(res)
        self.UI_update_all()
        self.update_textbox(self.MLrow25, self.Reg_model.new_y)
        self.create_Log_message(event='regression', key='newY', sign='positive', text=self.Reg_model.new_y)

    def get_degree(self, event):
        try:
            res = abs(int(self.MLcolumn3.get()))
            self.MLcolumn3.delete(0, customtkinter.END)
            self.Reg_model.set_degree(res)
            self.create_Log_message(event='regression', key='degree', sign='positive', text=res)
        except ValueError:
            self.create_Log_message(event='regression', key='degree', sign='negative')
            t = threading.Thread(target=self.red_alert, args=[self.MLcolumn3])
            t.start()

        try:
            self.Reg_model.create_model()
            self.UI_update_all()
            self.update_textbox(self.MLcolumn25, self.Reg_model.get_rmse())
            self.create_Log_message(event='regression', key='rmse', sign='positive', text=self.Reg_model.get_rmse())
        except:
            pass
    #command prompt
    def get_commands(self, event)->None:
        '''
        gets command input and decodes it to a readable format to be executed
        commands list:
        >>> data (''| clear)
        >>> cd (-|-n|dir)
        >>> color ('' theme:green|blue|dark-blue| appearance:dark|light button:0|1)
        >>> mode (read|write)
        >>> time (disable|normal)
        >>> type
        >>> file (load|save)
        >>> help
        '''
        try:
            #get input
            command = self.c_input.get().split()
            #save input in memo 
            self.memo.append(self.c_input.get())
            #clear entry
            self.c_input.delete(0, customtkinter.END)
            #decode input
            data, cd, color, mode, time, type, file, prompt, help = self.read_commands(command)
            #execute command
            self.execute_commands(data=data, cd=cd, color=color, mode=mode, time=time, type=type, file=file, prompt=prompt, help=help)
            #delete oldest input from list when it exceeds length=20
            if len(self.memo) > 20:
                self.memo.pop(0)
        except ValueError:
            self.create_Log_message(event='command error')

    def execute_commands(self, **kargs)->None:
        """
        executes commands from command prompt
        arguments:
        >>> data: True|False
        >>> cd: True|False
        >>> color: True|False
        >>> mode: True|False
        >>> time: True|False
        >>> type
        >>> file: True|False
        >>> prompt: None|extra arguments to specify certain executions
        >>> help
        """ 
        try:
            #ain't explaining allat
            if kargs.get('data'):
                if kargs.get('prompt'):
                    if kargs.get('prompt')[0] == 'clear':
                        self.Clear_all_data()
                else:
                    if self.parametres['Data_available']:
                        self.create_Log_message(event='data',sign='positive')
                    else:
                        self.create_Log_message(event='data',sign='negative')
            elif kargs.get('help'):
                self.help_update('table')
            elif kargs.get('cd'):
                prompt = kargs.get('prompt')
                if prompt == None:
                    self.create_Log_message(event='cd', text='current directory:' + self.cwd)

                elif prompt[0][0] == '-':
                    if len(prompt[0]) == 1:
                        self.return_to_dir()
                    else:
                        for i in range(int(prompt[0][1:])):
                            self.return_to_dir()
                    self.create_Log_message(event='custom', text='current directory:' + self.cwd)
                else:
                    try:
                        self.change_dir(*prompt)
                        self.create_Log_message(event='custom', text='current directory:' + self.cwd)
                    except FileNotFoundError:
                        self.create_Log_message(event='cd', text='cannot locate file in the current directory.')
                
            elif kargs.get('color'):
                global curr_appearance_mode, curr_theme_color
                if kargs.get('prompt'):
                    prompt = kargs.get('prompt')
                    try:
                        if prompt[0] == 'theme':
                            if len(prompt) == 1:
                                self.create_Log_message(event='color',text='theme color:' +themes[curr_theme_color])
                            else:
                                curr_theme_color = int(prompt[1])
                                a.load_theme('themes\\'+themes[curr_theme_color])
                                self.reset_UI()
                                self.create_Log_message(event='color',text='theme color was changed to: ' + themes[curr_theme_color].split('.')[0])
                        elif prompt[0] == 'appearance':
                            if len(prompt) == 1:
                                self.create_Log_message(event='color',text='appearance color: '+appearance_color[curr_appearance_mode])
                            else:
                                curr_appearance_mode = appearance_color.index(prompt[1])
                                self.change_appearance_mode_event(curr_appearance_mode)
                                self.create_Log_message(event='color',text='appearance color was changed to: ' + appearance_color[curr_appearance_mode])
                        elif prompt[0] == 'button':
                            if len(prompt) == 1:
                                self.create_Log_message(event='color',text='buttons color :' + appearance_color[self.parametres['default_color']])
                            else:
                                self.parametres['default_color'] = int(prompt[1])
                                self.create_Log_message(event='color',text='buttons color changed to :' +  appearance_color[self.parametres['default_color']])
                    except IndexError:
                        self.create_Log_message(event='color',text='option not available.')
                else:
                    raise Exception
            elif kargs.get('mode'):
                if kargs.get('prompt'):
                    if kargs.get('prompt')[0].lower() == 'read' or kargs.get('prompt')[0].lower() == 'r':
                        self.settings['mode'] = 'read'
                        self.create_Log_message(event='mode',text=self.settings.get('mode'),sign='positive')
                        self.reset_UI()
                    elif kargs.get('prompt')[0].lower() == 'write' or kargs.get('prompt')[0].lower() == 'w':
                        self.settings['mode'] = 'write'
                        self.create_Log_message(event='mode',text=self.settings.get('mode'),sign='positive')
                        self.reset_UI()
                    else:
                        self.create_Log_message(event='mode',text='option unavailable.',sign='negative')
                    
                else:
                    self.create_Log_message(event='custom',text=self.settings.get('mode'))
          
            elif kargs.get('time'):
                if kargs.get('prompt')[0].lower() == 'disable' or kargs.get('prompt')[0].lower() == 'd':
                    self.settings['enable_time'] = False
                elif kargs.get('prompt')[0].lower() == 'normal' or kargs.get('prompt')[0].lower() == 'n':
                    self.settings['enable_time'] = True
                self.create_Log_message(event='time',text=str(self.settings['enable_time']))
    
            elif kargs.get('type'):
                    self.create_Log_message(event='type',text=self.settings['Load_from'])
                    
            elif kargs.get('file'):
                if kargs.get('prompt'):
                    if kargs.get('prompt')[0].lower() == 'save':
                        try:
                            path = customtkinter.filedialog.askopenfilename(initialdir=self.cwd, title='choose or create a save file')
                            self.save_name, self.settings['Save_to']= os.path.split(path)[1].split(sep='.')
                            self.name = self.save_name
                            self.save_data(path)
                            self.create_Log_message(event='file',text=self.save_name+'.'+self.settings['Save_to'],key='save',sign='positive')
                        except AttributeError:
                            self.create_Log_message(event='file',text=self.save_name+'.'+self.settings['Save_to'],key='save',sign='negative')
                            
                    elif kargs.get('prompt')[0].lower() == 'load':
                        path = customtkinter.filedialog.askopenfilename(initialdir=self.cwd, title='load data')
                        try:
                            self.path = path
                            self.Clear_all_data()
                            self.settings['Load_from'] = os.path.split(self.path)[1].split(sep='.')[1]
                            self.Load_data()                                
                            self.Load_name = os.path.split(self.path)[1].split(sep='.')[0]
                            self.create_Log_message(event='file',text=self.Load_name+'.'+self.settings['Load_from'],key='load',sign='positive')
                        except AttributeError:
                            self.create_Log_message(event='file',text=self.Load_name+'.'+self.settings['Load_from'],key='load',sign='negative')
                        self.m_text.configure(text=f'loaded file: {self.Load_name}')
                else:
                    raise Exception
            else:
                raise Exception
            
        except Exception:
            self.create_Log_message(event='custom',text='invalid command')
            t = threading.Thread(target=self.red_alert, args=[self.c_input])
            t.start()

        self.UI_update_all()

    def red_alert(self, widget):
        og = widget._border_color

        widget.configure(border_color=RED)
        time.sleep(0.5)
        widget.configure(border_color=og)
     
    def Load_data(self)->None: #soon
        """
        responsible for reading data from local files and from clipboard
        """
        #uses loading method based off the file's name
        try:
            if self.settings.get('Load_from') == 'xlsx':
                self.read_xslx() 
            elif self.settings.get('Load_from') == 'txt':
                self.read_json()
            elif self.settings.get('Load_from') == 'csv':
                self.read_csv()
            # elif self.settings.get('Load_from') == 'html': #fix
            #     self.read_html() #loads it as a list of 1
            # elif self.settings.get('Load_from') == 'clipboard': #fix
            #     self.read_clipboard()
            else:
                raise AttributeError
            #checks if there is data in the file
            try:
                if not self.dataframe.empty:
                    self.parametres['Data_available'] = True
            except AttributeError:
                #in case of the dataframe being created as a list
                if self.dataframe:
                    self.parametres['Data_available'] = True
            #reshapes dataframe in a list[list] form
            self.loaded_data = self.convert_to_ttk_table()
        except:
            raise AttributeError

    def save_data(self, path:str)->None:
        """
        saves current data to a local file
        """
        try:
            if self.settings['Save_to'] == 'xlsx':
                save_excel(data = self.loaded_data, name=self.save_name)
            elif self.settings['Save_to'] == 'txt':
                self.save_json(path)
            elif self.settings['Save_to'] == 'csv':
                self.save_csv(path)
            # elif self.settings['Save_to'] == 'html':
            #     self.save_html(path)
            # elif self.settings['Save_to'] == 'clipboard':
            #     self.save_clipboard()
            else:
                raise AttributeError
        except:
            raise AttributeError
 
    def get_file_data(self)->str:
        """
        returns loaded ile information, to use type data in command prompt when data is loaded
        """
        text = f'file name: {os.path.split(self.path)[1]}\nfile directory: {os.path.split(self.path)[0]}\ncreation time: {datetime.fromtimestamp(os.stat(self.path).st_birthtime)}\nlast modified: {datetime.fromtimestamp(os.stat(self.path).st_mtime)}\nsize: {os.stat(self.path).st_size} bytes\n'
        return text

    def change_appearance_mode_event(self, new_appearance_mode: int)->None: 
        """
        changes appearance mode
        """
        customtkinter.set_appearance_mode(appearance_color[new_appearance_mode])


    def increment_index(self, event)->None:
        """
        command prompt binding method
        """
        try:
            self.memo_index += 1
            if self.memo_index > 0:
                raise IndexError
            self.preview_message()
        except IndexError:
            self.memo_index -= 1

    def decrement_index(self, event)->None:
        """
        command prompt binding method
        """
        try:
            self.memo_index -= 1
            if abs(self.memo_index) > len(self.memo):
                raise IndexError
            self.preview_message()
        except IndexError:
            self.memo_index += 1

    def Clear_all_data(self)->None:
        """
        clears all data
        """
        try:
            self.Load_name = ''
            self.m_text.configure(text=f'loaded file: {self.Load_name}')
            try:
                self.on_quit()
            except:
                pass
            self.parametres['Data_available'] = False
            self.change_geo(240,520)
            
        except AttributeError:
            pass

    #decoders
    def get_input(self, entry : customtkinter.CTkEntry) -> int|list|None:
        """
        used to read an entry input and return an integer version or look for the column name and return the index
        1:0:2:1
        """
        if entry.get().find(':') != -1:
            step = ''
            if entry.get().count(':') == 3:
                col, start, end, step = entry.get().split(sep=':')
                
            elif entry.get().count(':') == 2:
                col, start, end = entry.get().split(sep=':')

            #getting values
            if start == '':
                start = 0
            if end == '':
                end = len(self.tree.get_children())
            if step == '':
                step = 1
            start = int(start)
            end = int(end)
            step = int(step)
            #getting column
            try:
                #returns input as an integer
                col = int(col)
            except:
                #returns column's index after recieving column's name as an input
                col = self.tree['columns'].index(col)
            #getting range
            res = []
            for _ in range(start, end, step):
                res.append(int(self.tree.item(_,'values')[col]))
            entry.delete(0, customtkinter.END)
            return res
        
        else:
            try:
                #returns input as an integer
                col = int(entry.get())
                return col
            except:
                #returns column's index after recieving column's name as an input
                try:
                    col = self.tree['columns'].index(entry.get())
                    return col
                except ValueError:
                    #returns None in case of floating input, index out of range or column not found
                    return None
 
    def selected(self, **kargs) -> None: 
        """
        Modify a matrix of values to one value
        """
        #takes a list of 3 elements and separates them
        rowstart, rowend, rowstep = kargs.get('row')
        colstart, colend, colstep = kargs.get('column')
        #replaces 0 to the length of the array in case of no end value was specified
        if not rowend:
            rowend = len(self.tree.get_children())
        if not colend:
            colend = len(self.tree["columns"])
        #getting the entered value
        val = kargs.get('value')
        #replaces all values in the matrix with val
        for row in range(rowstart, rowend, rowstep):
            data = list(self.tree.item(row, 'values'))
            for col in range(colstart, colend, colstep):
                data[col] = val
            self.tree.item(row,values=data)

    def decode_input(self, event : str, entry : str)->list[int]:
        """
        reads an array type index input and returns it as a list of 3 key elements
        """
        #initializing start, end and step value in case of no specified input to any
        start = 0
        end = 0
        step = 1
        #addressing all input cases
        if entry.count(':') == 1:
            start, end = entry.split(sep=':')
        elif entry.count(':') == 2:
            if entry.find('::') != -1:
                start, step = entry.split(sep='::')
            else:
                start, end, step = entry.split(sep=':')
        if start == '':
            start = 0
        if end == '':
            end = 0
        if step == '':
            step = 1
        #returns row ids
        if event == 'row':
            return [int(start), int(end), int(step)]
        #returns column indexes
        elif event == 'column':
            try:
                return [int(start), int(end), int(step)]
            except:
                start = list(self.tree['columns']).index(start)
                end = list(self.tree['columns']).index(end)
                return [start, end, int(step)]
  
    def convert_tree_to_list(self)->list[list]:
        """
        converts present data in the table to a 2d array
        """
        data = []
        data.append(list(self.tree['columns']))
        for line in self.tree.get_children():
            row = []
            for item in self.tree.item(line)['values']:
                row.append(item)
            data.append(row)
        return data

    def read_commands(self, command : list[str]):
        """
        decodes commands
        """
        data = None
        cd = None
        color = None
        mode = None
        time = None
        type = None
        file = None
        prompt = None
        help = None
        if len(command) == 0:
            return data, cd, color, mode, time, type, file, prompt, help
        match command[0].lower():
            case 'data':
                data = True
            case 'cd':
                cd = True
            case 'color':
                color = True
            case 'mode':
                mode = True
            case 'time':
                time = True
            case 'type':
                type = True
            case 'file':
                file = True
            case 'help':
                help = True
        if len(command) > 1:
            prompt = command[1:]
        return data, cd, color, mode, time, type, file, prompt, help
 
    #setters
    def UI_update_all(self)->None:
        """
        updates appearance and state of widgets after changing a parameter
        """
        
        #button disable\swap
        self.m_button2.configure(text='<<<' if self.parametres['extend_1'] else '>>>', 
                                 command=self.minimize_1 if self.parametres['extend_1'] else self.maximize_1)
        self.m_button3.configure(state='normal' if self.parametres['Data_available'] else 'disabled')
        self.m_button4.configure(state='disabled' if self.parametres['Data_available'] else 'normal')
        #config frame
        if not self.parametres['table_available']:
            self.column2.delete(0,customtkinter.END)
            self.column3.delete(0,customtkinter.END)
            self.column4.delete(0,customtkinter.END)
            self.column5.delete(0,customtkinter.END)
            self.column6.delete(0,customtkinter.END)
            self.column7.delete(0,customtkinter.END)
            self.column8.delete(0,customtkinter.END)
            self.column85.delete(0,customtkinter.END)
            self.column95.delete(0,customtkinter.END)
            self.column10.delete(0,customtkinter.END)
        
        self.column05.configure(state='readonly' if self.parametres['table_available'] else 'disabled')
        self.column2.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column3.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column4.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column5.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column6.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column7.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column8.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column85.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column95.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column9.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column10.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.column11.configure(state='readonly' if self.parametres['table_available'] else 'disabled')
        self.column4.focus_force()
        self.row5.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.row6.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.row7.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.row8.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.row85.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.row95.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        self.row11.configure(state='normal' if self.parametres['table_available'] else 'disabled')
        #data frame
        if not self.exitflag:
            self.configure_tree()

        #ML
        if not self.exitflagML:
            match self.learningmode:
                case 'knn':
                    self.MLcolumn45.configure(state='disabled' if (bool(self.x and self.y and self.c) and not(self.normalize)) == False else 'normal')
                    self.MLcolumn35.configure(state='disabled' if bool(self.new_x and self.new_y) == False else 'normal')
                    self.MLplot.configure(state='disabled' if bool(self.x and self.y and self.c) == False else 'normal')
                case 'regression':
                    self.MLcolumn15.configure(state='normal' if self.Reg_model.modelcheck else 'disabled')
                    self.MLplot.configure(state='normal' if self.Reg_model.modelcheck else 'disabled')
                    self.MLplot2.configure(state='normal' if (self.Reg_model.new_modelcheck) else 'disabled')

    def set_conf_values(self)->None:
        """
        method used to initiate configuration frame's widgets' initial states and coloring
        """
        #colors
        if 'default' in a._currently_loaded_theme:
            self.column05.configure(fg_color=L_YELLOW)
            self.row5.configure(fg_color=D_YELLOW)
            self.row7.configure(fg_color=D_YELLOW)
            self.row85.configure(fg_color=L_GREEN)
            self.column85.configure(fg_color=L_GREEN)
            self.row95.configure(fg_color=D_GREEN)
            self.column95.configure(fg_color=L_GREEN)
            self.row9.configure(fg_color=D_GREEN)
            self.row10.configure(fg_color=L_GREEN)
            self.column10.configure(fg_color=L_GREEN)
            self.row11.configure(fg_color=D_GREEN)
        #textbox
        self.row05.insert('0.0',text='data read mode:')
        self.row1.insert('0.0',text='Property')
        self.column1.insert('0.0',text='Value')
        self.row2.insert('0.0',text='row')
        self.row3.insert('0.0',text='column')
        self.row4.insert('0.0',text='value')
        self.row9.insert('0.0', text='column scale')
        self.row10.insert('0.0', text='not yet:')
        self.row05.configure(state='disabled')
        self.row1.configure(state='disabled')
        self.row2.configure(state='disabled')
        self.row3.configure(state='disabled')
        self.row4.configure(state='disabled')
        self.row9.configure(state='disabled')
        self.row10.configure(state='disabled')
        #entries and inputs
        self.column2.bind('<Return>',command=self.return_row)
        self.column3.bind('<Return>',command=self.return_column)
        self.column4.bind('<Return>',command=self.write_value)
        self.column1.configure(state='disabled')
        #buttons

    def update_value(self)->None:
        """
        shows present value in selected node, only used on one single selected value
        """
        try:
            val = self.tree.item(self.rowid, 'values')[self.column]
            self.entry_text.set(val)
            self.column4.focus_force()
            self.column2.configure(placeholder_text=self.rowid)
            self.column3.configure(placeholder_text=self.column)
        except:
            return

    def configure_tree(self)->None:
        """
        configures table's theme and colors
        """
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview',
                        background=colors[self.parametres['default_color']][0], #filled rows background
                        foreground=colors[self.parametres['default_color']][1], #text color
                        rowheight=25, #row height
                        fieldbackground=colors[self.parametres['default_color']][2] #empty rows background
                        )
        style.map('Treeview',
                  background = [('selected',GREY)]) #selected rows color

    #LOGS
    def Update_Logs_channel(self, text : str)->None:
        """
        sends text to logs channel and saves it in logs file
        """
        try:
            #checks if time is enabled
            if self.settings.get('enable_time') == True:
                text = f'[{self.get_time()}] {text}'
            #writes text into the file
            with open(f'LOGS//{self.settings.get('Logs_file')}', 'a') as file:
                file.write(text)
            #sends message to logs textbox
            self.c_output.configure(state='normal')
            self.c_output.insert('0.0', text)
            self.c_output.configure(state='disabled')
        except AttributeError:
            pass

    def Open_Logs_channel(self)->None:
        """
        loads all messages in logs file and paste them to command prompt's textbox
        """
        self.c_output.configure(state='normal')
        with open(f'LOGS//{self.settings.get('Logs_file')}', 'r') as file:
            #clears logs file if it exceeds 50_000 bytes
            if os.stat(f'LOGS//{self.settings.get('Logs_file')}').st_size > 50_000:
                open(f'LOGS//{self.settings.get('Logs_file')}', 'w').close()
            #inserts messages to cmd
            for line in file:
                self.c_output.insert('0.0',line)
        self.c_output.configure(state='disabled')
    
    def create_Log_message(self, **kargs)->None:
        """
        forms the message sent in logs channel
        arguments:
        >>> event: which event caused the method to be called
        >>> key: specific function that needs to be reported
        >>> sign: 'positive' if no error occurred, 'negative' if an error occurred
        >>> text: text added with the message
        """
        message = ''
        match kargs.get('event'):
            case 'debug':
                message = 'we are heeereee \n'
            case 'custom':
                message = kargs.get('text') + '\n'
            case 'command error':
                message = 'invalid command \n'
            case 'data':
                match kargs.get('sign'):
                    case 'positive':
                        message = self.get_file_data()
                    case 'negative':
                        message = 'no data available.\n'
            case 'cd':
                message = kargs.get('text') + '\n'
            case 'color':
                message = kargs.get('text') + '\n'
            case 'mode':
                match kargs.get('sign'):
                    case 'positive':
                        message = f'changed to {kargs.get('text')} mode.\n'
                    case 'negative':
                        message = f'{kargs.get('text')}\n' 
            case 'time':
                message = f'show time is set to {kargs.get('text')}\n'
            case 'type':
                message = f'file type: {kargs.get('text')}\n'
            case 'file':
                match kargs.get('key'):
                    case 'save':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'succesfully saved in {kargs.get('text')}\n'
                            case 'negative':
                                message = f'couldn\'t save in {kargs.get('text')}\n'
                    case 'load':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'succesfully loaded the file {kargs.get('text')}\n'
                            case 'negative':
                                message = f'couldn\'t load the file {kargs.get('text')}\n'
            case 'config':
                match kargs.get('key'):
                    case 'row':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'rowid {kargs.get('text')} selected\n'
                            case 'negative':
                                message = f'rowid {kargs.get('text')} out of range\n'
                    case 'column':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'column {kargs.get('text')} selected\n'
                            case 'negative':
                                message = f'column {kargs.get('text')} out of range\n'
                    case 'value':
                        message = f'value updated to {kargs.get('text')}\n'
                    case 'addrow':
                        match kargs.get('sign'):
                            case 'positive':
                                if kargs.get('text') == '1':
                                    message = f'empty row was added\n'
                                else:
                                    message = f'{kargs.get('text')} rows were added\n'
                            case 'negative':
                                message = f'couldn\'t add row(s)\n'
                    case 'addcolumn':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'{kargs.get('text')} column was added\n'
                            case 'negative':
                                message = f'couldn\'t add column(s)\n'
                    case 'removerow':
                        match kargs.get('sign'):
                            case 'positive':
                                if kargs.get('text') == '1':
                                    message = f'empty row was added\n'
                                else:
                                    message = f'{kargs.get('text')} rows were removed\n'
                            case 'negative':
                                message = f'couldn\'t remove row(s)\n'
                    case 'removecolumn':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'{kargs.get('text')} column was removed\n'
                            case 'negative':
                                message = f'couldn\'t remove column(s)\n'
                    case 'replacecolumn':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'{kargs.get('text1')} index column was renamed to {kargs.get('text2')}\n'
                            case 'negative':
                                message = f'couldn\'t rename column\n'
                    case 'replace':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'{kargs.get('text1')} was replaced with {kargs.get('text2')} and {kargs.get('text3')} nodes affected\n'
                            case 'negative':
                                message = f'couldn\'t replace value\n'
            case 'knn':
                match kargs.get('key'):
                    case 'new_point':
                        match kargs.get('sign'):
                            case 'positive':
                                message = 'successfully added test coordinates\n'
                            case 'negative':
                                message = 'couldn\'t add test coordinates\n'
                    case 'base_point':
                        match kargs.get('sign'):
                            case 'positive':
                                message = 'successfully added base coordinates\n'
                            case 'negative':
                                message = 'couldn\'t add base coordinates, check if it contains a string or X,Y and C lengths\n'
                    case 'neighbor':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'number of considered neighbors changed to {kargs.get('text')}\n'
                            case 'negative':
                                message = 'couldn\'t modify variable\n'    
            case 'regression':
                match kargs.get('key'):
                    case 'X':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'added X coordinates array of length {len(kargs.get('text'))} elements\n'
                            case 'negative':
                                message = 'failed to add the array\n'
                    case 'Y':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'added Y coordinates array of length {len(kargs.get('text'))} elements\n'
                            case 'negative':
                                message = 'failed to add the array\n' 

                    case 'degree':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'degree set to {kargs.get('text')} \n'
                            case 'negative':
                                message = 'couldn\'t set degree\n'  
                    
                    case 'newX':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'added point {kargs.get('text')}\n'
                            case 'negative':
                                message = 'process failed\n'
                    
                    case 'newY':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'predicted Y point: {kargs.get('text')}\n'
                            case 'negative':
                                message = 'process failed\n'
                    
                    case 'rmse':
                        match kargs.get('sign'):
                            case 'positive':
                                message = f'sum of error per point: {kargs.get('text')}\n'
                            case 'negative':
                                message = 'process failed\n'
        self.Update_Logs_channel(message)

    #static
    def get_time(self) -> datetime: 
        """
        returns current date and time in string format
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def reset_UI(self)->None:
        """
        resets some widgets after updating theme
        """
        l = [self.main_frame,self.config_frame]
        for bruh in l:
            bruh.grid_forget()
            bruh.destroy()
        self.on_quit2()
        if not self.exitflagML:
            resetML = True
        else:
            resetML = False
        
        self.main_widget()
        self.configuration_frame()
        self.help_update('default')
        self.command_window()
        if not self.exitflag:
    
            self.on_quit()
            self.show_data_table()
        
        if resetML:

            self.quit_ML()
            self.plot_configure()
    
    def preview_message(self)->None:
        """
        inserts older messages when pressing arrow keys
        """
        self.c_input.delete(0, customtkinter.END)
        self.c_input.insert(0, self.memo[self.memo_index])

    def change_geo(self, x : int, y : int)->None:
        """
        changes the main window's geometry and updates expand button
        """
        self.geometry(f'{x}x{y}')
        if x<=300:
            
            self.parametres['extend_1'] = False

        elif x>300:
            self.parametres['extend_1'] = True
        self.UI_update_all()
   
    def update_textbox(self, box : customtkinter.CTkTextbox, text : str):
        box.configure(state='normal')
        box.delete('0.0', customtkinter.END)
        box.insert('0.0', text=text)
        box.configure(state='disabled')
    #forgot i had these getters
    def get_column(self, column_name) -> list: 
        column_values = []
        for id in self.tree.get_children():
            column_values.append(self.tree.item(id, "values")[self.tree["columns"].index(column_name)])
        return column_values
    
    def get_row(self, row_index) -> any: #get row
        print("get_children return value: ", self.tree.get_children())
        return self.tree.item(self.tree.get_children()[row_index], "values")

    def replace_placeholder(self):
        match self.readvalue:
            case 'single':
                self.column2.configure(placeholder_text='row id (index)')
                self.column3.configure(placeholder_text='column index|name')
                self.column7.configure(placeholder_text='row id (index)')
                self.column8.configure(placeholder_text='column index|name')
            case 'multiple':
                self.column2.configure(placeholder_text='row0:rowlast:step')
                self.column3.configure(placeholder_text='col0:lastcol:step')
                self.column7.configure(placeholder_text='row0:rowlast:step')
                self.column8.configure(placeholder_text='col0:lastcol:step')
                
class EntryPopup(ttk.Entry):
    def __init__(self, parent, iid, column, text, **kw):
        super().__init__(parent, **kw)
        self.tv = parent  # reference to parent window's treeview
        self.iid = iid  # row id
        self.column = column 

        self.insert(0, text) 
        self['exportselection'] = False  # Prevents selected text from being copied to  
                                         # clipboard when widget loses focus
        self.focus_force()  # Set focus to the Entry widget
        self.select_all()   # Highlight all text within the entry widget
        self.bind("<Return>", self.on_return) # Enter key bind
        self.bind("<Control-a>", self.select_all) # CTRL + A key bind
        self.bind("<Escape>", lambda *ignore: self.destroy()) # ESC key bind
        
    def on_return(self, event):
        '''Insert text into treeview, and delete the entry popup'''
        rowid = self.tv.focus()  # Find row id of the cell which was clicked
        vals = self.tv.item(rowid, 'values')  # Returns a tuple of all values from the row with id, "rowid"
        vals = list(vals)  # Convert the values to a list so it becomes mutable
        vals[self.column] = self.get()  # Update values with the new text from the entry widget
        self.tv.item(rowid, values=vals)  # Update the Treeview cell with updated row values
        self.destroy()  # Destroy the Entry Widget
        
    def select_all(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')
        return 'break' # returns 'break' to interrupt default key-bindings
    

if __name__ == '__main__':
    APP = app()
    APP.mainloop()
