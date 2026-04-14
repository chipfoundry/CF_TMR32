# CF_TMR32 PyUVM Verification — Known Issues

## Open

1. **Fault handling coverage**: The exact behavior of `pwm_fault` / `PWMFC` interaction
   needs validation against RTL. The fault sequence drives the signal and clears via register,
   but the precise timing of PWM shutdown/restart may vary.

2. **Up/Down counting boundary**: The transition point between up and down phases in
   `direction=3` (up/down) mode may have edge cases around the reload value that need
   closer scrutiny with waveform inspection.

3. **PWM1CFG size**: The YAML specifies PWM1CFG as 16-bit (vs PWM0CFG at 12-bit), but the
   RTL PWM1CFG register only uses 12 bits of actions (E0-E5, 2 bits each). The upper 4 bits
   may be reserved. Coverage currently covers all 6 action events for both channels.

4. **Prescaler PR register width**: The PR register uses the `PRW` parameter (default 16),
   but coverage bins only go up to 65535. If PRW is changed, bins may need adjustment.

## Resolved

(None yet — initial creation)
