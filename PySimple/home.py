import random
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
import page2 as page2
yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.allow_unicode = True

global ispec, isa_yaml, isa_checked_file
sg.theme('DarkGreen3')

def nextPage():
    window.close()
    page2.gui_page2(os.path.abspath(isa_checked_file), work_dir)
    
def open_ispec():
   global ispec, isa_yaml
   f1 = values['-file1-']
   ispec =open(f1, 'rb')
   file = ispec.read()
   isa_yaml = yaml.load(file)
   window['-ISA-'].update(isa_yaml['hart0']['ISA'])
   if 'User_Spec_Version' in isa_yaml['hart0'].keys():
      window['-USER_SPEC-'].update( isa_yaml['hart0']['User_Spec_Version'] )
   if 'pmp_granularity' in isa_yaml['hart0'].keys():
       window['-PMP-'].update(isa_yaml['hart0']['pmp_granularity'])
   window['-PA_SZ-'].update(isa_yaml['hart0']['physical_addr_sz'])
   window['-XLEN-'].update(isa_yaml['hart0']['supported_xlen'][0])
   ispec.close()
   
def submit():
    global isa_checked_file
    isa_yaml['hart0']['ISA']=values['-ISA-']
    if 'User_Spec_Version' in isa_yaml['hart0'].keys():
       isa_yaml['hart0']['User_Spec_Version']=values['-USER_SPEC-']
    if 'pmp_granularity' in isa_yaml['hart0'].keys():
       isa_yaml['hart0']['pmp_granularity']=int(values['-PMP-'])
    isa_yaml['hart0']['physical_addr_sz']=int(values['-PA_SZ-'])
    isa_yaml['hart0']['supported_xlen'][0]=int(values['-XLEN-'])
    f=open(os.path.realpath(ispec.name), 'w')
    utils.dump_yaml(isa_yaml, f)
    isa_checked_file = riscv_config.check_isa_specs(os.path.realpath(ispec.name), work_dir, True)
   
col2 = sg.Column([[sg.Frame('To Enter Input ISA Yaml:', [[sg.Text('File 1', size=(15, 1)), sg.InputText(key='-file1-'),
                                                          sg.FileBrowse(size=(10, 1), file_types=(("YAML files", "*.yaml"),))],
                                                          [sg.Button('Fill Fields')]],size=(150,400))]],pad=(0,0))

col1 = sg.Column(
    # Information sg.Frame
    [[sg.Frame('Input ISA Yaml fields:', [[sg.Text(), sg.Column([[sg.Text('ISA:', tooltip=' Takes input a string representing the ISA supported by the implementation. All extension names '
	                                                                                   ' (other than Zext) should be mentioned in upper-case. Z extensions should begin with an upper-case '
                                                                                    	    ' ''Z'' followed by lower-case extension name (without Camel casing) ')],
                             [sg.Input( key='-ISA-', size=(19,1))],
                             [sg.Text('User_Spec_Version:', tooltip='Version number of User/Non-priveleged ISA specification as string.  ')],
                             [sg.Input('2.3', key='-USER_SPEC-', size=(19,1))],
                             [sg.Text('supported_xlen:', tooltip=' list of supported xlen on the target  ')],
                             [sg.Input(key='-XLEN-', size=(19,1))],
                             [sg.Text('physical_addr_sz:', tooltip=' size of the physical address  ')],
                             [sg.Input(key='-PA_SZ-', size=(19,1))],
                             [sg.Text('pmp_granularity:', tooltip='Granularity of pmps')],
                             [sg.Input(key='-PMP-', size=(19,1))]
                             ], size=(235,350), pad=(0,0))]])]], pad=(0,0))

col3 = sg.Column([[sg.Frame('Actions:',
                            [[sg.Column([[sg.Button('Run in Riscv-Config'), sg.Button('Clear'), sg.Button('Next Page'), ]],
                                        size=(450,45), pad=(0,0))]])]], pad=(0,0))
# The final layout is a simple one
layout = [[col2],
          [col1],
          [col3]]

# A perhaps better layout would have been to use the vtop layout helpful function.
# This would allow the col2 column to have a different height and still be top aligned
# layout = [sg.vtop([col1, col2]),
#           [col3]]

parser = utils.riscv_config_cmdline_args()
args = parser.parse_args()
utils.setup_logging(args.verbose)
logger = logging.getLogger()
logger.handlers = []
ch = logging.StreamHandler()
ch.setFormatter(utils.ColoredFormatter())
logger.addHandler(ch)
fh = logging.FileHandler('run.log', 'w')
logger.addHandler(fh)
work_dir = os.path.join(os.getcwd(), args.work_dir)
if not os.path.exists(work_dir):
   logger.debug('Creating new work directory: ' + work_dir)
   os.mkdir(work_dir)


window = sg.Window('RISCV-CONFIG', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event=='Fill Fields':
       open_ispec()
    if event == 'Run in Riscv-Config':
       submit()
    if event == 'Next Page':
       nextPage()
    if  event == 'Clear':
       window['-ML-'].Update(' ')
window.close()
