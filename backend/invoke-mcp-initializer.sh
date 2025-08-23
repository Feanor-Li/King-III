port="${PORT:-8080}"
SESSION_ID="$(
  curl -sS -D - -o /dev/null \
    -H "Accept: application/json, text/event-stream" \
    -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","id":"1","method":"initialize","params":{"protocolVersion":"2025-03-26","clientInfo":{"name":"local-test","version":"0.0.1"},"capabilities":{}}}' \
    "http://localhost:${port}/mcp" \
  | tr -d '\r' | awk 'BEGIN{IGNORECASE=1}/^mcp-session-id:/{sub(/^[^:]*:[[:space:]]*/,""); print; exit}'
)"
echo "$SESSION_ID"
