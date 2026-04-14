"""TMR32 transaction item — carries timer/PWM state for coverage and scoreboarding."""

import random

from pyuvm import uvm_sequence_item


class tmr_item(uvm_sequence_item):
    PWM_EVENT = 0
    TIMER_EVENT = 1
    FAULT_EVENT = 2

    def __init__(self, name="tmr_item"):
        super().__init__(name)
        self.timer_value = 0
        self.reload = 0
        self.prescaler = 0
        self.mode = 0
        self.pwm0_state = 0
        self.pwm1_state = 0
        self.timeout = 0
        self.matchx = 0
        self.matchy = 0
        self.event_type = tmr_item.TIMER_EVENT
        self.pwm_fault = 0

    def randomize(self):
        self.timer_value = random.randint(0, 0xFFFFFFFF)
        self.reload = random.randint(1, 0xFFFF)
        self.prescaler = random.randint(0, 0xFF)

    def convert2string(self):
        return (
            f"tmr=0x{self.timer_value:08x} reload=0x{self.reload:08x} "
            f"pr={self.prescaler} mode={self.mode} "
            f"pwm0={self.pwm0_state} pwm1={self.pwm1_state} "
            f"TO={self.timeout} MX={self.matchx} MY={self.matchy}"
        )

    def do_compare(self, rhs):
        return (
            self.timer_value == rhs.timer_value
            and self.timeout == rhs.timeout
            and self.matchx == rhs.matchx
            and self.matchy == rhs.matchy
        )

    def do_copy(self, rhs):
        super().do_copy(rhs)
        self.timer_value = rhs.timer_value
        self.reload = rhs.reload
        self.prescaler = rhs.prescaler
        self.mode = rhs.mode
        self.pwm0_state = rhs.pwm0_state
        self.pwm1_state = rhs.pwm1_state
        self.timeout = rhs.timeout
        self.matchx = rhs.matchx
        self.matchy = rhs.matchy
        self.event_type = rhs.event_type
        self.pwm_fault = rhs.pwm_fault

    def do_clone(self):
        new = tmr_item(self.get_name())
        new.do_copy(self)
        return new
