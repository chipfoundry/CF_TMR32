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

        await self._all_directions_and_modes()
        await self._prescaler_sweep()
        await self._reload_and_tmr_ranges()
        await self._compare_match()
        await self._ctrl_combos()
        await self._pwm_actions_sweep()
        await self._pwm_enables()
        await self._pwm_inversion()
        await self._deadtime_sweep()
        await self._fault_handling()
        await self._irq_flags_and_masks()

    async def _w(self, name, reg, val):
        await write_reg_seq(name, self.addr[reg], val).start(self.sequencer)

    async def _r(self, name, reg):
        await read_reg_seq(name, self.addr[reg]).start(self.sequencer)

    async def _stop_timer(self):
        await self._w("ctrl_off", "CTRL", 0)

    async def _run_timer(self, direction, periodic, reload_val, prescaler=0,
                         cmpx=None, cmpy=None, p0e=0, p1e=0, dte=0,
                         pi0=0, pi1=0, cycles=None):
        """Configure and run the timer, then wait for it to count."""
        await self._stop_timer()
        await self._w("pr", "PR", prescaler)
        await self._w("reload", "RELOAD", reload_val)
        if cmpx is not None:
            await self._w("cmpx", "CMPX", cmpx)
        if cmpy is not None:
            await self._w("cmpy", "CMPY", cmpy)
        cfg = (direction & 0x3) | ((periodic & 0x1) << 2)
        await self._w("cfg", "CFG", cfg)
        ctrl = (
            0x03
            | (p0e << 2) | (p1e << 3)
            | (dte << 4) | (pi0 << 5) | (pi1 << 6)
        )
        await self._w("ctrl", "CTRL", ctrl)
        if cycles is None:
            cycles = max((prescaler + 1) * reload_val * 3, 30)
        await ClockCycles(self.dut.CLK, cycles)

    async def _all_directions_and_modes(self):
        """Sweep all 3 active count directions x periodic/oneshot = 6 mode bins,
        plus DIR=0 (no counting) for the direction coverpoint."""
        for d in [0, 1, 2, 3]:
            for p in [0, 1]:
                await self._run_timer(direction=d, periodic=p,
                                      reload_val=20, cmpx=7, cmpy=14)
                await self._r("cfg_rd", "CFG")
                await self._r("tmr_rd", "TMR")
                await self._r("ris_rd", "RIS")

    async def _prescaler_sweep(self):
        """Hit all PR bins: 0, (1-15), (16-255), (256-0xFFFF)."""
        for pr_val in [0, 5, 64, 500]:
            await self._run_timer(direction=2, periodic=1, reload_val=10,
                                  prescaler=pr_val)
            await self._r("pr_rd", "PR")
            await self._r("tmr_rd", "TMR")

    async def _reload_and_tmr_ranges(self):
        """Hit RELOAD and TMR register value-range bins:
        zero, byte, halfword, word."""
        for reload_val in [0, 100, 0x1234, 0x00100000]:
            await self._w("reload", "RELOAD", reload_val)
            await self._r("reload_rd", "RELOAD")

        for reload_val, pr, wait in [
            (200, 0, 250),
            (0xFFFF, 0, 50),
            (0x00100000, 0, 50),
        ]:
            await self._run_timer(direction=2, periodic=1,
                                  reload_val=reload_val, prescaler=pr,
                                  cycles=wait)
            await self._r("tmr_rd", "TMR")

    async def _compare_match(self):
        """Set CMPX/CMPY to values in each range bin and run the timer long
        enough that the compare match actually fires (MX/MY in RIS)."""
        test_cases = [
            (0, 0),
            (0x42, 0x80),
            (0x1234, 0x2000),
            (0x00050000, 0x00080000),
        ]
        for cx, cy in test_cases:
            await self._w("cmpx", "CMPX", cx)
            await self._r("cmpx_rd", "CMPX")
            await self._w("cmpy", "CMPY", cy)
            await self._r("cmpy_rd", "CMPY")

        for cx, cy in [(5, 15), (10, 18)]:
            await self._w("im", "IM", 0x7)
            await self._run_timer(direction=2, periodic=1, reload_val=20,
                                  cmpx=cx, cmpy=cy)
            await self._r("ris_match", "RIS")
            await self._w("icr", "ICR", 0x7)

    async def _ctrl_combos(self):
        """Sweep CTRL field combinations to hit all 1-bit field bins."""
        for val in range(128):
            await self._w("ctrl", "CTRL", val)
            await self._r("ctrl_rd", "CTRL")

    async def _pwm_actions_sweep(self):
        """Hit all 4 PWM action values for every event slot on both channels,
        running the timer so the actions actually fire."""
        for action in range(4):
            pwm_cfg = 0
            for evt in range(6):
                pwm_cfg |= (action << (evt * 2))
            await self._w("pwm0cfg", "PWM0CFG", pwm_cfg & 0xFFF)
            await self._r("pwm0cfg_rd", "PWM0CFG")
            await self._w("pwm1cfg", "PWM1CFG", pwm_cfg & 0xFFF)
            await self._r("pwm1cfg_rd", "PWM1CFG")

        mixed_configs = [
            0x02 | (0x01 << 2) | (0x03 << 4) | (0x02 << 6) | (0x01 << 8) | (0x03 << 10),
            0x03 | (0x02 << 2) | (0x01 << 4) | (0x03 << 6) | (0x02 << 8) | (0x01 << 10),
        ]
        for cfg in mixed_configs:
            await self._w("pwm0cfg", "PWM0CFG", cfg & 0xFFF)
            await self._r("pwm0cfg_rd", "PWM0CFG")
            await self._w("pwm1cfg", "PWM1CFG", cfg & 0xFFF)
            await self._r("pwm1cfg_rd", "PWM1CFG")
            await self._run_timer(direction=2, periodic=1, reload_val=20,
                                  cmpx=7, cmpy=14, p0e=1, p1e=1)

    async def _pwm_enables(self):
        """Hit all PWM enable combinations with the timer running."""
        for p0e in [0, 1]:
            for p1e in [0, 1]:
                await self._run_timer(direction=2, periodic=1, reload_val=20,
                                      cmpx=7, cmpy=14, p0e=p0e, p1e=p1e)
                await self._r("ctrl_rd", "CTRL")

    async def _pwm_inversion(self):
        """Hit all PWM inversion combinations."""
        for pi0 in [0, 1]:
            for pi1 in [0, 1]:
                await self._run_timer(direction=2, periodic=1, reload_val=20,
                                      cmpx=7, cmpy=14, p0e=1, p1e=1,
                                      pi0=pi0, pi1=pi1)
                await self._r("ctrl_rd", "CTRL")

    async def _deadtime_sweep(self):
        """Hit all deadtime value bins and exercise DTE enable/disable."""
        for dt_val in [0, 8, 64, 200]:
            await self._w("pwmdt", "PWMDT", dt_val)
            await self._r("pwmdt_rd", "PWMDT")

        for dte in [0, 1]:
            await self._run_timer(direction=2, periodic=1, reload_val=40,
                                  cmpx=10, cmpy=30, p0e=1, p1e=1, dte=dte)
            await self._r("ctrl_rd", "CTRL")

    async def _fault_handling(self):
        """Drive pwm_fault and exercise PWMFC register bins."""
        pwm0_cfg = 0x02 | (0x01 << 2)
        await self._w("pwm0cfg", "PWM0CFG", pwm0_cfg)
        await self._run_timer(direction=2, periodic=1, reload_val=50,
                              cmpx=15, cmpy=35, p0e=1, p1e=1)

        self.dut.pwm_fault.value = 1
        await ClockCycles(self.dut.CLK, 20)
        await self._r("tmr_fault", "TMR")

        await self._w("pwmfc", "PWMFC", 0xFFFF)
        await self._r("pwmfc_rd", "PWMFC")
        self.dut.pwm_fault.value = 0
        await ClockCycles(self.dut.CLK, 20)

        await self._w("pwmfc_zero", "PWMFC", 0)
        await self._r("pwmfc_rd2", "PWMFC")

        self.dut.pwm_fault.value = 1
        await ClockCycles(self.dut.CLK, 10)
        self.dut.pwm_fault.value = 0
        await ClockCycles(self.dut.CLK, 10)
        await self._w("pwmfc_clr", "PWMFC", 0x0001)
        await self._r("pwmfc_rd3", "PWMFC")

    async def _irq_flags_and_masks(self):
        """Hit all 8 IM mask combinations, and ensure all 3 RIS flags
        (TO, MX, MY) are observed as set."""
        for mask in range(8):
            await self._w("im", "IM", mask)
            await self._r("im_rd", "IM")

        await self._w("im", "IM", 0x7)
        await self._run_timer(direction=2, periodic=1, reload_val=20,
                              cmpx=5, cmpy=15)
        await self._r("ris_all", "RIS")
        await self._w("icr_all", "ICR", 0x7)

        for d in [1, 3]:
            await self._run_timer(direction=d, periodic=1, reload_val=20,
                                  cmpx=5, cmpy=15)
            await self._r("ris_dir", "RIS")
            await self._w("icr_dir", "ICR", 0x7)
