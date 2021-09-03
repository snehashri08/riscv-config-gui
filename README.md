RISCV-Config GUI
=================

RISC-V Configuration Validator GUI

LICENSE: BSD-3 Clause.

Latest Documentation of [RISCV-Config](<https://riscv-config.readthedocs.io/>).

To run the gui:
===============

https://user-images.githubusercontent.com/39543372/132003388-80be8c6f-7b97-4724-8cb5-b9c0e6c2fcdf.mp4

```
cd riscv-config-gui/PySimple
python3 -m riscv_config_gui.main 
```

1. First click on `Browse` to select the isa file, and then `Fill Fields` so that the entries in the gui are automatically filled.
2. You can now make appropriate changes in the home page, before clicking on `Run in Riscv-Config` which will reflect these changes and then run to produce the isa checked file.(riscv-config-gui/riscv_config_work/<isa_checked.yaml>)
3.  The logger output will be displayed in the terminal.
4. Next, you can proceed to click on `Next Page` to take you to the page where all the csrs corresponding to the ISA extensions you enabled , will be displayed as buttons.
5. You can now edit all fields of a csr by clicking on its button, and then press `Save` once you are done. It will automatically reflect all the values in the isa checked yaml. 
6. Click on `Run in Riscv-Config` to make sure all the changes you made compile with the RISC-V ISA Standards.

