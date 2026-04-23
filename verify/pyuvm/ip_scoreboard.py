"""TMR32 scoreboard — compares PWM outputs and timeout events against expectations."""

from cf_verify.base.scoreboard import scoreboard
from ip_item.tmr_item import tmr_item


class tmr_scoreboard(scoreboard):
    def build_phase(self):
        super().build_phase()
        self.check_count = 0
        self._prev_pwm0 = 0
        self._prev_pwm1 = 0

    async def _compare_ip(self):
        """Compare PWM and timer events from DUT monitor against reference."""
        while True:
            dut_tr = await self.ip_dut_fifo.get()
            ref_tr = await self.ip_ref_fifo.get()

            self.logger.debug(
                f"TMR32 SB: event={dut_tr.event_type} "
                f"tmr=0x{dut_tr.timer_value:08x} "
                f"pwm0={dut_tr.pwm0_state} pwm1={dut_tr.pwm1_state} "
                f"TO={dut_tr.timeout} MX={dut_tr.matchx} MY={dut_tr.matchy}"
            )

            self._check("IP", dut_tr, ref_tr)
            self.check_count += 1

    def check_phase(self):
        assert self.failed == 0, (
            f"TMR32 scoreboard mismatches: failed={self.failed}, passed={self.passed}"
        )

    def report_phase(self):
        self.logger.info(
            f"TMR32 Scoreboard: {self.check_count} events checked, "
            f"passed={self.passed}, failed={self.failed}"
        )
