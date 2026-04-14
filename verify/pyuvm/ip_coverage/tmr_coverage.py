"""TMR32 coverage component — samples both auto-generated and custom coverage."""

from pyuvm import ConfigDB

from cf_verify.ip_env.ip_coverage import ip_coverage
from ip_coverage.tmr_cov_groups import tmr_cov_groups
from ip_item.tmr_item import tmr_item


class tmr_coverage(ip_coverage):
    def build_phase(self):
        super().build_phase()
        regs = ConfigDB().get(None, "", "bus_regs")
        self.cov_groups = tmr_cov_groups("top.ip", regs)

    def sample(self, tr):
        if isinstance(tr, tmr_item):
            self.cov_groups.sample(tr)
        else:
            self.cov_groups.sample_bus(tr)
