# Trojan Insertion Pattern Summary

This summary is based on the generated files under `trojan_outputs/google_gemini-3-flash-preview/`, the taxonomy files produced by `GHOST_Trojan_GPT.py`, and the notebook analysis cells in `Hardware_Trojan_Insertion_Lab.ipynb`.

The generated output set contains 12 Trojaned Verilog files and 12 taxonomy files:

| Type | Generated Designs |
| --- | --- |
| `T1` | `aes_sbox`, `alu_simple`, `shift_reg`, `uart_controller` |
| `T2` | `aes_sbox`, `alu_simple`, `shift_reg`, `uart_controller` |
| `T3` | `aes_sbox`, `uart_controller` |
| `T4` | `aes_sbox`, `uart_controller` |

The notebook analysis utility found 12 Trojaned designs and 12 taxonomy files. The filename parser now keys on the explicit `_HT1_` through `_HT4_` token, so design names with underscores, such as `aes_sbox` and `uart_controller`, are grouped correctly.

## Vulnerability Patterns

| Type | Vulnerability | Generated Count | Trigger Patterns Observed | Payload Patterns Observed | Common Inserted Structures | Detection Cues |
| --- | --- | ---: | --- | --- | --- | --- |
| `T1` | Change functionality | 4 | Time/event counters combined with rare values. Examples include 16-bit counters reaching `0xFFFF` or `16'hFFFF`, `a == 0xFF`, AES input `0xFF`, and UART `tx_start` event overflow. | Silent functional corruption: wrong AES S-box constant `0xEE`, ALU add off-by-one, inverted shift input bit, inverted UART transmit bit. | Hidden counters, trigger flags, rare-value comparators, conditional branches inside normal datapath operations. | Extra sequential state in otherwise simple combinational/sequential blocks; hardcoded thresholds; arithmetic/bit inversions under narrow conditions. |
| `T2` | Leak information | 4 | Sequence, duration, and pattern triggers. Examples include `trigger_signal` held high for 16 cycles, ALU op sequence `010 -> 011 -> 001`, shift-register pattern matching against `auth_key`, and 255-cycle UART delay after reset. | Covert information leakage through output behavior or side channels: parity on `leak_port`, leaking ALU input `a` through `result`, modulating switching activity from `data_out` MSB, XORing internal data with UART transmit bits. | Shadow/secret buffers, sequence detectors, trigger state machines, covert ports, parity logic, XOR/modulation logic. | Added observability paths, new ports or repurposed outputs, direct reads of internal data, sequence-detection state. |
| `T3` | Denial of service | 2 | Rare event counters. AES activates after 65,535 occurrences of `8'h03`; UART activates after 65,535 idle receptions of byte `0xFF`. | Availability failure: AES S-box output forced to `8'h00`; UART `tx` forced high/idle so valid data is not transmitted. | Long counters, activation registers, rare input comparators, output override muxes. | Branches that suppress normal updates or force constant outputs; reset/idle-like behavior activated by unlikely counters. |
| `T4` | Performance degradation | 2 | Specific input/event triggers. AES activates when `data_in == 8'h03`; UART activates after 10 occurrences of byte `0xFF`. | Functionally silent high-toggle activity: 32-bit inverted circular shift, wide feedback/toggling register updated with `~power_sink_reg + 32'h55555555`. | Hidden shift registers, accumulators/power sink registers, trigger latch, event counter. | Registers that toggle but do not feed functional outputs; high-activity constants; parametric/power-only payloads. |

## Static Metrics From Generated Verilog

| Type | Files | Avg. Lines | Avg. `if` Statements | Avg. `reg` Declarations | Avg. Hardcoded Constants | Avg. Counter-Like Increments | Avg. Equality Comparisons |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `T1` | 4 | 48.2 | 3.5 | 2.5 | 10.2 | 1.2 | 1.5 |
| `T2` | 4 | 57.8 | 4.8 | 3.8 | 14.8 | 0.8 | 2.8 |
| `T3` | 2 | 57.5 | 4.5 | 3.5 | 14.5 | 1.5 | 2.0 |
| `T4` | 2 | 61.5 | 5.5 | 4.5 | 15.5 | 1.0 | 1.0 |

## Cross-Type Patterns

| Pattern | Appears In | Examples From Outputs |
| --- | --- | --- |
| Counters | `T1`, `T2`, `T3`, `T4` | `16'hFFFF` time bombs, 16-cycle external trigger duration, 255-cycle UART delay, 10-event UART power trigger. |
| Magic constants | `T1`, `T2`, `T3`, `T4` | `0xFFFF`, `8'h03`, `0xFF`, `0xEE`, ALU op sequence `010/011/001`, `32'h55555555`. |
| Rare conditions | `T1`, `T2`, `T3`, `T4` | Long counters, uncommon byte values, multi-cycle operation sequences, key/pattern matches. |
| Trigger latch / active flag | `T1`, `T2`, `T3`, `T4` | Persistent activation registers used after a threshold or pattern match. |
| Added internal state | `T1`, `T2`, `T3`, `T4` | Counters, shadow buffers, sequence states, power sink registers, shift registers. |
| Output override | `T1`, `T2`, `T3` | Corrupting normal result bits, leaking internal values through outputs, forcing DoS constants. |
| Functionally silent side effect | `T2`, `T4` | Side-channel modulation and high-toggle registers that preserve nominal functional output. |

## Notebook Validation Notes

The validation utility ran on all 12 generated Verilog files and reported:

| Check | Result |
| --- | --- |
| Module structure found | 12/12 |
| Trojan markers detected | 12/12 |
| Syntax validation passed | 12/12 |
| Trojan indicators found | 12/12 |

The utility reported suspicious-pattern counts from 2 to 10 across the generated files, mainly from equality comparisons, hardcoded constants, and counter-like updates.

## Practical Review Cues

- Search for added `reg`, `localparam`, equality comparators, and conditional assignments near output logic.
- Inspect hardcoded thresholds and byte constants that are not part of the original protocol or truth table.
- Trace any shadow register, covert output, or parity/XOR logic back to internal signals.
- Review branches that force constants, hold idle values, invert bits, or skip normal state updates.
- For `T4`, look for toggling state that does not contribute to functional outputs but increases switching activity.
