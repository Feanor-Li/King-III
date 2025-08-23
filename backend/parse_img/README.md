# Start python tool server locally
To start the python tool server locally,
first run:
```bash
uvicorn app:app --reload --port <PORT>
```
Then in another terminal run:
```bash
curl -X POST http://localhost:8080/chat -H "Content-Type: application/json"   -d '{"message":"Explain transformers briefly."}'
```
The user message above really doesnt matter for now, you should expect this function to
produce 
```
{"text":"15 + 29 = 44"}
```