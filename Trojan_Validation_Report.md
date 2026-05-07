# Trojan Validation Report

This report summarizes the saved output from the notebook validation function in `Hardware_Trojan_Insertion_Lab.ipynb`.

The validation cell was updated to remove the erroneous `verilog_files[:5]` slice. It now validates all generated Trojaned Verilog files under `./trojan_outputs`, excluding notebook checkpoint folders.

## Validation Log

```text
TASK 4: Trojan Validation & Testing
==================================================
Validating 12 Trojaned designs...

Validating: aes_sbox_HT1_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 4 suspicious patterns
   Syntax validation passed

Validating: aes_sbox_HT2_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 3 suspicious patterns
   Syntax validation passed

Validating: aes_sbox_HT3_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 4 suspicious patterns
   Syntax validation passed

Validating: aes_sbox_HT4_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 2 suspicious patterns
   Syntax validation passed

Validating: alu_simple_HT1_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 3 suspicious patterns
   Syntax validation passed

Validating: alu_simple_HT2_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 10 suspicious patterns
   Syntax validation passed

Validating: shift_reg_HT1_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 3 suspicious patterns
   Syntax validation passed

Validating: shift_reg_HT2_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 3 suspicious patterns
   Syntax validation passed

Validating: uart_controller_HT1_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 3 suspicious patterns
   Syntax validation passed

Validating: uart_controller_HT2_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 4 suspicious patterns
   Syntax validation passed

Validating: uart_controller_HT3_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 6 suspicious patterns
   Syntax validation passed

Validating: uart_controller_HT4_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 4 suspicious patterns
   Syntax validation passed

VALIDATION SUMMARY
============================================================
Files validated: 12
Valid module structure: 12/12
Syntax validation passed: 12/12
Trojan indicators found: 12/12
```

## Pass / Fail Table

| Sample | Vulnerability | Module Structure | Trojan Markers | Suspicious Patterns | Syntax Check | Result | Issues |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `aes_sbox_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | Pass | Pass | 4 | Pass | Pass | None reported |
| `aes_sbox_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | Pass | Pass | 3 | Pass | Pass | None reported |
| `aes_sbox_HT3_google_gemini-3-flash-preview_A1.v` | `T3` | Pass | Pass | 4 | Pass | Pass | None reported |
| `aes_sbox_HT4_google_gemini-3-flash-preview_A1.v` | `T4` | Pass | Pass | 2 | Pass | Pass | None reported |
| `alu_simple_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | Pass | Pass | 3 | Pass | Pass | None reported |
| `alu_simple_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | Pass | Pass | 10 | Pass | Pass | None reported |
| `shift_reg_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | Pass | Pass | 3 | Pass | Pass | None reported |
| `shift_reg_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | Pass | Pass | 3 | Pass | Pass | None reported |
| `uart_controller_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | Pass | Pass | 3 | Pass | Pass | None reported |
| `uart_controller_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | Pass | Pass | 4 | Pass | Pass | None reported |
| `uart_controller_HT3_google_gemini-3-flash-preview_A1.v` | `T3` | Pass | Pass | 6 | Pass | Pass | None reported |
| `uart_controller_HT4_google_gemini-3-flash-preview_A1.v` | `T4` | Pass | Pass | 4 | Pass | Pass | None reported |

## Summary

| Check | Result |
| --- | --- |
| Files discovered by validation function | 12 |
| Files validated by function | 12 |
| Module structure pass rate | 12/12 |
| Syntax pass rate | 12/12 |
| Trojan marker detection rate | 12/12 |
| Reported failures | 0 |

## Issues / Notes

- No syntax failures were reported across the generated sample set.
- The suspicious-pattern counts are expected for Trojaned designs; they come from constants, comparisons, and counter-like updates.
- No optional functional testbench was run in the saved notebook output. The evidence here covers module-structure checks, Trojan-marker checks, suspicious-pattern checks, and syntax validation only.
