$port = if ($Env:PORT) { $Env:PORT } else { 9900 }

$body = @'
{
  "jsonrpc":"2.0",
  "id":"1",
  "method":"initialize",
  "params":{
    "protocolVersion":"2025-03-26",
    "clientInfo":{"name":"local-test","version":"0.0.1"},
    "capabilities":{}
  }
}
'@

# Use Invoke-WebRequest (shows headers), and advertise both content types
$r = Invoke-WebRequest -Uri "http://localhost:$port/mcp" `
  -Method Post `
  -Headers @{ Accept = "application/json, text/event-stream" } `
  -ContentType "application/json" `
  -Body $body

$sessionId = $r.Headers['Mcp-Session-Id']  # header key is case-insensitive
$sessionId