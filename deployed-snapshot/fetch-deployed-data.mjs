// Script kéo dữ liệu từ dự án đã deploy qua gateway (socket.io, XTransformPort=3030)
import { io } from "socket.io-client";

const URL = "https://q1nwx7kyrqx1-d.space-z.ai/";

const socket = io(URL, {
  query: { XTransformPort: "3030" },
  transports: ["websocket", "polling"],
  reconnection: false,
  timeout: 15000,
});

const results = {};
const timeout = setTimeout(() => {
  console.error("TIMEOUT - dumping partial results");
  console.log(JSON.stringify(results, null, 2));
  process.exit(1);
}, 20000);

socket.on("connect", () => {
  console.error("[connected] sid =", socket.id);
  socket.emit("agents:list");
  socket.emit("history:get", { limit: 100 });
});

socket.on("agents:data", (data) => {
  results.agents = data;
  console.error("[agents:data] received, keys:", Object.keys(data ?? {}));
  maybeFinish();
});

socket.on("history:data", (data) => {
  results.history = data;
  console.error("[history:data] received, keys:", Object.keys(data ?? {}));
  maybeFinish();
});

socket.on("connect_error", (err) => {
  console.error("[connect_error]", err.message);
});

function maybeFinish() {
  if (results.agents !== undefined && results.history !== undefined) {
    clearTimeout(timeout);
    console.log(JSON.stringify(results, null, 2));
    socket.disconnect();
    process.exit(0);
  }
}
