# CF_TMR32 PyUVM Verification

![Tests](https://img.shields.io/badge/tests-12-blue)
![Buses](https://img.shields.io/badge/buses-APB%20%7C%20AHB%20%7C%20WB-green)
![Coverage](https://img.shields.io/badge/coverage-functional-orange)
![Framework](https://img.shields.io/badge/framework-pyuvm%20%2B%20cocotb-purple)

PyUVM-based verification environment for the CF_TMR32 32-bit Timer with dual PWM generator.

## Quick Start

```bash
pip install -r requirements.txt
python test_runner.py
```

### Run specific bus/test

```bash
BUSES=APB TESTS=WriteReadRegsTest python test_runner.py
```

### Run with Verilator

```bash
SIM=verilator python test_runner.py
```

## Test Suite

| Test | Description |
|------|-------------|
| WriteReadRegsTest | Write/read all accessible registers |
| TimerUpCountTest | Up counting from 0 to RELOAD |
| TimerDownCountTest | Down counting from RELOAD to 0 |
| TimerUpDownTest | Up/down counting mode |
| OneShotTest | One-shot mode — timer stops after one cycle |
| PeriodicTest | Periodic mode — auto-reload verification |
| PWMTest | PWM output generation and configuration |
| CompareMatchTest | CMPX/CMPY match flag detection |
| InterruptTest | TO/MX/MY interrupt fire and clear |
| DeadtimeTest | PWM deadtime insertion |
| FaultTest | External fault input handling |
| CoverageClosureTest | Systematic coverage bin sweep |

## Architecture

```
test_lib.py              # 12 test classes + tmr_env + tmr_base_test
test_runner.py           # cocotb.runner — builds, runs, merges coverage
top.v                    # Testbench top — APB/AHB/WB conditional instantiation
ip_agent/
  tmr_driver.py          # Drives pwm_fault signal
  tmr_monitor.py         # Watches pwm0, pwm1 transitions
ip_item/
  tmr_item.py            # Timer/PWM transaction item
ip_coverage/
  tmr_coverage.py        # Coverage component (auto + custom)
  tmr_cov_groups.py      # Custom coverpoints: directions, modes, PWM, IRQ
seq_lib/
  tmr_config_seq.py      # Timer configuration helper
  tmr_upcount_seq.py     # Up counting test sequence
  tmr_downcount_seq.py   # Down counting test sequence
  tmr_pwm_seq.py         # PWM output test sequence
  tmr_compare_seq.py     # Compare match test sequence
  tmr_interrupt_seq.py   # Interrupt test sequence
  tmr_deadtime_seq.py    # Deadtime test sequence
  tmr_fault_seq.py       # Fault handling test sequence
  tmr_coverage_closure_seq.py  # Coverage closure sweep
```

## Coverage Groups

- **Auto-generated**: Register field coverage from YAML (CTRL, CFG, PR, PWM0CFG, PWM1CFG, PWMDT, PWMFC)
- **CountDirection**: up / down / updown / none
- **TimerMode**: direction × periodic/oneshot (6 bins)
- **PWM_Enables**: PWM0/PWM1 enable combinations
- **PWM_Inversion**: PWM0/PWM1 inversion combinations
- **PWM action events**: E0-E5 for both PWM channels (no_action/low/high/invert)
- **IRQ flags**: TO, MX, MY assertion and mask combinations
- **Compare ranges**: CMPX/CMPY value range bins
- **Deadtime**: Enable state and value range bins
