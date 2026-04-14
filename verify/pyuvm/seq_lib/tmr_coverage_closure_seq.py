"""TMR32 coverage closure — systematically hits all remaining coverage bins."""

from pyuvm import uvm_sequence, ConfigDB
from cocotb.triggers import ClockCycles

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, read_reg_seq


class tmr_coverage_closure_seq(uvm_sequence):
    async def body(self):
        regs = ConfigDB().get(None, "", "bus_regs")
        self.addr = regs.reg_name_to_address
        self.dut = ConfigDB().get(None, "", "DUT")

        if "GCLK" in self.addr:
            await self._w("gclk", "GCLK", 1)

        await self._all_directions()
        await self._all_modes()
        await self._ctrl_combos()
        await self._prescaler_sweep()
        await self._compare_ranges()
        await self._pwm_enables()
        await self._pwm_actions()
        await self._pwm_inversion()
        await self._deadtime_sweep()
        await self._irq_masks()

    async def _w(self, name, reg, val):
        await write_reg_seq(name, self.addr[reg], val).start(self.sequencer)

    async def _r(self, name, reg):
        await read_reg_seq(name, self.addr[reg]).start(self.sequencer)

    async def _all_directions(self):
        """Hit all direction bins: 0(none), 1(down), 2(up), 3(updown)."""
        for d in [0, 1, 2, 3]:
            await self._w("ctrl_off", "CTRL", 0)
            await self._w("pr", "PR", 0)
            await self._w("reload", "RELOAD", 20)
            cfg = d & 0x3
            await self._w("cfg", "CFG", cfg)
            await self._r("cfg_rd", "CFG")
            ctrl = 0x03  # TE + TS
            await self._w("ctrl", "CTRL", ctrl)
            await ClockCycles(self.dut.CLK, 30)
            await self._r("tmr", "TMR")
            await self._r("ris", "RIS")

    async def _all_modes(self):
        """Hit all 6 timer mode bins (dir x periodic)."""
        for d in [1, 2, 3]:
            for p in [0, 1]:
                await self._w("ctrl_off", "CTRL", 0)
                await self._w("pr", "PR", 0)
                await self._w("reload", "RELOAD", 20)
                cfg = (d & 0x3) | ((p & 0x1) << 2)
                await self._w("cfg", "CFG", cfg)
                await self._r("cfg_rd", "CFG")
                ctrl = 0x03  # TE + TS
                await self._w("ctrl", "CTRL", ctrl)
                await ClockCycles(self.dut.CLK, 40)
                await self._r("tmr", "TMR")
                await self._r("ris", "RIS")

    async def _ctrl_combos(self):
        """Sweep CTRL field combinations for all 1-bit fields."""
        for val in range(128):
            await self._w("ctrl", "CTRL", val)
            await self._r("ctrl_rd", "CTRL")

    async def _prescaler_sweep(self):
        """Hit all PR bins: 0, (1-3), (4-15), (16-63), (64-255), (256-65535)."""
        for pr_val in [0, 2, 8, 32, 128, 1000]:
            await self._w("ctrl_off", "CTRL", 0)
            await self._w("pr", "PR", pr_val)
            await self._r("pr_rd", "PR")
            await self._w("cfg", "CFG", 0x06)  # up + periodic
            await self._w("reload", "RELOAD", 10)
            await self._w("ctrl", "CTRL", 0x03)
            wait = max((pr_val + 1) * 15, 20)
            await ClockCycles(self.dut.CLK, wait)
            await self._r("tmr", "TMR")

    async def _compare_ranges(self):
        """Hit all CMPX/CMPY range bins: zero, byte, halfword, word."""
        for val in [0, 0x42, 0x1234, 0x12345678]:
            await self._w("cmpx", "CMPX", val)
            await self._r("cmpx_rd", "CMPX")
            await self._w("cmpy", "CMPY", val)
            await self._r("cmpy_rd", "CMPY")

    async def _pwm_enables(self):
        """Hit all PWM enable combinations."""
        for p0e in [0, 1]:
            for p1e in [0, 1]:
                ctrl = 0x01 | (p0e << 2) | (p1e << 3)
                await self._w("ctrl", "CTRL", ctrl)
                await self._r("ctrl_rd", "CTRL")

    async def _pwm_actions(self):
        """Hit all 4 PWM action values (no_action, low, high, invert) for each event."""
        for action in [0, 1, 2, 3]:
            pwm0_cfg = 0
            pwm1_cfg = 0
            for evt in range(6):
                pwm0_cfg |= (action << (evt * 2))
                pwm1_cfg |= (action << (evt * 2))
            await self._w("pwm0cfg", "PWM0CFG", pwm0_cfg & 0xFFF)
            await self._r("pwm0cfg_rd", "PWM0CFG")
            await self._w("pwm1cfg", "PWM1CFG", pwm1_cfg & 0xFFFF)
            await self._r("pwm1cfg_rd", "PWM1CFG")

    async def _pwm_inversion(self):
        """Hit all PWM inversion combinations."""
        for pi0 in [0, 1]:
            for pi1 in [0, 1]:
                ctrl = 0x01 | (pi0 << 5) | (pi1 << 6)
                await self._w("ctrl", "CTRL", ctrl)
                await self._r("ctrl_rd", "CTRL")

    async def _deadtime_sweep(self):
        """Hit all deadtime bins: zero, tiny, small, medium, large."""
        for dt_val in [0, 3, 15, 64, 200]:
            await self._w("pwmdt", "PWMDT", dt_val)
            await self._r("pwmdt_rd", "PWMDT")

        # DTE enable/disable
        for dte in [0, 1]:
            ctrl = 0x01 | (dte << 4)
            await self._w("ctrl", "CTRL", ctrl)
            await self._r("ctrl_rd", "CTRL")

    async def _irq_masks(self):
        """Hit all 8 IM mask combinations."""
        for mask in range(8):
            await self._w("im", "IM", mask)
            await self._r("im_rd", "IM")
