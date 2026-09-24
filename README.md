# EDA Skills

Reusable Codex skills for electronic design automation workflows.

## Included skill

- [`eda-chip-circuit-design-skill`](skills/eda-chip-circuit-design-skill/): verifies manufacturer data, explains IC pins, derives typical and target circuits, selects passive components, and produces BOM, netlist, and design review notes.

## Use in Codex

Copy the skill directory to your user skills directory:

```powershell
Copy-Item -Recurse -Force skills\eda-chip-circuit-design-skill "$env:USERPROFILE\.agents\skills\eda-chip-circuit-design-skill"
```

Then start a new Codex session and invoke `/eda-chip-circuit-design-skill`.

The skill treats manufacturer documentation as the primary source. Calculations are first-pass estimates and still require datasheet stability checks, simulation, layout review, and laboratory validation before production use.

## License

MIT. See [`LICENSE`](skills/eda-chip-circuit-design-skill/LICENSE).
