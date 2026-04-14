"""TMR32 IP monitor — watches pwm0, pwm1, and timer flag signals."""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Edge, Timer
from pyuvm import uvm_monitor, uvm_analysis_port, ConfigDB

from ip_item.tmr_item import tmr_item


class tmr_monitor(uvm_monitor):
    def build_phase(self):
        super().build_phase()
        self.ap = uvm_analysis_port("ap", self)
        self.dut = ConfigDB().get(self, "", "DUT")

    async def run_phase(self):
        cocotb.start_soon(self._watch_pwm0())
        cocotb.start_soon(self._watch_pwm1())

    async def _watch_pwm0(self):
        """Monitor PWM0 output transitions."""
        while True:
            try:
                await Edge(self.dut.pwm0)
            except Exception:
                await ClockCycles(self.dut.CLK, 1)
                continue
            await Timer(1, "ns")
            tr = tmr_item("pwm0_mon")
            tr.event_type = tmr_item.PWM_EVENT
            try:
                tr.pwm0_state = int(self.dut.pwm0.value)
            except Exception:
                tr.pwm0_state = 0
            try:
                tr.pwm1_state = int(self.dut.pwm1.value)
            except Exception:
                tr.pwm1_state = 0
            self.ap.write(tr)

    async def _watch_pwm1(self):
        """Monitor PWM1 output transitions."""
        while True:
            try:
                await Edge(self.dut.pwm1)
            except Exception:
                await ClockCycles(self.dut.CLK, 1)
                continue
            await Timer(1, "ns")
            tr = tmr_item("pwm1_mon")
            tr.event_type = tmr_item.PWM_EVENT
            try:
                tr.pwm0_state = int(self.dut.pwm0.value)
            except Exception:
                tr.pwm0_state = 0
            try:
                tr.pwm1_state = int(self.dut.pwm1.value)
            except Exception:
                tr.pwm1_state = 0
            self.ap.write(tr)
