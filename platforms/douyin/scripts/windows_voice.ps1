param([Parameter(Mandatory=$true)][string]$Config)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$items = Get-Content -LiteralPath $Config -Raw -Encoding UTF8 | ConvertFrom-Json
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Huihui Desktop')
$synth.Rate = 1
try {
    foreach ($item in $items) {
        if (-not (Test-Path -LiteralPath $item.output)) {
            $synth.SetOutputToWaveFile($item.output)
            $synth.Speak($item.text)
            $synth.SetOutputToNull()
        }
    }
} finally { $synth.Dispose() }
Write-Output 'Chinese narration complete.'
