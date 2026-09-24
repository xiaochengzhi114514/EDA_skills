param(
  [string]$Destination = "$env:USERPROFILE\.agents\skills\eda-chip-circuit-design-skill"
)

$source = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Copy-Item -Path (Join-Path $source '*') -Destination $Destination -Recurse -Force
Write-Output "Installed eda-chip-circuit-design-skill to $Destination"
