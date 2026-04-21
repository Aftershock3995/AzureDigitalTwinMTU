$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://*:8000/")

$listener.Start()
Write-Host "Server running on port 8000..."

while ($listener.IsListening) {
    try {
        $context = $listener.GetContext()
        $response = $context.Response

        $file = $context.Request.Url.LocalPath.TrimStart("/")

        $path = Join-Path (Get-Location) $file

        $bytes = $null

        if (Test-Path $path) {

            for ($i = 0; $i -lt 5; $i++) {
                try {
                    $fs = [System.IO.File]::Open($path, 'Open', 'Read', 'ReadWrite')

                    $reader = New-Object System.IO.StreamReader($fs)
                    $content = $reader.ReadToEnd()

                    $reader.Close()
                    $fs.Close()

                    $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
                    break
                }
                catch {
                    Start-Sleep -Milliseconds 10
                }
            }
        }

        if ($bytes -ne $null) {
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        }
        else {
            $msg = [System.Text.Encoding]::UTF8.GetBytes("ERROR: FILE NOT READY")
            $response.OutputStream.Write($msg, 0, $msg.Length)
        }

        $response.Close()
    }
    catch {
        Write-Host "Error handling request: $_"
    }
}
