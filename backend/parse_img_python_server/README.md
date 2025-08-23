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

In order to use the image processing, set up the environment by installing
```bash
pip install fastapi uvicorn python-multipart
pip install anthropic
```
Then, start the server as expected and send request using
```bash
 curl -X POST "http://localhost:8080/img/claude"  -F "prompt=Summarize this chart"   -F "image=@<Your Img Path>"
```

Sample Img Path on windows: `C:\Users\Alice\Pictures\image.jpg`
Sample Img Path on Mac: `/Users/alice/Pictures/image.jpg`