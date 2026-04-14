"""TMR32 IP driver — drives pwm_fault signal from sequence items."""

import cocotb
from cocotb.triggers import ClockCycles, Timer
from pyuvm import uvm_driver, ConfigDB

from ip_item.tmr_item import tmr_item


class tmr_driver(uvm_driver):
    def build_phase(self):
        super().build_phase()
        self.dut = ConfigDB().get(self, "", "DUT")

    async def run_phase(self):
        while True:
            item = await self.seq_item_port.get_next_item()
            self.logger.info(f"TMR driver got item: {item.convert2string()}")
            if item.event_type == tmr_item.FAULT_EVENT:
                self.dut.pwm_fault.value = item.pwm_fault
                await ClockCycles(self.dut.CLK, 2)
            self.seq_item_port.item_done()
