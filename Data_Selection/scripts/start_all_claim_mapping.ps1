param(
    [string]$InputPath = 'C:\Users\박이정\Documents\카카오톡 받은 파일\claims_all.json',
    [int]$Threads = 4,
    [int]$BatchSize = 4
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $repoRoot '.venv\Scripts\python.exe'
$scriptPath = Join-Path $PSScriptRoot 'run_all_claim_mapping.py'
$outputPath = Join-Path $repoRoot 'data\processed\claim_evidence_all'
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
$stdoutPath = Join-Path $outputPath 'stdout.log'
$stderrPath = Join-Path $outputPath 'stderr.log'
$statusPath = Join-Path $outputPath 'full_run_status.json'
if (Test-Path -LiteralPath $statusPath) {
    $previous = Get-Content -LiteralPath $statusPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($previous.status -in @('starting','scoring','exporting','validating')) {
        if (Get-Process -Id $previous.pid -ErrorAction SilentlyContinue) {
            throw 'A full mapping job is already running. Check full_run_status.json and progress.json.'
        }
        if ($previous.worker_pid -and (Get-Process -Id $previous.worker_pid -ErrorAction SilentlyContinue)) {
            throw 'The previous scorer is still running. Do not start a second scorer.'
        }
    }
}
$stdinPath = Join-Path $outputPath 'stdin.empty'
[IO.File]::WriteAllText($stdinPath, '')
$processArguments = @('-u', '-X', 'utf8', ('"' + $scriptPath + '"'),
    '--input', ('"' + $InputPath + '"'), '--threads', $Threads.ToString(), '--batch-size', $BatchSize.ToString())
$worker = Start-Process -FilePath $pythonPath -ArgumentList $processArguments `
    -WorkingDirectory $repoRoot -WindowStyle Hidden -RedirectStandardInput $stdinPath `
    -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
$launch = [ordered]@{ launcher_pid=$worker.Id; output=$outputPath; status=$statusPath; stdout=$stdoutPath; stderr=$stderrPath }
$launch | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputPath 'launch.json') -Encoding UTF8
$launch | ConvertTo-Json
