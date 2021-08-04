import random
import os
import logging
import shutil
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from tkinter import scrolledtext
import tkinter.messagebox
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from tkinter.tix import *
import runpy
import riscv_config.checker as riscv_config
import riscv_config_gui.utils as utils
import riscv_config_gui.page2 as page2
from riscv_config_gui.widgets import *
import ruamel
from ruamel.yaml import YAML
import yaml as pyyaml
import re
yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.allow_unicode = True

    
global isa_checked_file
global ispec, w_dir, isa_yaml
global t1_var, t2_var, isa_var, user_spec_var, pmp_var, pa_var, s_xlen_var, h, T1, T2
global root




def nextPage():
    root.destroy()
    page2.gui_page2(os.path.abspath(isa_checked_file), w_dir)
    
def open_ispec():
   global ispec, isa_yaml
   ispec = filedialog.askopenfile(mode='r', filetypes=[('YAML Files', '*.yaml')])
   file = ispec.read()
   isa_yaml = yaml.load(file)
   isa_var.set(isa_yaml['hart0']['ISA'])
   if 'User_Spec_Version' in isa_yaml['hart0'].keys():
       user_spec_var.set( isa_yaml['hart0']['User_Spec_Version'] )
   if 'pmp_granularity' in isa_yaml['hart0'].keys():
       pmp_var.set(isa_yaml['hart0']['pmp_granularity'])
   if 'custom_exceptions' in isa_yaml['hart0'].keys():
       custom_e=[]
       for value in isa_yaml['hart0']['custom_exceptions']:
           custom_e.append(dict(value))
       t1_var.set(custom_e)
       button7_ttp = CreateToolTip(T1, custom_e)
   if 'custom_interrupts' in isa_yaml['hart0'].keys():
       custom_i=[]
       for value in isa_yaml['hart0']['custom_interrupts']:
           custom_i.append(dict(value))
       t2_var.set(custom_i)
       button7_ttp = CreateToolTip(T2, custom_i)
   pa_var.set(isa_yaml['hart0']['physical_addr_sz'])
   s_xlen_var.set(isa_yaml['hart0']['supported_xlen'][0])
   ispec.close()
   
   
    
def submit():
    global isa_checked_file
    isa_yaml['hart0']['ISA']=isa_var.get()
    if 'User_Spec_Version' in isa_yaml['hart0'].keys():
       isa_yaml['hart0']['User_Spec_Version']=user_spec_var.get()
    if 'pmp_granularity' in isa_yaml['hart0'].keys():
       isa_yaml['hart0']['pmp_granularity']=int(pmp_var.get())
    isa_yaml['hart0']['physical_addr_sz']=int(pa_var.get())
    isa_yaml['hart0']['supported_xlen'][0]=int(s_xlen_var.get())
    f=open(os.path.realpath(ispec.name), 'w')
    utils.dump_yaml(isa_yaml, f)
    isa_checked_file = riscv_config.check_isa_specs(os.path.realpath(ispec.name), w_dir, True)

def first_page(work_dir):
       global w_dir
       global t1_var, t2_var, isa_var, user_spec_var, pmp_var, pa_var, s_xlen_var, root, h, T1, T2
       w_dir=work_dir
       root = tk.Tk()
       root.title("RISCV-CONFIG")
       root.geometry('1000x1000')
       t1_var=tk.StringVar()
       t2_var=tk.StringVar()
       T1 = tk.Entry(root, textvariable = t1_var, width = 100)
       T2 = tk.Entry(root, textvariable = t2_var, width = 100)
       Label = tk.Label(root, text="Click the Button to browse the Files", font=('Georgia 13'))
       B=tk.Button(root, text="Browse", command=open_ispec, fg='red')

       label = tk.Label(root, text ="INITIAL YAML FIELDS ", font=("Arial", 16))
       a = tk.Label(root, text="ISA:", font=("Arial", 16))
       isa_var= tk.StringVar()
       isa=isa_var.get()
       entry1 = tk.Entry (root, textvariable = isa_var, font=('calibre',10,'normal'), width=50) 
       button1_ttp = CreateToolTip(a, \
	    ' Takes input a string representing the ISA supported by the implementation. All extension names '
	    ' (other than Zext) should be mentioned in upper-case. Z extensions should begin with an upper-case '
	    ' ''Z'' followed by lower-case extension name (without Camel casing) ')
       b = tk.Label(root, text="User_Spec_version:", font=("Arial", 16))
       user_spec_var= tk.StringVar()
       user_spec=user_spec_var.get()
       entry2 = tk.Entry (root, textvariable = user_spec_var, font=('calibre',10,'normal'))
       user_spec_var.set('2.3') 
       button2_ttp = CreateToolTip(b, \
	    ' Version number of User/Non-priveleged ISA specification as string.  ')

       c = tk.Label(root, text="supported_xlen:", font=("Arial", 16))
       s_xlen_var= tk.StringVar()
       s_xlen=s_xlen_var.get()
       entry3 = tk.Entry (root, textvariable = s_xlen_var, font=('calibre',10,'normal')) 
       button3_ttp = CreateToolTip(c, \
	    ' list of supported xlen on the target  ')
	    
       d = tk.Label(root, text="physical_addr_sz:", font=("Arial", 16))
       pa_var= tk.StringVar()
       pa=pa_var.get()
       entry4 = tk.Entry (root, textvariable = pa_var, font=('calibre',10,'normal')) 
       button4_ttp = CreateToolTip(d, \
	    ' size of the physical address  ')

       e = tk.Label(root, text="pmp_granularity:", font=("Arial", 16))
       pmp_var= tk.StringVar()
       pmp=pmp_var.get()
       entry5 = tk.Entry (root, textvariable = pmp_var, font=('calibre',10,'normal')) 
       button4_ttp = CreateToolTip(e, \
	    ' Granularity of pmps  ')
	    
       f = tk.Label(root, text="custom_exceptions:", font=("Arial", 16))
       button5_ttp = CreateToolTip(f, \
	    ' list of custom exceptions implemented  ')
       
	     
       g = tk.Label(root, text="custom_interrupts:", font=("Arial", 16))
       button5_ttp = CreateToolTip(g, \
	    ' list of custom interrupts implemented  ')
	 
       MyButton1 = tk.Button(root, text="Submit", width=10, command=submit)
       button5_ttp = CreateToolTip(MyButton1, \
	    ' To create the default input ISA yaml and then run in riscv-config package  ')
       Next = tk.Button(root, text="Next Page", command= nextPage)
       button6_ttp = CreateToolTip(Next, \
	    'Navigates to the next page with the csrs corresponding to the enabled extensions  ')
       label.grid(column=0, row=0)
       Label.grid(column=0, row=1)
       B.grid(column=1, row=1, sticky='NW')
       a.grid(column=0, row=2,sticky='NW')
       entry1.grid(column=1, row=2, sticky='NW')
       b.grid(column=0, row=3,sticky='NW')
       entry2.grid(column=1, row=3, sticky='NW')
       c.grid(column=0, row=4,sticky='NW')
       entry3.grid(column=1, row=4, sticky='NW')
       d.grid(column=0, row=5,sticky='NW')
       entry4.grid(column=1, row=5, sticky='NW')
       e.grid(column=0, row=6,sticky='NW')
       entry5.grid(column=1, row=6, sticky='NW')
       f.grid(column=0, row=7,sticky='NW')
				
       T1.grid(column=0, row=8,sticky='NW')
       g.grid(column=0, row=9,sticky='NW')
       T2.grid(column=0, row=10,sticky='NW')
       MyButton1.grid(column=1, row=11) 
       Next.grid(column=1, row=12)
       button = tk.Button(root, text="QUIT", fg="red", command=quit)
       button.grid(column=1, row=13)
       h = tk.scrolledtext.ScrolledText(root)
       h.grid(column=1, row=14)
       text_handler = TextHandler(h)
       # Add the handler to logger
       logger = logging.getLogger()
       logger.addHandler(text_handler)
       root.mainloop()
