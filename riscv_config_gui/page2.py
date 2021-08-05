import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter.font as font
import tkinter.messagebox
from tkinter.tix import *
from tkinter import scrolledtext
import logging
import ruamel
from riscv_config_gui.widgets import *
from ruamel.yaml import YAML
import yaml as pyyaml
import riscv_config_gui.utils as utils
import riscv_config.checker as riscv_config
import riscv_config_gui.riscv_config_gui as gui
import re
yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.allow_unicode = True

global entries, entry
entries=[]
global isa_yaml
global rvxlen
global pagenum, canvas, scrollbar
global checkvar
checkvar=[]
global check_s, check_n, check_u
global ispec, wdir, root


def cli():
    '''
     For a final run in riscv-config '''
    isa_file = riscv_config.check_isa_specs(ispec, wdir, True)
   

def subfields(label, field, cond, csr, subfield):
   '''
    Function to print all subfields of node '''
   global entries, entry
   for node,value in field.items():
       if eval(cond):
           label_name = tk.Label(label, text =str(node)+':', font=("Arial", 12))
           if str(node) in {'address', 'reset-val', 'lsb', 'msb'}:
              pa_var=tk.IntVar()
           else:
              pa_var= tk.StringVar()
           if str(node) == 'type':
             if 'warl' in value :
               value['warl']=dict(value['warl'])
               pa_var.set(dict(value))
             else:
               pa_var.set(dict(value))
           elif str(node) == 'implemented':
               pa_var.set(str(value))
           else:
             pa_var.set(value)
           entry4 = tk.Entry (label, textvariable = pa_var, font=('calibre',10,'normal'), width=20) 
           button1_ttp = CreateToolTip(entry4, str(value))
           label_name.pack()
           entry4.pack()
           entries.append([csr, subfield, str(node) , pa_var]) 
           
def update_fields():
   '''
    Function to update all changes done by the user'''
    
   global isa_yaml, rvxlen, entries, checkvar
   for entry in entries:
    csr, subfield, node, pa_var = entry
    update=pa_var.get()
    if node == 'type':
      update=eval(update)
    elif node == 'implemented':
       if update=='True':
          update=True
       else:
          update=False
    elif update == 'None':
         update=None
    if subfield != None:
       isa_yaml['hart0'][csr][rvxlen][subfield][node]=update
    elif subfield==None and node in {'description', 'priv_mode', 'reset-val', 'address'}:
       isa_yaml['hart0'][csr][node]=update
    else:
      isa_yaml['hart0'][csr][rvxlen][node]=update
   for var in checkvar:
       field, var1= var
       isa_yaml['hart0'][field][rvxlen]['accessible']=bool(var1.get())
   f=open(ispec, 'w')
   utils.dump_yaml(isa_yaml, f)


def print_csrs(scrollable_frame, n, m, priv_mode):
  ''' 
   To print required number of csrs '''
  global isa_yaml, rvxlen, checkvar, check_s
  with open(ispec, 'r') as file:
    isa_yaml = yaml.load(file)
    i=0
    p=0
    rvxlen= 'rv'+str(isa_yaml['hart0']['supported_xlen'][0])
    for field in isa_yaml['hart0'] :
     if isinstance(isa_yaml['hart0'][field], dict) and (isa_yaml['hart0'][field][rvxlen]['accessible']==True) and (isa_yaml['hart0'][field]['priv_mode']==priv_mode) :
      i+=1
      if (i>=n) and (i<m):
        label = tk.LabelFrame(scrollable_frame, text =str(field)+':', font=("Arial", 16), fg="blue")
        label.grid(row=0, column=p, sticky='N')
        var1 = tk.IntVar()
        var1.set(1)
        cb= tk.Checkbutton(label, text="accessible", variable=var1, onvalue=1, offvalue=0)
        cb.IntVar = var1
        checkvar.append([field, var1])
        cb.pack()
        sub_field=[]
        sub_field=list(set(isa_yaml['hart0'][field][rvxlen].keys()) - set(['fields', 'msb', 'lsb', 'accessible', 'shadow', 'shadow_type','type']))
        if sub_field != []:
          for sub in sub_field:
           label_sub = tk.LabelFrame(label, text =str(sub)+':', font=("Arial", 16))
           label_sub.pack(fill="both", expand=True)
           subfields(label_sub, isa_yaml['hart0'][field][rvxlen][sub], '1', str(field), str(sub)) #extra subfields like mxl
        else:
          subfields(label, isa_yaml['hart0'][field][rvxlen], ''' str(node) not in {'accessible', 'fields'} ''', str(field), None) #msb, lsb, shadow 
        subfields(label, isa_yaml['hart0'][field], ''' str(node) not in {'rv64', 'rv32'} ''', str(field), None) #reset, priv_mode
        p+=1

def page1(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 0, 10, 'M')
    tk.Button(scrollable_frame, text = 'Back to Home page', command = changetoprevpage).grid(row = 0, column=10, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 2', command = changepage).grid(row = 0, column=11, sticky='NW')        
    
    
def page2(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 10, 19, 'M')
    tk.Button(scrollable_frame, text = 'To prev page 1', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 3', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page3(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 19, 28, 'M')
    tk.Button(scrollable_frame, text = 'To prev page 2', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 4', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page4(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 28, 37, 'M')
    tk.Button(scrollable_frame, text = 'To prev page 3', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 5', command = changepage).grid(row = 0, column=10, sticky='NW')
    
    
def page5(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 37, 46, 'M')
    tk.Button(scrollable_frame, text = 'To prev page 4', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 6', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page6(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 46, 55, 'M')
    tk.Button(scrollable_frame, text = 'To prev page 5', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 7', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page7(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 55, 64, 'M')
    tk.Button(scrollable_frame, text = 'To prev page 6', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 8', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page8(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 64, 73, 'M')
    tk.Button(scrollable_frame, text = 'To prev page 7', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 9', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page9(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 73, 82, 'M')
    tk.Button(scrollable_frame, text = 'To prev page 8', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 10', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page10(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 0, 10, 'S')
    if not check_s and not check_u and not check_n:
       tk.Label(scrollable_frame, text='S, N and U extensions disabled, go to next page',font=("Arial", 18), fg='red').grid(row=1, column=1)
    tk.Button(scrollable_frame, text = 'To prev page 9', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 11', command = changepage).grid(row = 0, column=10, sticky='NW')
      

def page11(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 10, 19, 'S')
    if not check_s:
       tk.Label(scrollable_frame, text='Supervisor extension disabled, go to next page',font=("Arial", 18)).grid(row=1, column=1)
    tk.Button(scrollable_frame, text = 'To prev page 10', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 12', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page12(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 0, 10, 'U')
    if not check_u:
       tk.Label(scrollable_frame, text='User (U) extension disabled, go to next page',font=("Arial", 18), fg='red').grid(row=1, column=1)
    tk.Button(scrollable_frame, text = 'To prev page 11', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 13', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page13(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 10, 19, 'U')
    if not check_u:
       tk.Label(scrollable_frame, text='User (U) extension disabled, go to next page',font=("Arial", 18), fg='red').grid(row=1, column=1)
    tk.Button(scrollable_frame, text = 'To prev page 12', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 14', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page14(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 19, 28, 'U')
    if not check_u:
       tk.Label(scrollable_frame, text='User (U) extension disabled, go to next page',font=("Arial", 18), fg='red').grid(row=1, column=1)
    tk.Button(scrollable_frame, text = 'To prev page 13', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 15', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page15(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 28, 37, 'U')
    if not check_u:
       tk.Label(scrollable_frame, text='User (U) extension disabled, go to next page',font=("Arial", 18), fg='red').grid(row=1, column=1)
    tk.Button(scrollable_frame, text = 'To prev page 14', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    tk.Button(scrollable_frame, text = 'To page 16', command = changepage).grid(row = 0, column=10, sticky='NW')
    
def page16(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    print_csrs(scrollable_frame, 37, 46, 'U')
    if not check_n:
       tk.Label(scrollable_frame, text='User-level Interrupts(N) extension disabled',font=("Arial", 18), fg='red').grid(row=1, column=1)
    button = tk.Button(scrollable_frame, text="TO FINAL RUN PAGE", fg="red", command=changepage)
    tk.Button(scrollable_frame, text = 'Prev page 15', command = changetoprevpage).grid(row = 0, column=9, sticky='NW')
    button.grid(row=0, column=10, sticky='N')    
    
def page17(canvas):
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all") ))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw" )
    canvas.configure(yscrollcommand=scrollbar.set )
    h = tk.scrolledtext.ScrolledText(scrollable_frame, state='disabled')
    h.grid(column=1, row=0, sticky='NW')
    text_handler = TextHandler(h)
    # Add the handler to logger
    logger = logging.getLogger()
    logger.addHandler(text_handler)
    tk.Button(scrollable_frame, text = 'RUN \n IN \n RISCV-CONFIG', command = cli, fg='red', height=10).grid(row = 0, column=0, sticky='NW')
    

def changepage():
    global pagenum, canvas
    update_fields()
    for widget in canvas.winfo_children():
        widget.destroy()
    if pagenum == 1:
        page2(canvas)
        pagenum = 2
    elif pagenum==2 :
        page3(canvas)
        pagenum = 3
    elif pagenum==3:
        page4(canvas)
        pagenum = 4
    elif pagenum==4:
        page5(canvas)
        pagenum = 5
    elif pagenum==5:
        page6(canvas)
        pagenum = 6
    elif pagenum==6:
        page7(canvas)
        pagenum = 7
    elif pagenum==7:
        page8(canvas)
        pagenum = 8
    elif pagenum==8:
        page9(canvas)
        pagenum=9
    elif pagenum==9:
        page10(canvas)
        pagenum=10
    elif pagenum==10:
        page11(canvas)
        pagenum=11
    elif pagenum==11:
        page12(canvas)
        pagenum=12
    elif pagenum==12:
        page13(canvas)
        pagenum=13
    elif pagenum==13:
        page14(canvas)
        pagenum=14
    elif pagenum==14:
        page15(canvas)
        pagenum=15
    elif pagenum==15:
        page16(canvas)
        pagenum=16
    elif pagenum==16:
        page17(canvas)
        pagenum=17
 
 
def changetoprevpage():
    global pagenum, canvas
    for widget in canvas.winfo_children():
        widget.destroy()
    if pagenum==1:
       root.destroy()
       gui.first_page(wdir)
    if pagenum==2 :
        page1(canvas)
        pagenum = 1
    elif pagenum==3:
        page2(canvas)
        pagenum = 2
    elif pagenum==4:
        page3(canvas)
        pagenum = 3
    elif pagenum==5:
        page4(canvas)
        pagenum = 4
    elif pagenum==6:
        page5(canvas)
        pagenum = 5
    elif pagenum==7:
        page6(canvas)
        pagenum = 6
    elif pagenum==8:
        page7(canvas)
        pagenum=7
    elif pagenum==9:
        page8(canvas)
        pagenum=8
    elif pagenum==10:
        page9(canvas)
        pagenum=9
    elif pagenum==11:
        page10(canvas)
        pagenum=10
    elif pagenum==12:
        page11(canvas)
        pagenum=11
    elif pagenum==13:
        page12(canvas)
        pagenum=12
    elif pagenum==14:
        page13(canvas)
        pagenum=13
    elif pagenum==15:
        page14(canvas)
        pagenum=14
    elif pagenum==16:
        page15(canvas)
        pagenum=15
        
def gui_page2(isa_spec, work_dir): 
    global canvas, scrollbar, pagenum
    global ispec, wdir
    global check_s, check_n, check_u, root
    ispec=isa_spec
    wdir=work_dir       
    root = tk.Tk()
    root['bg']='#fff'
    container = tk.Frame(root)
    canvas = tk.Canvas(container)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    pagenum = 1
    page1(canvas)
    if 'S' in isa_yaml['hart0']['ISA']:
        check_s=True
    else:
        check_s=False
    if 'N' in isa_yaml['hart0']['ISA']:
        check_n=True
    else:
        check_n=False
    if 'U' in isa_yaml['hart0']['ISA']:
        check_u=True
    else:
        check_u=False
    container.pack(fill="both", expand=True)
    canvas.pack(side=tk.LEFT, fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    root.mainloop()
