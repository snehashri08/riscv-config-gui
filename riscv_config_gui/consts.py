const1 = """hart_ids: [0]
hart0:
    custom_exceptions: 
{0}
    custom_interrupts: 
{1}
    ISA: {2}
    User_Spec_Version: {3} 
    pmp_granularity: {4}
    physical_addr_sz: {5}
    supported_xlen: 
     - {6}
   
    """
    
    
custom_exceptions = """      - cause_val: 25
        cause_name: halt_ebreak
        priv_mode: M
      - cause_val: 26
        cause_name: halt_trigger
        priv_mode: M
      - cause_val: 28
        cause_name: halt_step
        priv_mode: M
      - cause_val: 29
        cause_name: halt_reset
        priv_mode: M"""
        
        
custom_interrupts = """      - cause_val: 16
        cause_name: debug_interrupt
        on_reset_enable: 1
        priv_mode : M   """
