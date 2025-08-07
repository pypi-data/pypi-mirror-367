globalThis.requestBackend = async function (method, payload = null) {
  return await fetch(`/__method__/${method}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
};

// page events listener register
window.addEventListener("pagehide", (e) => {
  if (e.persisted) return;
  navigator.sendBeacon("/__event__/page_closed")
});
window.addEventListener("DOMContentLoaded", () => {
  fetch("/__event__/page_loaded", { method: "POST" })
});

// start SSE client
const eventSource = new EventSource("/__sse__");
eventSource.onerror = function (err) {
  console.error("EventSource failed:", err);
};
globalThis.backendListener = {
  on: (event, callback) => {
    eventSource.addEventListener(event, (e) => {
      callback(e.data);
    });
  },
  off: (event, callback) => {
    eventSource.removeEventListener(event, callback);
  },
  once: (event, callback) => {
    eventSource.addEventListener(event, callback, {
      once: true
    });
  },
};
