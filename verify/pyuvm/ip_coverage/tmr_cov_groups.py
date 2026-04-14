"""TMR32 coverage groups — auto-generated register coverage + essential custom points."""

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

        self.custom_cov = self._custom_coverage()
        self._init_sample(None)

    def _init_sample(self, tr):
        @self._apply_decorators(self.auto_points + self.custom_cov)
        def _cold(tr):
            pass

    def sample(self, tr):
        @self._apply_decorators(self.auto_points + self.custom_cov)
        def _s(tr):
            pass
        _s(tr)

    def sample_bus(self, tr):
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

        @self._apply_decorators(self.auto_points + self.custom_cov)
        def _bus(tr):
            pass
        _bus(tr)

    def _custom_coverage(self):
        h = self.hierarchy
        regs = self.regs
        return [
            CoverPoint(
                f"{h}.CountDirection",
                xf=lambda tr: regs.read_reg_value("CFG") & 0x3,
                bins=[0, 1, 2, 3],
                bins_labels=["none", "down", "up", "updown"],
                at_least=1,
            ),
            CoverPoint(
                f"{h}.IRQ.TO",
                xf=lambda tr: (regs.read_reg_value("RIS") >> 0) & 1,
                bins=[0, 1],
                bins_labels=["no_TO", "TO"],
                at_least=1,
            ),
            CoverPoint(
                f"{h}.IRQ.MX",
                xf=lambda tr: (regs.read_reg_value("RIS") >> 1) & 1,
                bins=[0, 1],
                bins_labels=["no_MX", "MX"],
                at_least=1,
            ),
            CoverPoint(
                f"{h}.IRQ.MY",
                xf=lambda tr: (regs.read_reg_value("RIS") >> 2) & 1,
                bins=[0, 1],
                bins_labels=["no_MY", "MY"],
                at_least=1,
            ),
        ]

    @staticmethod
    def _apply_decorators(decorators):
        def wrapper(func):
            for dec in decorators:
                func = dec(func)
            return func
        return wrapper
