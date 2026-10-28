param(
    [int]$Trials = 1000,
    [int]$Seed = 20261018,
    [double]$TargetPrecision = 0.99,
    [string]$OutputDirectory = ''
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $repoRoot '.venv\Scripts\python.exe'
$scriptPath = Join-Path $PSScriptRoot 'calibrate_product_name_thresholds.py'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Project Python not found: $pythonPath"
}
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $runName = 'run_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')
    $OutputDirectory = Join-Path $repoRoot ('data\processed\product_name_calibration\' + $runName)
}
$outputPath = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $outputPath) {
    throw 'Choose a new output directory. For a previous run, use the Python --resume command.'
}
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
$stdoutPath = Join-Path $outputPath 'stdout.log'
$stderrPath = Join-Path $outputPath 'stderr.log'
$stdinPath = Join-Path $outputPath 'stdin.empty'
[IO.File]::WriteAllText($stdinPath, '')
$culture = [Globalization.CultureInfo]::InvariantCulture
$processArguments = @(
    '-X', 'utf8', '-u', ('"' + $scriptPath + '"'),
    '--trials', $Trials.ToString($culture),
    '--seed', $Seed.ToString($culture),
    '--target-precision', $TargetPrecision.ToString($culture),
    '--output', ('"' + $outputPath + '"')
)
$worker = Start-Process -FilePath $pythonPath -ArgumentList $processArguments `
    -WorkingDirectory $repoRoot -WindowStyle Hidden `
    -RedirectStandardInput $stdinPath `
    -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
# A Windows venv python.exe may launch another Python process. Report the PID
# written by the actual worker rather than only the venv launcher PID.
$workerPid = $worker.Id
$progressPath = Join-Path $outputPath 'progress.json'
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    if (Test-Path -LiteralPath $progressPath) {
        try {
            $bootProgress = Get-Content -LiteralPath $progressPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($bootProgress.pid -gt 0) {
                $workerPid = $bootProgress.pid
                break
            }
        } catch { }
    }
    if ($worker.HasExited) { break }
    Start-Sleep -Milliseconds 100
}
$launch = [ordered]@{
    pid = $workerPid
    launcher_pid = $worker.Id
    output = $outputPath
    trials = $Trials
    progress = $progressPath
    report = (Join-Path $outputPath 'report.md')
    stdout = $stdoutPath
    stderr = $stderrPath
}
$launch | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputPath 'launch.json') -Encoding UTF8
$launch | ConvertTo-Json
