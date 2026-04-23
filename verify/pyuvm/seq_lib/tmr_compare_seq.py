"""TMR32 compare-match sequence — tests CMPX/CMPY match detection and flags."""

from pyuvm import uvm_sequence, ConfigDB
from cocotb.triggers import ClockCycles

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq, reset_seq
from seq_lib.tmr_config_seq import tmr_config_seq


class tmr_compare_seq(uvm_sequence):
    async def body(self):
        await reset_seq("rst").start(self.sequencer)

        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(None, "", "DUT")

        reload_val = 100
        pr = 0

        for cmpx_val, cmpy_val in [(25, 75), (10, 90), (50, 50), (1, 99)]:
            config = tmr_config_seq(
                "config", direction=2, periodic=1, prescaler=pr,
                reload=reload_val, cmpx=cmpx_val, cmpy=cmpy_val,
                te=1, ts=1,
            )
            await config.start(self.sequencer)

            # Wait long enough for at least one full timer period
            timer_cyc = (pr + 1) * (reload_val + 20)
            await ClockCycles(dut.CLK, timer_cyc)

            await read_reg_seq("rd_tmr", addr["TMR"]).start(self.sequencer)
            await read_reg_seq("rd_ris", addr["RIS"]).start(self.sequencer)
            if "MIS" in addr:
                await read_reg_seq("rd_mis", addr["MIS"]).start(self.sequencer)

            # Clear interrupts
            if "IC" in addr:
                await write_reg_seq("ic_clear", addr["IC"], 0x7).start(self.sequencer)
            await read_reg_seq("rd_ris_clr", addr["RIS"]).start(self.sequencer)
