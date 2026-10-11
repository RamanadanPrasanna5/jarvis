param([ValidateSet('listen','speak')][string]$Mode, [string]$TextBase64='')
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Speech
try {
    if ($Mode -eq 'speak') {
        $speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
        try {
            $speaker.SetOutputToDefaultAudioDevice()
            $speaker.Speak([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($TextBase64)))
        } finally { $speaker.Dispose() }
    } else {
        $info = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers() | Where-Object { $_.Culture.TwoLetterISOLanguageName -eq 'en' } | Select-Object -First 1
        if (-not $info) { throw 'No installed English speech recognizer.' }
        $engine = New-Object System.Speech.Recognition.SpeechRecognitionEngine($info)
        try {
            $engine.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
            $engine.SetInputToDefaultAudioDevice()
            $engine.InitialSilenceTimeout = [TimeSpan]::FromSeconds(6)
            $engine.BabbleTimeout = [TimeSpan]::FromSeconds(10)
            $result = $engine.Recognize([TimeSpan]::FromSeconds(12))
            if ($result -and $result.Confidence -ge 0.45) { [Console]::Write($result.Text) }
        } finally { $engine.Dispose() }
    }
} catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }
