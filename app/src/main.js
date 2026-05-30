import { invoke } from "@tauri-apps/api/core";
import { open as openDialog, save as saveDialog } from "@tauri-apps/plugin-dialog";
import { writeTextFile } from "@tauri-apps/plugin-fs";

const drop = document.getElementById("drop");
const pick = document.getElementById("pick");
const strip = document.getElementById("strip");
const status = document.getElementById("status");
const result = document.getElementById("result");
const output = document.getElementById("output");
const copyBtn = document.getElementById("copy");
const saveBtn = document.getElementById("save");

let lastMarkdown = "";

function showStatus(msg, isError = false) {
  status.hidden = false;
  status.textContent = msg;
  status.classList.toggle("error", isError);
}

function hideStatus() {
  status.hidden = true;
  status.classList.remove("error");
}

async function convert(path) {
  hideStatus();
  result.hidden = true;
  showStatus(`Converting ${path}...`);
  try {
    const markdown = await invoke("convert_file", {
      path,
      stripBoilerplate: strip.checked,
    });
    lastMarkdown = markdown;
    output.textContent = markdown;
    result.hidden = false;
    hideStatus();
  } catch (err) {
    showStatus(String(err), true);
  }
}

pick.addEventListener("click", async () => {
  const selected = await openDialog({ multiple: false, directory: false });
  if (typeof selected === "string") {
    await convert(selected);
  }
});

// Tauri delivers file drops via the OS; the webview also fires the events,
// but on Tauri 2 we use the webview drag-drop wiring (configured in tauri.conf.json).
drop.addEventListener("dragover", (e) => {
  e.preventDefault();
  drop.classList.add("dragover");
});
drop.addEventListener("dragleave", () => drop.classList.remove("dragover"));
drop.addEventListener("drop", (e) => {
  e.preventDefault();
  drop.classList.remove("dragover");
  // The webview drop event itself doesn't expose a usable native path on
  // Tauri 2; users should drop onto the window (handled by the runtime),
  // or use the Browse button. We surface a hint instead of failing silently.
  showStatus(
    "Drop the file anywhere on the window, or use the Browse button.",
  );
});

// Tauri 2 file-drop event from the webview window.
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
const appWindow = getCurrentWebviewWindow();
appWindow.onDragDropEvent(async (event) => {
  if (event.payload.type === "drop" && event.payload.paths.length > 0) {
    drop.classList.remove("dragover");
    await convert(event.payload.paths[0]);
  } else if (event.payload.type === "over") {
    drop.classList.add("dragover");
  } else {
    drop.classList.remove("dragover");
  }
});

copyBtn.addEventListener("click", async () => {
  await navigator.clipboard.writeText(lastMarkdown);
  showStatus("Copied to clipboard.");
  setTimeout(hideStatus, 1500);
});

saveBtn.addEventListener("click", async () => {
  const target = await saveDialog({
    defaultPath: "output.md",
    filters: [{ name: "Markdown", extensions: ["md"] }],
  });
  if (target) {
    await writeTextFile(target, lastMarkdown);
    showStatus(`Saved to ${target}`);
    setTimeout(hideStatus, 2000);
  }
});
