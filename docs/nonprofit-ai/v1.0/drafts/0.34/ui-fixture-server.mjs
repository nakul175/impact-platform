import {createServer} from "vite";
const server=await createServer({root:"/private/tmp/tola-ai-portability-draft",configFile:false,server:{host:"127.0.0.1",port:8190,strictPort:true},esbuild:{jsx:"automatic"}});
await server.listen();console.log("Synthetic request fixture ready at http://127.0.0.1:8190");
