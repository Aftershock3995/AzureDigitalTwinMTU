$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://+:8000/")
$listener.Start()

Write-Host "Server running on port 8000..."

while ($listener.IsListening) {
    try {
        $context = $listener.GetContext()
        $response = $context.Response

        # Always serve coords.txt
        $path = Join-Path (Get-Location) "coords.txt"

        if (Test-Path $path) {
            $content = Get-Content $path
        } else {
            $content = "0,0,0"
        }

        $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
        $response.ContentLength64 = $bytes.Length
        $response.OutputStream.Write($bytes, 0, $bytes.Length)
        $response.OutputStream.Close()

    } catch {
        Write-Host "Error: $($_.Exception.Message)"
    }
}
