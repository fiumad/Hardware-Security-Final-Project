# Trojan Insertion Pattern Summary

This summary is based on the recorded outputs in `Hardware_Trojan_Insertion_Lab.ipynb` and the vulnerability definitions in `GHOST_Trojan_GPT.py`.

The notebook contains executed examples for `T1` and `T2`: a detailed single-design `T1` insertion on `simple_counter`, plus a batch run that generated `T1` and `T2` variants for `alu_simple` and `shift_reg`. The notebook lists `T3` and `T4` and creates a batch configuration for all four types, but that later batch cell was not executed in the saved outputs.

| Type | Vulnerability | Observed or Expected Trigger Pattern | Observed or Expected Payload Pattern | Common Inserted Structures | Stealth / Detectability Pattern | Evidence in Notebook |
| --- | --- | --- | --- | --- | --- | --- |
| `T1` | Change functionality | Internal event-count trigger. The detailed `simple_counter` example activates after `enable` has been asserted for 10 clock cycles. This uses a small counter and a hard-coded threshold constant. | Functional result is subtly altered after activation. In the counter example, the count changes from increment-by-1 to increment-by-2. | Extra trigger counter, trigger latch, local parameter/magic constant such as `4'd10`, conditional branch around original datapath update. | Looks like ordinary state/control logic, but exposes patterns such as threshold comparisons, extra persistent state, and arithmetic changes under a rare branch. | Executed single insertion for `simple_counter`; batch output also generated `HT1` files for `alu_simple` and `shift_reg`. |
| `T2` | Leak information | Pattern-detection trigger on functional inputs. The displayed `shift_reg` taxonomy says activation occurs when the pattern `101` is detected. | Covert serialization of internal state. The displayed `shift_reg` example leaks `data_out` LSB-first on an added `trojan_leak_out` output. | Pattern shift register, bit counter, active flag, added output or covert channel, serialization mux/conditional. | More visible than `T1` when it adds ports; internally it resembles debug/status logic. Strong indicators include new output channels, serial leak counters, and direct access to internal registers. | Executed batch output includes `HT2` files for `alu_simple` and `shift_reg`; notebook prints the `shift_reg` T2 code and taxonomy excerpts. |
| `T3` | Denial of service | Rare sequence-of-events trigger, usually expressed as a counter, state sequence detector, or magic condition over existing control signals. | Temporarily disables or stalls the module. Expected payloads include suppressing enables, holding outputs/state, forcing busy/reset-like states, or blocking writes. | Sequence detector, rare-condition comparator, disable/stall flag, gating around clock-enable or control paths. | Can resemble legitimate error handling, backpressure, reset, or flow-control logic. Detection should focus on unusual state-holding branches and conditions that suppress normal updates. | Listed in the notebook and defined in `GHOST_Trojan_GPT.py`; no saved executed `T3` insertion output is present. |
| `T4` | Performance degradation | Specific event trigger or low-visibility always-on activity. The configured strategy asks for a continuously running shift register or accumulator that activates on a specific event. | Increased switching activity and power consumption while preserving primary logical outputs. | Free-running or conditionally enabled shift register, accumulator, toggling register bank, extra arithmetic chain. | Functionally silent, so it is more likely to evade ordinary simulation. Static clues include unused or weakly connected registers, high-toggle logic, and accumulators that do not affect outputs. | Listed in the notebook and defined in `GHOST_Trojan_GPT.py`; no saved executed `T4` insertion output is present. |

## Cross-Type Patterns

| Pattern | Appears In | Notes |
| --- | --- | --- |
| Counters | `T1`, `T2`, likely `T3`; sometimes `T4` | Used for time/event triggers, bit serialization, and rare activation windows. |
| Magic constants | `T1`, `T2`, likely `T3` | Examples include `4'd10` for delayed activation and `3'b101` for pattern detection. |
| Rare conditions | All types | Central stealth mechanism: preserve normal behavior until a threshold, pattern, or uncommon sequence occurs. |
| Trigger latch / active flag | `T1`, `T2`, likely `T3` and `T4` | Stores activation state after a rare condition is detected. |
| Added internal state | All types | Registers are the main footprint: counters, shift registers, activity flags, accumulators, or shadow state. |
| Original-functionality preservation | All types | The generated prompt explicitly asks to maintain normal functionality, so inserted logic tends to wrap existing behavior rather than replace it outright. |
| Covert observability channel | `T2` | The observed T2 example adds `trojan_leak_out`; other designs may hide this through existing outputs or side channels. |
| Silent resource/power impact | `T4` | Expected to avoid changing functional outputs while increasing toggle activity. |

## Practical Review Cues

- Compare Trojaned files against clean designs for added `reg`, `localparam`, comparator, and conditional assignments.
- Inspect thresholds and binary constants that do not correspond to documented protocol states or datapath requirements.
- Trace any newly added output or debug-like signal back to internal data paths.
- Review branches that hold, skip, or alter normal state updates under narrow conditions.
- For performance-degradation variants, look for extra state that toggles but does not contribute to module outputs.
