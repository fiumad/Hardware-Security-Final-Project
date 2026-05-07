# Trojan Validation Report

This report summarizes the saved output from the notebook validation function in `Hardware_Trojan_Insertion_Lab.ipynb`.

The validation cell was run on `./trojan_outputs` after Trojan generation. It reported finding 12 Trojaned designs, but the function validates only the first five files because the loop is limited to `verilog_files[:5]`.

## Validation Log

```text
TASK 4: Trojan Validation & Testing
==================================================
Validating 12 Trojaned designs...

Validating: alu_simple_HT2_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 10 suspicious patterns
   Syntax validation passed

Validating: alu_simple_HT1_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 3 suspicious patterns
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

Validating: aes_sbox_HT1_google_gemini-3-flash-preview_A1.v
   Module structure found
   Trojan markers detected
   Found 4 suspicious patterns
   Syntax validation passed

VALIDATION SUMMARY
============================================================
Files validated: 5
Valid module structure: 5/5
Syntax validation passed: 5/5
Trojan indicators found: 5/5
```

## Pass / Fail Table

| Sample | Vulnerability | Module Structure | Trojan Markers | Suspicious Patterns | Syntax Check | Result | Issues |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `alu_simple_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | Pass | Pass | 10 | Pass | Pass | None reported |
| `alu_simple_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | Pass | Pass | 3 | Pass | Pass | None reported |
| `shift_reg_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | Pass | Pass | 3 | Pass | Pass | None reported |
| `shift_reg_HT2_google_gemini-3-flash-preview_A1.v` | `T2` | Pass | Pass | 3 | Pass | Pass | None reported |
| `aes_sbox_HT1_google_gemini-3-flash-preview_A1.v` | `T1` | Pass | Pass | 4 | Pass | Pass | None reported |

## Summary

| Check | Result |
| --- | --- |
| Files discovered by validation function | 12 |
| Files actually validated by function | 5 |
| Module structure pass rate | 5/5 |
| Syntax pass rate | 5/5 |
| Trojan marker detection rate | 5/5 |
| Reported failures | 0 |

## Issues / Notes

- No syntax failures were reported for the five sampled files.
- The validation function prints that it is validating 12 designs, but only checks the first five because of the `verilog_files[:5]` limit.
- The suspicious-pattern counts are expected for Trojaned designs; they come from constants, comparisons, and counter-like updates.
- No optional functional testbench was run in the saved notebook output. The evidence here covers module-structure checks, Trojan-marker checks, suspicious-pattern checks, and syntax validation only.
