"""Test library for CF_TMR32 verification — 12 tests covering full timer/PWM functionality."""

import os
from pathlib import Path

import cocotb
import pyuvm
from pyuvm import uvm_root, ConfigDB

from cocotb.triggers import ClockCycles
from cocotb_coverage.coverage import coverage_db

from cf_verify.base.base_test import base_test
from cf_verify.base.top_env import top_env
from cf_verify.bus_env.bus_regs import BusRegs
from cf_verify.bus_env.bus_seq_lib import write_read_regs_seq, reset_seq
from cf_verify.ip_env.ip_agent import ip_agent
from cf_verify.ip_env.ip_driver import ip_driver
from cf_verify.ip_env.ip_monitor import ip_monitor
from cf_verify.ip_env.ip_coverage import ip_coverage

from ip_agent.tmr_driver import tmr_driver
from ip_agent.tmr_monitor import tmr_monitor
from ip_coverage.tmr_coverage import tmr_coverage


class tmr_env(top_env):
    """TMR32-specific top environment with proper component wiring."""

    def build_phase(self):
        from cf_verify.bus_env.bus_agent import bus_agent
        from cf_verify.ip_env.ip_logger import ip_logger
        from cf_verify.base.ref_model import ref_model

        self.bus_agent = bus_agent("bus_agent", self)
        self.ip_agent = tmr_ip_agent("ip_agent", self)
        self.ref_model = ref_model("ref_model", self)
        self.ip_coverage = tmr_coverage("ip_coverage", self)
        self.ip_logger = ip_logger("ip_logger", self)

    def connect_phase(self):
        super().connect_phase()
        self.bus_agent.monitor.ap.connect(self.ip_coverage.analysis_export)


class tmr_ip_agent(ip_agent):
    driver_cls = tmr_driver
    monitor_cls = tmr_monitor


class tmr_base_test(base_test):
    """Base test for CF_TMR32 — wires up the timer environment."""

    def build_phase(self):
        import os
        import cocotb

        dut = cocotb.top
        bus_type = os.environ.get("BUS_TYPE", "APB")
        yaml_file = os.environ.get(
            "YAML_FILE",
            str(Path(__file__).resolve().parent.parent.parent / "CF_TMR32.yaml"),
        )
        test_path = os.environ.get("TEST_PATH", "./sim")

        regs = BusRegs(yaml_file)

        ConfigDB().set(None, "*", "DUT", dut)
        ConfigDB().set(None, "*", "BUS_TYPE", bus_type)
        ConfigDB().set(None, "*", "bus_regs", regs)
        ConfigDB().set(None, "*", "irq_exist", regs.get_irq_exist())
        ConfigDB().set(None, "*", "collect_coverage", True)
        ConfigDB().set(None, "*", "disable_logger", False)
        ConfigDB().set(None, "*", "TEST_PATH", test_path)

        self.env = tmr_env("env", self)
        super().build_phase()


# ──────────────────────────────────────────
#  12 TMR32 TESTS
# ──────────────────────────────────────────

@pyuvm.test()
class WriteReadRegsTest(tmr_base_test):
    """Write/read all accessible registers."""

    async def run_phase(self):
        self.raise_objection()
        seq = write_read_regs_seq("write_read_regs")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class TimerUpCountTest(tmr_base_test):
    """Up counting — verifies timer counts from 0 to RELOAD."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_upcount_seq import tmr_upcount_seq
        seq = tmr_upcount_seq("upcount")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class TimerDownCountTest(tmr_base_test):
    """Down counting — verifies timer counts from RELOAD to 0."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_downcount_seq import tmr_downcount_seq
        seq = tmr_downcount_seq("downcount")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class TimerUpDownTest(tmr_base_test):
    """Up/Down counting — verifies timer counts up then down."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_config_seq import tmr_config_seq
        from cf_verify.bus_env.bus_seq_lib import read_reg_seq, write_reg_seq

        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(self, "", "DUT")

        config = tmr_config_seq(
            "config", direction=3, periodic=1, prescaler=0,
            reload=50, te=1, ts=1,
        )
        await config.start(self.env.bus_agent.sequencer)

        await ClockCycles(dut.CLK, 120)
        await read_reg_seq("rd_tmr", addr["TMR"]).start(self.env.bus_agent.sequencer)
        await read_reg_seq("rd_ris", addr["RIS"]).start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class OneShotTest(tmr_base_test):
    """One-shot mode — verifies timer stops after one count cycle."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_config_seq import tmr_config_seq
        from cf_verify.bus_env.bus_seq_lib import read_reg_seq, write_reg_seq

        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(self, "", "DUT")

        config = tmr_config_seq(
            "config", direction=2, periodic=0, prescaler=0,
            reload=30, te=1, ts=1,
        )
        await config.start(self.env.bus_agent.sequencer)

        # Wait for one-shot to complete
        await ClockCycles(dut.CLK, 50)
        await read_reg_seq("rd_tmr1", addr["TMR"]).start(self.env.bus_agent.sequencer)

        # Wait more — timer should remain stopped
        await ClockCycles(dut.CLK, 50)
        await read_reg_seq("rd_tmr2", addr["TMR"]).start(self.env.bus_agent.sequencer)
        await read_reg_seq("rd_ris", addr["RIS"]).start(self.env.bus_agent.sequencer)

        # Restart with TS
        await write_reg_seq("wr_ctrl_ts", addr["CTRL"], 0x03).start(
            self.env.bus_agent.sequencer)
        await ClockCycles(dut.CLK, 50)
        await read_reg_seq("rd_tmr3", addr["TMR"]).start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class PeriodicTest(tmr_base_test):
    """Periodic mode — verifies timer auto-reloads and keeps counting."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_config_seq import tmr_config_seq
        from cf_verify.bus_env.bus_seq_lib import read_reg_seq, write_reg_seq

        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address
        dut = ConfigDB().get(self, "", "DUT")

        config = tmr_config_seq(
            "config", direction=2, periodic=1, prescaler=0,
            reload=30, te=1, ts=1,
        )
        await config.start(self.env.bus_agent.sequencer)

        # Wait for multiple timer periods
        await ClockCycles(dut.CLK, 100)
        await read_reg_seq("rd_tmr1", addr["TMR"]).start(self.env.bus_agent.sequencer)
        await read_reg_seq("rd_ris1", addr["RIS"]).start(self.env.bus_agent.sequencer)

        # Clear and wait again
        if "IC" in addr:
            await write_reg_seq("ic_clear", addr["IC"], 0x7).start(
                self.env.bus_agent.sequencer)
        await ClockCycles(dut.CLK, 100)
        await read_reg_seq("rd_tmr2", addr["TMR"]).start(self.env.bus_agent.sequencer)
        await read_reg_seq("rd_ris2", addr["RIS"]).start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class PWMTest(tmr_base_test):
    """PWM — configures PWM outputs and verifies correct operation."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_pwm_seq import tmr_pwm_seq
        seq = tmr_pwm_seq("pwm_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class CompareMatchTest(tmr_base_test):
    """Compare match — tests CMPX/CMPY match detection."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_compare_seq import tmr_compare_seq
        seq = tmr_compare_seq("compare_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class InterruptTest(tmr_base_test):
    """Interrupt — verifies TO, MX, MY interrupts fire and clear."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_interrupt_seq import tmr_interrupt_seq
        seq = tmr_interrupt_seq("irq_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class DeadtimeTest(tmr_base_test):
    """Deadtime — verifies PWM deadtime insertion at various values."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_deadtime_seq import tmr_deadtime_seq
        seq = tmr_deadtime_seq("deadtime_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class FaultTest(tmr_base_test):
    """Fault — drives pwm_fault input and verifies fault handling."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_fault_seq import tmr_fault_seq
        seq = tmr_fault_seq("fault_test")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()


@pyuvm.test()
class CoverageClosureTest(tmr_base_test):
    """Coverage closure — systematically exercises all coverage bins."""

    async def run_phase(self):
        self.raise_objection()
        from seq_lib.tmr_coverage_closure_seq import tmr_coverage_closure_seq
        seq = tmr_coverage_closure_seq("cov_closure")
        await seq.start(self.env.bus_agent.sequencer)
        self.drop_objection()
