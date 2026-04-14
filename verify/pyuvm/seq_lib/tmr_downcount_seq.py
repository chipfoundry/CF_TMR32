"""TMR32 down-count sequence — configures down counting and verifies timer reaches zero."""

from pyuvm import uvm_sequence, ConfigDB
from cocotb.triggers import ClockCycles

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq
from seq_lib.tmr_config_seq import tmr_config_seq


class tmr_downcount_seq(uvm_sequence):
    async def body(self):
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(None, "", "DUT")

        reload_val = 50
        pr = 0

        config = tmr_config_seq(
            "config", direction=1, periodic=1, prescaler=pr,
            reload=reload_val, te=1, ts=1,
        )
        await config.start(self.sequencer)

        timer_cyc = (pr + 1) * (reload_val + 10)
        await ClockCycles(dut.CLK, timer_cyc)

        await read_reg_seq("rd_tmr", addr["TMR"]).start(self.sequencer)
        await read_reg_seq("rd_ris", addr["RIS"]).start(self.sequencer)

        if "IC" in addr:
            await write_reg_seq("ic_clear", addr["IC"], 0x7).start(self.sequencer)

        await ClockCycles(dut.CLK, timer_cyc)
        await read_reg_seq("rd_tmr2", addr["TMR"]).start(self.sequencer)
        await read_reg_seq("rd_ris2", addr["RIS"]).start(self.sequencer)
