"""TMR32 coverage groups — auto-generated + timer/PWM-specific custom coverage."""

from cocotb_coverage.coverage import CoverPoint, CoverCross

from cf_verify.coverage.auto_coverage import generate_coverage_from_yaml
from cf_verify.bus_env.bus_item import bus_item
from ip_item.tmr_item import tmr_item

TMR_FIELD_BINS = {
    ("TMR", None): [(0, 0), (1, 0xFFFFFFFF)],
    ("RELOAD", None): [(0, 0), (1, 0xFFFFFFFF)],
    ("PR", None): [(0, 0), (1, 0xFFFF)],
    ("CMPX", None): [(0, 0), (1, 0xFFFFFFFF)],
    ("CMPY", None): [(0, 0), (1, 0xFFFFFFFF)],
    ("CTRL", "TE"): [(0, 0), (1, 1)],
    ("CTRL", "TS"): [(0, 0), (1, 1)],
    ("CTRL", "P0E"): [(0, 0), (1, 1)],
    ("CTRL", "P1E"): [(0, 0), (1, 1)],
    ("CTRL", "DTE"): [(0, 0), (1, 1)],
    ("CTRL", "PI0"): [(0, 0), (1, 1)],
    ("CTRL", "PI1"): [(0, 0), (1, 1)],
    ("CFG", "DIR"): [(0, 0), (1, 1), (2, 2), (3, 3)],
    ("CFG", "P"): [(0, 0), (1, 1)],
    ("PWM0CFG", "E0"): [(0, 0), (1, 3)],
    ("PWM0CFG", "E1"): [(0, 0), (1, 3)],
    ("PWM0CFG", "E2"): [(0, 0), (1, 3)],
    ("PWM0CFG", "E3"): [(0, 0), (1, 3)],
    ("PWM0CFG", "E4"): [(0, 0), (1, 3)],
    ("PWM0CFG", "E5"): [(0, 0), (1, 3)],
    ("PWM1CFG", "E0"): [(0, 0), (1, 3)],
    ("PWM1CFG", "E1"): [(0, 0), (1, 3)],
    ("PWM1CFG", "E2"): [(0, 0), (1, 3)],
    ("PWM1CFG", "E3"): [(0, 0), (1, 3)],
    ("PWM1CFG", "E4"): [(0, 0), (1, 3)],
    ("PWM1CFG", "E5"): [(0, 0), (1, 3)],
    ("PWMDT", None): [(0, 0), (1, 255)],
    ("PWMFC", None): [(0, 0), (1, 0xFFFF)],
}


class tmr_cov_groups:
    def __init__(self, hierarchy, regs):
        self.hierarchy = hierarchy
        self.regs = regs

        self.auto_points = generate_coverage_from_yaml(
            regs, hierarchy,
            field_bins_override=TMR_FIELD_BINS,
            skip_crosses=True,
        )

        self.dir_cov = self._direction_coverage()
        self.mode_cov = self._mode_coverage()
        self.pwm_cov = self._pwm_coverage()
        self.irq_cov = self._irq_coverage()
        self.compare_cov = self._compare_coverage()
        self.deadtime_cov = self._deadtime_coverage()

        self._init_sample(None)

    def _init_sample(self, tr):
        """Cold-start: register all CoverPoints without actually counting."""
        @self._apply_decorators(
            self.auto_points + self.dir_cov + self.mode_cov
            + self.pwm_cov + self.irq_cov + self.compare_cov
            + self.deadtime_cov
        )
        def _cold(tr):
            pass

    def sample(self, tr):
        """Sample everything using a tmr_item."""
        @self._apply_decorators(
            self.auto_points + self.dir_cov + self.mode_cov
            + self.pwm_cov + self.irq_cov + self.compare_cov
            + self.deadtime_cov
        )
        def _s(tr):
            pass
        _s(tr)

    def sample_bus(self, tr):
        """Sample from bus transactions; update reg values for both reads and writes.

        For write-only registers, only update shadow from writes — hardware
        reads return 0 which would corrupt the shadow and prevent coverage
        from seeing the written values.
        """
        rname = self.regs._reg_address_to_name.get(tr.addr)
        if rname:
            if tr.kind == bus_item.WRITE:
                self.regs._reg_values[rname.lower()] = tr.data
            elif tr.kind == bus_item.READ:
                reg = next(
                    (r for r in self.regs._registers if r.name == rname),
                    None,
                )
                if not reg or reg.mode != "w":
                    self.regs._reg_values[rname.lower()] = tr.data

        @self._apply_decorators(
            self.auto_points + self.dir_cov + self.mode_cov
            + self.pwm_cov + self.irq_cov + self.compare_cov
            + self.deadtime_cov
        )
        def _bus(tr):
            pass
        _bus(tr)

    def _direction_coverage(self):
        """Cover all timer count directions: up, down, up/down."""
        return [CoverPoint(
            f"{self.hierarchy}.CountDirection",
            xf=lambda tr: self.regs.read_reg_value("CFG") & 0x3,
            bins=[0, 1, 2, 3],
            bins_labels=["none", "down", "up", "updown"],
            at_least=1,
        )]

    def _mode_coverage(self):
        """Cover periodic vs one-shot and direction cross."""
        return [
            CoverPoint(
                f"{self.hierarchy}.TimerMode",
                xf=lambda tr: (
                    self.regs.read_reg_value("CFG") & 0x3,
                    (self.regs.read_reg_value("CFG") >> 2) & 0x1,
                ),
                bins=[
                    (1, 0), (1, 1),
                    (2, 0), (2, 1),
                    (3, 0), (3, 1),
                ],
                bins_labels=[
                    "down_oneshot", "down_periodic",
                    "up_oneshot", "up_periodic",
                    "updown_oneshot", "updown_periodic",
                ],
                at_least=1,
            ),
        ]

    def _pwm_coverage(self):
        """Cover PWM enable states."""
        points = []
        points.append(CoverPoint(
            f"{self.hierarchy}.PWM_Enables",
            xf=lambda tr: (
                (self.regs.read_reg_value("CTRL") >> 2) & 0x1,
                (self.regs.read_reg_value("CTRL") >> 3) & 0x1,
            ),
            bins=[(0, 0), (0, 1), (1, 0), (1, 1)],
            bins_labels=["none", "pwm1_only", "pwm0_only", "both"],
            at_least=1,
        ))
        return points

    def _irq_coverage(self):
        """Cover interrupt flags: TO, MX, MY."""
        flags = [("TO", 0), ("MX", 1), ("MY", 2)]
        points = []
        for name, bit in flags:
            points.append(CoverPoint(
                f"{self.hierarchy}.IRQ.{name}",
                xf=lambda tr, b=bit: (self.regs.read_reg_value("RIS") >> b) & 1,
                bins=[0, 1], bins_labels=[f"no_{name}", name], at_least=1,
            ))
        points.append(CoverPoint(
            f"{self.hierarchy}.IRQ.Mask",
            xf=lambda tr: self.regs.read_reg_value("IM") & 0x7,
            bins=list(range(8)),
            bins_labels=[f"mask_{i:03b}" for i in range(8)],
            at_least=1,
        ))
        return points

    def _compare_coverage(self):
        """Covered by auto-generated reg.CMPX / reg.CMPY bins."""
        return []

    def _deadtime_coverage(self):
        """Covered by auto-generated reg.CTRL.DTE and reg.PWMDT bins."""
        return []

    @staticmethod
    def _apply_decorators(decorators):
        def wrapper(func):
            for dec in decorators:
                func = dec(func)
            return func
        return wrapper
