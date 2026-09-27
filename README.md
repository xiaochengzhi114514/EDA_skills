# EDA Skills

Reusable Codex skills for electronic design automation workflows.

## Included skill

- [`eda-chip-circuit-design-skill`](skills/eda-chip-circuit-design-skill/): verifies manufacturer data, explains IC pins, derives typical and target circuits, selects passive components, and produces BOM, netlist, PCB placement/trace guidance, controlled-impedance decisions, and design review notes.

## Example

- [TPS54331DR 12 V → 5 V / 3 A: schematic, PCB layout guide, calculations, and validation notes](examples/tps54331dr-12v-to-5v-3a/design.md).
- [Standalone combined schematic and PCB guide](examples/tps54331dr-12v-to-5v-3a/tps54331dr_12v_to_5v_3a_circuit_pcb_review.html).

## Use in Codex

Copy the skill directory to your user skills directory:

```powershell
Copy-Item -Recurse -Force skills\eda-chip-circuit-design-skill "$env:USERPROFILE\.agents\skills\eda-chip-circuit-design-skill"
```

Then start a new Codex session and invoke `/eda-chip-circuit-design-skill`.

The skill treats manufacturer documentation as the primary source. Calculations are first-pass estimates and still require datasheet stability checks, simulation, layout review, and laboratory validation before production use.

## License

MIT. See [`LICENSE`](skills/eda-chip-circuit-design-skill/LICENSE).
