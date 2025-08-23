# King-III

To start the server:
run
```bash
npm run build
```
Then, inside `\dist\sample_project\src\config.js` 
Replace
```js
dotenv.config();
```
with
```js
const envPath = path.resolve(import.meta.dirname, "../.env");

dotenv.config({
    path: path.resolve(envPath, '../.env')
});
```

Then run
```bash
npm start
```

In another terminal, run
`./invoke-mcp-initializer.ps1` to get the mcp-server-session id
The server is hosted on default PORT=9900, which can be set through modifying your `.env` args