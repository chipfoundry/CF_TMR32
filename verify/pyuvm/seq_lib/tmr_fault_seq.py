"""TMR32 fault sequence — drives pwm_fault input and tests fault handling."""

from pyuvm import uvm_sequence, ConfigDB
from cocotb.triggers import ClockCycles

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq
from seq_lib.tmr_config_seq import tmr_config_seq


class tmr_fault_seq(uvm_sequence):
    async def body(self):
        await reset_seq("rst").start(self.sequencer)

        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(None, "", "DUT")

        reload_val = 100
        pr = 0

        # PWM0: set high at zero, low at CMPX
        pwm0_cfg = 0x02 | (0x01 << 2)

        config = tmr_config_seq(
            "config", direction=2, periodic=1, prescaler=pr,
            reload=reload_val, cmpx=30, cmpy=70,
            te=1, ts=1, p0e=1, p1e=1,
        )
        await config.start(self.sequencer)

        await write_reg_seq("wr_pwm0cfg", addr["PWM0CFG"], pwm0_cfg).start(
            self.sequencer)

        # Let PWM run normally for a while
        timer_cyc = (pr + 1) * reload_val * 2
        await ClockCycles(dut.CLK, timer_cyc)

        # Assert fault
        dut.pwm_fault.value = 1
        await ClockCycles(dut.CLK, 20)

        await read_reg_seq("rd_tmr_fault", addr["TMR"]).start(self.sequencer)

        # Clear fault
        await write_reg_seq("wr_pwmfc", addr["PWMFC"], 0xFFFF).start(
            self.sequencer)
        dut.pwm_fault.value = 0
        await ClockCycles(dut.CLK, 20)

        await read_reg_seq("rd_tmr_post", addr["TMR"]).start(self.sequencer)

        # Assert fault again with different clear pattern
        dut.pwm_fault.value = 1
        await ClockCycles(dut.CLK, 10)
        dut.pwm_fault.value = 0
        await ClockCycles(dut.CLK, 10)

        await write_reg_seq("wr_pwmfc2", addr["PWMFC"], 0x0001).start(
            self.sequencer)
        await ClockCycles(dut.CLK, timer_cyc)
        await read_reg_seq("rd_tmr_final", addr["TMR"]).start(self.sequencer)
