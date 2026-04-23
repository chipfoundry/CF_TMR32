"""TMR32 configuration sequence — sets up timer mode, prescaler, and enables."""

import random

from pyuvm import uvm_sequence, ConfigDB

from cf_verify.bus_env.bus_seq_lib import write_reg_seq, reset_seq


class tmr_config_seq(uvm_sequence):
    def __init__(self, name="tmr_config_seq", direction=None, periodic=None,
                 prescaler=None, reload=None, cmpx=None, cmpy=None,
                 te=1, ts=0, p0e=0, p1e=0, dte=0, pi0=0, pi1=0, im=None):
        super().__init__(name)
        self.direction = direction
        self.periodic = periodic
        self.prescaler = prescaler
        self.reload = reload
        self.cmpx = cmpx
        self.cmpy = cmpy
        self.te = te
        self.ts = ts
        self.p0e = p0e
        self.p1e = p1e
        self.dte = dte
        self.pi0 = pi0
        self.pi1 = pi1
        self.im = im

    async def body(self):
        await reset_seq("rst").start(self.sequencer)

        regs = ConfigDB().get(None, "", "bus_regs")
        addr = regs.reg_name_to_address

        if "GCLK" in addr:
            await write_reg_seq("wr_gclk", addr["GCLK"], 1).start(self.sequencer)

        # Disable timer first
        await write_reg_seq("wr_ctrl_off", addr["CTRL"], 0).start(self.sequencer)

        # Prescaler
        pr = self.prescaler if self.prescaler is not None else random.choice([0, 1, 4])
        await write_reg_seq("wr_pr", addr["PR"], pr).start(self.sequencer)

        # Reload
        rl = self.reload if self.reload is not None else random.randint(10, 100)
        await write_reg_seq("wr_reload", addr["RELOAD"], rl).start(self.sequencer)

        # Compare values
        cx = self.cmpx if self.cmpx is not None else rl // 3
        cy = self.cmpy if self.cmpy is not None else (rl * 2) // 3
        await write_reg_seq("wr_cmpx", addr["CMPX"], cx).start(self.sequencer)
        await write_reg_seq("wr_cmpy", addr["CMPY"], cy).start(self.sequencer)

        # CFG: DIR[1:0] + P[2]
        d = self.direction if self.direction is not None else random.choice([1, 2, 3])
        p = self.periodic if self.periodic is not None else random.randint(0, 1)
        cfg = (d & 0x3) | ((p & 0x1) << 2)
        await write_reg_seq("wr_cfg", addr["CFG"], cfg).start(self.sequencer)

        # Interrupt mask
        im_val = self.im if self.im is not None else 0x7
        if "IM" in addr:
            await write_reg_seq("wr_im", addr["IM"], im_val).start(self.sequencer)

        # CTRL: TE[0] TS[1] P0E[2] P1E[3] DTE[4] PI0[5] PI1[6]
        ctrl = (
            (self.te & 1)
            | ((self.ts & 1) << 1)
            | ((self.p0e & 1) << 2)
            | ((self.p1e & 1) << 3)
            | ((self.dte & 1) << 4)
            | ((self.pi0 & 1) << 5)
            | ((self.pi1 & 1) << 6)
        )
        await write_reg_seq("wr_ctrl", addr["CTRL"], ctrl).start(self.sequencer)
