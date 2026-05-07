# Heuristic Detector Results

This report summarizes the saved output from the heuristic detector cells in `Hardware_Trojan_Insertion_Lab.ipynb`.

The detector evaluates three scores per file:

- `Trig`: suspicious trigger evidence
- `Payload`: suspicious payload evidence
- `Link`: evidence that trigger logic gates or controls payload behavior

Detection pass means the file was assigned `Medium` or `High` risk. Classification pass means the predicted `T1`-`T4` type matched the known label encoded in the generated filename.

## Trojaned Sample Results

| File | Known | Pred | Risk | Trig | Payload | Link | Detection | Classification |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `aes_sbox_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | `T1` | High | 7 | 5 | 2 | PASS | PASS |
| `aes_sbox_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | `T2` | High | 6 | 11 | 2 | PASS | PASS |
| `aes_sbox_HT3_google_gemini-3-flash-preview_A1.v` | `T3` | `T3` | High | 7 | 5 | 2 | PASS | PASS |
| `aes_sbox_HT4_google_gemini-3-flash-preview_A1.v` | `T4` | `T4` | High | 5 | 8 | 2 | PASS | PASS |
| `alu_simple_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | `T1` | High | 7 | 5 | 2 | PASS | PASS |
| `alu_simple_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | `T2` | High | 4 | 5 | 2 | PASS | PASS |
| `shift_reg_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | `T1` | High | 7 | 5 | 2 | PASS | PASS |
| `shift_reg_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | `T2` | High | 6 | 5 | 2 | PASS | PASS |
| `uart_controller_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | `T1` | High | 8 | 8 | 2 | PASS | PASS |
| `uart_controller_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | `T2` | High | 7 | 11 | 2 | PASS | PASS |
| `uart_controller_HT3_google_gemini-3-flash-preview_A1.v` | `T3` | `T3` | High | 10 | 8 | 2 | PASS | PASS |
| `uart_controller_HT4_google_gemini-3-flash-preview_A1.v` | `T4` | `T4` | High | 6 | 11 | 2 | PASS | PASS |

## Trojaned Summary

| Metric | Result |
| --- | --- |
| Files scanned | 12 |
| Medium/High risk detections | 12/12 |
| Detection rate | 100.0% |
| Correct `T1`-`T4` classifications | 12/12 |
| Classification rate | 100.0% |
| High risk | 12 |
| Medium risk | 0 |
| Low risk | 0 |
| No risk | 0 |

## Clean Baseline False-Positive Check

The detector was also run on the clean baseline designs in `demo_designs` and `batch_trojan_designs`.

| File | Known | Pred | Risk | Trig | Payload | Link | Detection | Classification |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `alu_simple.v` | Clean | Unknown | None | 0 | 0 | 0 | FAIL | PASS |
| `shift_reg.v` | Clean | Unknown | None | 0 | 3 | 0 | FAIL | PASS |
| `aes_sbox.v` | Clean | Unknown | Low | 0 | 5 | 0 | FAIL | PASS |
| `uart_controller.v` | Clean | Unknown | Low | 2 | 8 | 2 | FAIL | PASS |

For clean files, `Detection = FAIL` means the detector did not flag the design as Medium/High risk, which is the desired outcome.

## Clean Summary

| Metric | Result |
| --- | --- |
| Clean files scanned | 4 |
| Clean files flagged Medium/High risk | 0/4 |
| Observed false positives | 0 |
| High risk | 0 |
| Medium risk | 0 |
| Low risk | 2 |
| No risk | 2 |

## Conclusion

The detector was successful on this sample set:

- It detected all 12 generated Trojaned designs.
- It correctly classified all 12 generated designs as `T1`, `T2`, `T3`, or `T4`.
- It produced no Medium/High-risk false positives on the four clean baseline designs.

The two Low-risk clean results are useful review hints rather than false positives. They come from benign structures that resemble parts of Trojan patterns: AES constants, UART counters, reset/idle assignments, and shift-register behavior. The detector avoids escalating these to positive detections because it requires stronger rare-trigger and payload-link evidence.

Potential false negatives remain possible for Trojans that avoid obvious counters, magic constants, suspicious names, or trigger-gated payload assignments.
