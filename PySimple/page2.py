import os
import logging
import shutil
import PySimpleGUI as sg
import riscv_config.checker as riscv_config
import riscv_config.utils as utils
import ruamel
from ruamel.yaml import YAML
import yaml as pyyaml
import re
yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.allow_unicode = True
global ispec, wdir, isa_yaml, rvxlen
global csr_name, values, sub_field, window, console_frame
from collections import OrderedDict

def submit():
    isa_checked_file = riscv_config.check_isa_specs(ispec, wdir, True)
    
def update_fields():
   '''
    Function to update all changes done by the user'''
   for  k in list(set(isa_yaml['hart0'][csr_name].keys())-set(['rv32', 'rv64'])):
      if k in {'address', 'reset-val'}:
         isa_yaml['hart0'][csr_name][k]=int(values['-'+csr_name+'_'+k+'-'])
      else:
         isa_yaml['hart0'][csr_name][k]=values['-'+csr_name+'_'+k+'-']
   if sub_field ==[]:
      for k in list(set(isa_yaml['hart0'][csr_name][rvxlen].keys()) - set(['fields','accessible'])):
        update = values['-'+csr_name+'_'+k+'-']
        if k in {'msb', 'lsb'}:
           update = int(update)
        elif k == 'type':
           update=eval(update)
        elif update == '':
           update=None
        else:
           update = update
        isa_yaml['hart0'][csr_name][rvxlen][k]= update
   else:
     for sub in sub_field:
      for k in list(set(isa_yaml['hart0'][csr_name][rvxlen][sub].keys()) - set(['fields'])):
          update = values['-'+csr_name+'_'+sub+k+'-']
          if k in {'msb', 'lsb'}:
           update = int(update)
          elif k == 'type':
           update=eval(update)
          elif k == 'implemented':
            if update=='1':
              update=True
            else:
             update=False
          elif update == '':
           update=None
          else:
           update = update
          isa_yaml['hart0'][csr_name][rvxlen][sub][k]=update
   isa_yaml['hart0'][csr_name][rvxlen]['accessible']=values['-accessible_'+csr_name+'-']
   f=open(ispec, 'w')
   utils.dump_yaml(isa_yaml, f)
   
def inner(csr):
  global csr_name, sub_field
  csr_name=csr
  sub_field=list(set(isa_yaml['hart0'][csr][rvxlen].keys()) - set(['fields', 'msb', 'lsb', 'accessible', 'shadow', 'shadow_type','type']))
  if sub_field == [] :
     rr= [[sg.Text(k), sg.InputText(isa_yaml['hart0'][csr][rvxlen][k], key='-'+csr+'_'+k+'-', tooltip=str(isa_yaml['hart0'][csr][rvxlen][k])) ] for k in list(set(isa_yaml['hart0'][csr][rvxlen].keys()) - set(['fields', 'type', 'accessible'])) ]
     if 'type' in isa_yaml['hart0'][csr][rvxlen].keys():
        _type= [[sg.Text('type'), sg.InputText(eval(str(isa_yaml['hart0'][csr][rvxlen]['type']).replace('ordereddict','dict')), key='-'+csr+'_type-', tooltip=str(isa_yaml['hart0'][csr][rvxlen]['type'])) ]]
     else:
       _type=[[]]
  else:
    rr=[[sg.Column([[sg.Frame(sub, [[sg.Text(k), sg.InputText(isa_yaml['hart0'][csr][rvxlen][sub][k], key='-'+csr+'_'+sub+k+'-', tooltip=str(isa_yaml['hart0'][csr][rvxlen][sub][k])) ] for k in list(set(isa_yaml['hart0'][csr][rvxlen][sub].keys()) -set(['fields','type'])) ]+ [[sg.Text('type'), sg.InputText(eval(str(isa_yaml['hart0'][csr][rvxlen][sub]['type']).replace('ordereddict','dict')), key='-'+csr+'_'+sub+'type-', tooltip=str(isa_yaml['hart0'][csr][rvxlen][sub]['type'])) ]]) ]  for sub in sub_field] , pad=(0,0), scrollable=True, key = "Columnmmm", size=(400,500))]]
    _type= [[]]
  return [[sg.Text(k), sg.InputText(isa_yaml['hart0'][csr][k], key='-'+csr+'_'+k+'-', tooltip=str(isa_yaml['hart0'][csr][k])) ] for k in list(set(isa_yaml['hart0'][csr].keys())-set(['rv32', 'rv64'])) ] + rr +_type
         

def print_csrs(csr):
  ''' 
   To print required number of csrs '''
  
  col1 = sg.Column([[sg.Frame(csr, inner(csr))]], pad=(0,0), scrollable=True, key = "Column", size=(450,500))
  return  col1
        
def page1(csr):
    global values
    col3 = sg.Column([[sg.Frame('Actions:',
                            [[sg.Column([[sg.Checkbox('Accessible', default=True, key='-accessible_'+csr+'-'), sg.Button('Save'), ]],
                                        size=(450,45), pad=(0,0))]])]], pad=(0,0))
    col1=print_csrs(csr)
    layout=[[col1],
            [col3]]
    window = sg.Window('PAGE1', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Save':
           update_fields()
           window.close()
           
def index():
  global isa_yaml, rvxlen, console_frame
  with open(ispec, 'r') as file:
    isa_yaml = yaml.load(file)
    rvxlen= 'rv'+str(isa_yaml['hart0']['supported_xlen'][0])
  csr=[]
  for field in isa_yaml['hart0']:
       if isinstance(isa_yaml['hart0'][field], dict) and (isa_yaml['hart0'][field][rvxlen]['accessible']==True):
          csr.append(str(field))  
  csr.sort()
  col2=[[sg.Button(str(csr[(j*10)+(i+1)]), size=(12,0)) for i in range(0,10)] for j in range(0, int(len(csr)/10))]
  col5 = sg.Column([[sg.Frame('Actions:',
                            [[sg.Column([[sg.Button('Run in Riscv-Config'), sg.Button('Clear') ]],
                                        size=(450,45), pad=(0,0))]])]], pad=(0,0))
  layout=[[col2],
          [col5]]
  window1 = sg.Window('LIST OF CSRS', layout)
  while True:
      event, values = window1.read()
      if event == 'Run in Riscv-Config':
         submit()
      elif  event == 'Clear':
         window['-MLl-'].Update(' ')
      else:
         page1(str(event))
      if event == sg.WIN_CLOSED:
          break
      
      

def gui_page2(isa_spec, work_dir): 
    global pagenum
    global ispec, wdir
    ispec=isa_spec
    wdir=work_dir       
    index()
