"""TMR32 interrupt sequence — exercises TO, MX, MY interrupts and verifies IM/IC."""

from pyuvm import uvm_sequence, ConfigDB
from cocotb.triggers import ClockCycles

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq
from seq_lib.tmr_config_seq import tmr_config_seq


class tmr_interrupt_seq(uvm_sequence):
    async def body(self):
        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(None, "", "DUT")

        reload_val = 50
        cmpx_val = 15
        cmpy_val = 35
        pr = 0

        # Enable all 3 interrupts (TO=0, MX=1, MY=2)
        config = tmr_config_seq(
            "config", direction=2, periodic=1, prescaler=pr,
            reload=reload_val, cmpx=cmpx_val, cmpy=cmpy_val,
            te=1, ts=1, im=0x7,
        )
        await config.start(self.sequencer)

        # Wait for timer to count through one full period
        timer_cyc = (pr + 1) * (reload_val + 10)
        await ClockCycles(dut.CLK, timer_cyc)

        # Read RIS — should see MX and MY flags set
        await read_reg_seq("rd_ris", addr["RIS"]).start(self.sequencer)
        await read_reg_seq("rd_mis", addr["MIS"]).start(self.sequencer)

        # Clear MX (bit 1)
        if "IC" in addr:
            await write_reg_seq("ic_mx", addr["IC"], 0x2).start(self.sequencer)
        await read_reg_seq("rd_ris_mx", addr["RIS"]).start(self.sequencer)

        # Clear MY (bit 2)
        if "IC" in addr:
            await write_reg_seq("ic_my", addr["IC"], 0x4).start(self.sequencer)
        await read_reg_seq("rd_ris_my", addr["RIS"]).start(self.sequencer)

        # Clear TO (bit 0)
        if "IC" in addr:
            await write_reg_seq("ic_to", addr["IC"], 0x1).start(self.sequencer)
        await read_reg_seq("rd_ris_to", addr["RIS"]).start(self.sequencer)

        # Test individual mask bits
        for bit in range(3):
            await write_reg_seq("im_set", addr["IM"], 1 << bit).start(self.sequencer)
            await read_reg_seq("im_rd", addr["IM"]).start(self.sequencer)

        # Restore all interrupts
        await write_reg_seq("im_all", addr["IM"], 0x7).start(self.sequencer)
