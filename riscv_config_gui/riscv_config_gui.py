import random
import os
import logging
import shutil
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from tkinter import scrolledtext
import tkinter.messagebox
from tkinter.tix import *
import runpy
import riscv_config.checker as riscv_config
import riscv_config_gui.utils as utils
import riscv_config_gui.page2 as page2
from riscv_config_gui.consts import *
from riscv_config_gui.widgets import *

    
global isa_file
global ispec, w_dir
global T1, T2, isa_var, user_spec_var, pmp_var, pa_var, s_xlen_var, h
global root




def nextPage():
    root.destroy()
    page2.gui_page2(os.path.abspath(isa_file), w_dir)
    
def submit():
    global isa_file
    f = open(ispec, "w")
    yaml_str=''
    yaml_str+=const1.format( T1.get(1.0, "end-1c"), T2.get(1.0, "end-1c"), isa_var.get(), "'"+user_spec_var.get()+"'", pmp_var.get(), pa_var.get(), s_xlen_var.get())
    f.write(yaml_str)
    f.close()
    isa_file = riscv_config.check_isa_specs(os.path.realpath(f.name), w_dir, True)

def first_page(isa_spec, work_dir):
       global ispec, w_dir
       global T1, T2, isa_var, user_spec_var, pmp_var, pa_var, s_xlen_var, root, h
       ispec=isa_spec
       w_dir=work_dir
       root = tk.Tk()
       root.title("RISCV-CONFIG")
       root.geometry('1000x1000')
       T1 = tk.Text(root, height = 12, width = 52)
       T2 = tk.Text(root, height = 4, width = 52)
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
       a.grid(column=0, row=1,sticky='NW')
       entry1.grid(column=1, row=1, sticky='NW')
       b.grid(column=0, row=2,sticky='NW')
       entry2.grid(column=1, row=2, sticky='NW')
       c.grid(column=0, row=3,sticky='NW')
       entry3.grid(column=1, row=3, sticky='NW')
       d.grid(column=0, row=4,sticky='NW')
       entry4.grid(column=1, row=4, sticky='NW')
       e.grid(column=0, row=5,sticky='NW')
       entry5.grid(column=1, row=5, sticky='NW')
       f.grid(column=0, row=6,sticky='NW')

				
       T1.insert(tk.END, custom_exceptions)
       T1.grid(column=0, row=7,sticky='NW')

       g.grid(column=0, row=8,sticky='NW')

				
       T2.insert(tk.END, custom_interrupts)
       T2.grid(column=0, row=9,sticky='NW')
       MyButton1.grid(column=1, row=10) 
       Next.grid(column=1, row=11)
       button = tk.Button(root, text="QUIT", fg="red", command=quit)
       button.grid(column=1, row=12)
       h = tk.scrolledtext.ScrolledText(root)
       h.grid(column=1, row=13)
       text_handler = TextHandler(h)
       # Add the handler to logger
       logger = logging.getLogger()
       logger.addHandler(text_handler)
       root.mainloop()
