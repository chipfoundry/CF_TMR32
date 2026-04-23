"""TMR32 deadtime sequence — configures PWM deadtime and verifies insertion."""

from pyuvm import uvm_sequence, ConfigDB
from cocotb.triggers import ClockCycles

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq
from seq_lib.tmr_config_seq import tmr_config_seq


class tmr_deadtime_seq(uvm_sequence):
    async def body(self):
        await reset_seq("rst").start(self.sequencer)

        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(None, "", "DUT")

        reload_val = 200
        cmpx_val = 60
        cmpy_val = 140
        pr = 0

        # PWM0: set high at zero, low at CMPX
        pwm0_cfg = 0x02 | (0x01 << 2)
        # PWM1: set high at zero, low at CMPY
        pwm1_cfg = 0x02 | (0x01 << 4)

        for dt_val in [0, 5, 20, 50, 128]:
            config = tmr_config_seq(
                "config", direction=2, periodic=1, prescaler=pr,
                reload=reload_val, cmpx=cmpx_val, cmpy=cmpy_val,
                te=1, ts=1, p0e=1, p1e=1, dte=1,
            )
            await config.start(self.sequencer)

            await write_reg_seq("wr_pwm0cfg", addr["PWM0CFG"], pwm0_cfg).start(
                self.sequencer)
            await write_reg_seq("wr_pwm1cfg", addr["PWM1CFG"], pwm1_cfg).start(
                self.sequencer)
            await write_reg_seq("wr_pwmdt", addr["PWMDT"], dt_val).start(
                self.sequencer)

            timer_cyc = (pr + 1) * reload_val * 3
            await ClockCycles(dut.CLK, timer_cyc)

            await read_reg_seq("rd_tmr", addr["TMR"]).start(self.sequencer)
            await read_reg_seq("rd_pwmdt", addr["PWMDT"]).start(self.sequencer)
