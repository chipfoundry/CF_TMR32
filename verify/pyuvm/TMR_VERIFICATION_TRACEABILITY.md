# CF_TMR32 — Verification traceability

## Scoreboard

- **IP path**: `tmr_scoreboard` compares DUT IP monitor transactions to the reference model in lockstep (`await` on both FIFOs).
- **check_phase**: Fails the test if any `_check` reported a mismatch (`assert self.failed == 0`).

## Register smoke

- **WriteReadRegsTest**: Runs `write_read_regs_seq`, then explicitly writes and reads back each writable register that is readable (skips `IC`, `GCLK`, `*_FLUSH`, and YAML `mode: w`).

## Anti–vacuous pass

- Removed `get_nowait` / swallowed exceptions so missing reference transactions cannot be silently ignored.
