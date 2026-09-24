#!/usr/bin/env python3
"""First-pass, unit-explicit power calculations for eda-chip-circuit-design-skill.

This script is deliberately conservative: it computes estimates and flags values
that still require a device datasheet, stability matrix, simulation, or lab test.
It does not select a specific manufacturer's part.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass


def positive(name: str, value: float) -> float:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return value


def ratio(name: str, value: float, low: float = 0, high: float = 1) -> float:
    if not math.isfinite(value) or not low < value < high:
        raise ValueError(f"{name} must be between {low} and {high}")
    return value


@dataclass
class BuckResult:
    duty: float
    ripple_current: float
    inductance_h: float
    peak_current_a: float
    rms_current_a: float
    input_cap_rms_a: float
    output_cap_for_ripple_f: float
    output_esr_max_ohm: float
    output_power_w: float
    input_power_est_w: float
    notes: list[str]


@dataclass
class BoostResult:
    duty: float
    ripple_current: float
    inductance_h: float
    input_current_avg_a: float
    peak_current_a: float
    output_cap_for_ripple_f: float
    output_power_w: float
    input_power_est_w: float
    notes: list[str]


def buck(vin: float, vout: float, iout: float, fs: float, ripple_fraction: float,
         output_ripple: float, efficiency: float) -> BuckResult:
    for n, x in (("vin", vin), ("vout", vout), ("iout", iout), ("fs", fs), ("output_ripple", output_ripple)):
        positive(n, x)
    ratio("ripple_fraction", ripple_fraction, 0, 1)
    if not math.isfinite(efficiency) or not 0 < efficiency <= 1:
        raise ValueError("efficiency must be between 0 and 1, inclusive of 1")
    if vin <= vout:
        raise ValueError("buck requires vin > vout for this CCM estimate")
    d = vout / vin
    di = ripple_fraction * iout
    l = (vin - vout) * d / (fs * di)
    ipk = iout + di / 2
    irms = math.sqrt(iout * iout + di * di / 12)
    icin = iout * math.sqrt(d * (1 - d))
    # Split the allowed ripple equally between the capacitive and ESR terms.
    cmin = di / (8 * fs * (output_ripple / 2))
    esr = (output_ripple / 2) / di
    pout = vout * iout
    pin = pout / efficiency
    return BuckResult(d, di, l, ipk, irms, icin, cmin, esr, pout, pin, [
        "CCM, ideal duty approximation; include controller losses and min/max duty limits.",
        "Capacitive and ESR ripple each receive half the specified ripple budget; check the combined result.",
        "Use effective capacitance at bias and temperature, not the capacitor label.",
        "Check datasheet stability matrix, current limit, transient response, and thermal limits.",
    ])


def boost(vin: float, vout: float, iout: float, fs: float, ripple_fraction: float,
          output_ripple: float, efficiency: float) -> BoostResult:
    for n, x in (("vin", vin), ("vout", vout), ("iout", iout), ("fs", fs), ("output_ripple", output_ripple)):
        positive(n, x)
    ratio("ripple_fraction", ripple_fraction, 0, 1)
    if not math.isfinite(efficiency) or not 0 < efficiency <= 1:
        raise ValueError("efficiency must be between 0 and 1, inclusive of 1")
    if vout <= vin:
        raise ValueError("boost requires vout > vin for this estimate")
    d = 1 - vin / vout
    pout = vout * iout
    pin = pout / efficiency
    iin = pin / vin
    di = ripple_fraction * iin
    l = vin * d / (fs * di)
    ipk = iin + di / 2
    cmin = iout * d / (fs * (output_ripple / 2))
    return BoostResult(d, di, l, iin, ipk, cmin, pout, pin, [
        "CCM, ideal duty approximation; account for switch/diode drops and max duty.",
        "Only half of specified ripple is allocated to the capacitive term; check ESR and transient ripple separately.",
        "The input current is often much higher than output current; size the inductor and switch accordingly.",
        "Check reverse voltage, current limit, startup, short-circuit, thermal, and output overvoltage behavior.",
    ])


def divider(vout: float, vref: float, rbot_ohm: float, min_current_a: float | None = None) -> dict[str, float | list[str]]:
    positive("vout", vout)
    positive("vref", vref)
    positive("rbot_ohm", rbot_ohm)
    if vout <= vref:
        raise ValueError("vout must be greater than vref for a two-resistor divider")
    rtop = rbot_ohm * (vout / vref - 1)
    current = vout / (rtop + rbot_ohm)
    out: dict[str, float | list[str]] = {"rtop_ohm": rtop, "rbot_ohm": rbot_ohm, "divider_current_a": current, "notes": [
        "Recalculate with the datasheet FB leakage/bias current and resistor tolerance.",
        "For fixed-output parts, do not add a divider unless the datasheet says the pin supports it.",
    ]}
    if min_current_a is not None:
        positive("min_current_a", min_current_a)
        out["meets_min_current"] = current >= min_current_a
    return out


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="First-pass DC-DC calculations; outputs JSON by default.")
    sub = p.add_subparsers(dest="kind", required=True)
    for kind in ("buck", "boost"):
        q = sub.add_parser(kind)
        q.add_argument("--vin", type=float, required=True, help="V")
        q.add_argument("--vout", type=float, required=True, help="V")
        q.add_argument("--iout", type=float, required=True, help="A")
        q.add_argument("--fs", type=float, required=True, help="Hz")
        q.add_argument("--ripple-fraction", type=float, default=0.3)
        q.add_argument("--output-ripple", type=float, required=True, help="V peak-to-peak, capacitive estimate")
        q.add_argument("--efficiency", type=float, default=0.9)
    q = sub.add_parser("divider")
    q.add_argument("--vout", type=float, required=True, help="V")
    q.add_argument("--vref", type=float, required=True, help="V")
    q.add_argument("--rbot", type=float, required=True, help="ohm")
    q.add_argument("--min-current", type=float, help="A")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.kind == "buck":
            result = asdict(buck(args.vin, args.vout, args.iout, args.fs, args.ripple_fraction, args.output_ripple, args.efficiency))
        elif args.kind == "boost":
            result = asdict(boost(args.vin, args.vout, args.iout, args.fs, args.ripple_fraction, args.output_ripple, args.efficiency))
        else:
            result = divider(args.vout, args.vref, args.rbot, args.min_current)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
