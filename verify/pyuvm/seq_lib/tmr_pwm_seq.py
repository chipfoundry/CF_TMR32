"""TMR32 PWM sequence — configures PWM outputs and verifies toggling."""

from pyuvm import uvm_sequence, ConfigDB
from cocotb.triggers import ClockCycles

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq
from seq_lib.tmr_config_seq import tmr_config_seq


class tmr_pwm_seq(uvm_sequence):
    async def body(self):
        await reset_seq("rst").start(self.sequencer)

        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(None, "", "DUT")

        reload_val = 100
        cmpx_val = 30
        cmpy_val = 70
        pr = 0

        # PWM0CFG: E0=high(10), E1=low(01), E3=invert(11)
        # E0 on zero match -> go high, E1 on CMPX match up -> go low
        pwm0_cfg = 0x02 | (0x01 << 2)
        # PWM1CFG: E0=high(10), E2=low(01)
        pwm1_cfg = 0x02 | (0x01 << 4)

        config = tmr_config_seq(
            "config", direction=2, periodic=1, prescaler=pr,
            reload=reload_val, cmpx=cmpx_val, cmpy=cmpy_val,
            te=1, ts=1, p0e=1, p1e=1,
        )
        await config.start(self.sequencer)

        await write_reg_seq("wr_pwm0cfg", addr["PWM0CFG"], pwm0_cfg).start(
            self.sequencer)
        await write_reg_seq("wr_pwm1cfg", addr["PWM1CFG"], pwm1_cfg).start(
            self.sequencer)

        # Run for several timer periods
        timer_cyc = (pr + 1) * reload_val * 4
        await ClockCycles(dut.CLK, timer_cyc)

        await read_reg_seq("rd_tmr", addr["TMR"]).start(self.sequencer)
        await read_reg_seq("rd_ris", addr["RIS"]).start(self.sequencer)
