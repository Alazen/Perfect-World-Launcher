import { invoke } from "@tauri-apps/api/core";
import { open as openDialog } from "@tauri-apps/plugin-dialog";
import { listen } from "@tauri-apps/api/event";

// --- Types mapping to Rust models ---
type Account = {
    run: boolean;
    login: string;
    password: string;
    character: string;
};

type Server = {
    name: string;
    client_path: string;
    accounts: Account[];
};

type Settings = {
    delay: number;
    servers: Server[];
};

// --- State Management ---
let currentState: Settings = { delay: 3, servers: [] };
let logVisible = false;

// --- DOM Elements ---
const appEl = document.getElementById("app")!;

// --- Initialization ---
window.addEventListener("DOMContentLoaded", async () => {
    try {
        currentState = await invoke("get_config");
        setupLogListener();
        render();
    } catch (e) {
        console.error("Failed to load settings from Rust backend:", e);
    }
});

// --- Debounced save ---
let saveTimeout: number | undefined;
function requestSave() {
    if (saveTimeout) clearTimeout(saveTimeout);
    saveTimeout = window.setTimeout(async () => {
        try {
            await invoke("save_config", { newConfig: currentState });
            logMsg("Settings saved automatically.", "success");
        } catch (e) {
            logMsg(`Failed to save settings: ${e}`, "error");
        }
    }, 1000);
}

function fullReRender() {
    requestSave();
    render();
}

// --- Render Engine ---
function render() {
    let activeAccountsCount = 0;
    currentState.servers.forEach(s => {
        s.accounts.forEach(a => { if (a.run) activeAccountsCount++; });
    });

    appEl.innerHTML = `
        <header>
            <div class="title-area">
                <h2>Perfect World Launcher</h2>
                <p>Manage multiple accounts and servers seamlessly</p>
            </div>
            <div class="controls-area">
                <button id="btn-import">Import Settings</button>
                <button id="btn-export">Export Settings</button>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <label style="font-size: 13px; color: var(--text-muted)">Delay (s):</label>
                    <input type="number" id="input-delay" style="width: 60px" value="${currentState.delay}" min="0" max="60" />
                </div>
            </div>
        </header>

        <main class="content-area" id="server-list"></main>

        <footer>
            <button id="btn-start-all" class="btn-success">Start ${activeAccountsCount} accounts</button>
            <div style="display: flex; gap: 12px">
                <button id="btn-add-server" class="btn-primary">Add Server</button>
                <button id="btn-toggle-log">${logVisible ? "Hide Log" : "Show Log"}</button>
            </div>
        </footer>

        <div class="log-panel ${logVisible ? 'visible' : ''}" id="log-panel">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                <span style="font-weight: 600; color: var(--text-white)">Launch Log</span>
                <button id="btn-close-log" style="padding: 2px 8px; font-size: 11px">Close</button>
            </div>
            <div class="log-content" id="log-content"></div>
        </div>
    `;

    // Render Server List
    const serverListEl = document.getElementById("server-list")!;
    currentState.servers.forEach((server, serverIdx) => {

        let accountsHtml = server.accounts.map((acc, accIdx) => `
            <div class="account-row">
                <div class="center"><input type="checkbox" class="run-checkbox" data-srv="${serverIdx}" data-acc="${accIdx}" ${acc.run ? 'checked' : ''} /></div>
                <div><input type="text" style="width: 100%" class="acc-login" data-srv="${serverIdx}" data-acc="${accIdx}" value="${escapeHtml(acc.login)}" placeholder="Login"/></div>
                <div><input type="password" style="width: 100%" class="acc-pass" data-srv="${serverIdx}" data-acc="${accIdx}" value="${escapeHtml(acc.password)}" placeholder="Password"/></div>
                <div><input type="text" style="width: 100%" class="acc-char" data-srv="${serverIdx}" data-acc="${accIdx}" value="${escapeHtml(acc.character)}" placeholder="Character Name"/></div>
                <div class="center"><button class="btn-play-acc" data-srv="${serverIdx}" data-acc="${accIdx}">Play</button></div>
                <div class="center"><button class="btn-danger btn-del-acc" data-srv="${serverIdx}" data-acc="${accIdx}">X</button></div>
            </div>
        `).join("");

        const card = document.createElement("div");
        card.className = "server-card";
        card.innerHTML = `
            <div class="server-header">
                <div class="server-title">
                    <input type="text" class="server-name" data-srv="${serverIdx}" value="${escapeHtml(server.name)}" placeholder="Server Name" />
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn-primary btn-play-srv" data-srv="${serverIdx}">Play ${escapeHtml(server.name)}</button>
                    <button class="btn-danger btn-del-srv" data-srv="${serverIdx}">Remove Server</button>
                </div>
            </div>
            <div class="client-path-row">
                <label style="font-weight: 600; font-size: 13px">Client Path:</label>
                <input type="text" class="server-path" data-srv="${serverIdx}" value="${escapeHtml(server.client_path)}" placeholder="e.g. C:\\Games\\PW\\elementclient.exe"/>
                <button class="btn-browse" data-srv="${serverIdx}">Browse</button>
            </div>
            <div class="accounts-grid">
                <div class="table-header">
                    <div class="center">Run?</div>
                    <div>Login</div>
                    <div>Password</div>
                    <div>Character Name</div>
                    <div class="center">Launch</div>
                    <div class="center">Delete</div>
                </div>
                ${accountsHtml}
            </div>
            <div style="margin-top: 12px;">
                <button class="btn-add-acc" data-srv="${serverIdx}">+ Add Account</button>
            </div>
        `;
        serverListEl.appendChild(card);
    });

    attachListeners();
}

function escapeHtml(unsafe: string) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function logMsg(msg: string, type: 'info' | 'success' | 'error' = 'info') {
    const logContent = document.getElementById("log-content");
    if (!logContent) return;

    let htmlClass = "";
    if (type === 'success') htmlClass = "log-success";
    if (type === 'error') htmlClass = "log-error";

    const d = new Date();
    const timeStr = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;

    const el = document.createElement("div");
    el.className = "log-entry";
    el.innerHTML = `<span class="timestamp">[${timeStr}]</span> <span class="${htmlClass}">${escapeHtml(msg)}</span>`;

    logContent.appendChild(el);
    logContent.scrollTop = logContent.scrollHeight;
}

async function setupLogListener() {
    await listen<string>("launch-log", (payload) => {
        let type: 'info' | 'success' | 'error' = 'info';
        if (payload.payload.toLowerCase().includes("success")) type = 'success';
        if (payload.payload.toLowerCase().includes("fail")) type = 'error';
        logMsg(payload.payload, type);
    });
}

// --- Event Binding ---
function attachListeners() {
    // Top Controls
    document.getElementById("input-delay")?.addEventListener("input", (e) => {
        currentState.delay = parseInt((e.target as HTMLInputElement).value) || 0;
        requestSave();
    });

    document.getElementById("btn-toggle-log")?.addEventListener("click", () => {
        logVisible = !logVisible;
        render(); // Cheap enough to re-render for UI updates
    });

    document.getElementById("btn-close-log")?.addEventListener("click", () => {
        logVisible = false;
        render();
    });

    // Server list actions
    document.getElementById("btn-add-server")?.addEventListener("click", () => {
        currentState.servers.push({ name: "New Server", client_path: "", accounts: [] });
        fullReRender();
    });

    document.querySelectorAll(".btn-del-srv").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const idx = parseInt((e.target as HTMLElement).getAttribute("data-srv")!);
            currentState.servers.splice(idx, 1);
            fullReRender();
        });
    });

    // Account list actions
    document.querySelectorAll(".btn-add-acc").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const idx = parseInt((e.target as HTMLElement).getAttribute("data-srv")!);
            currentState.servers[idx].accounts.push({ run: true, login: "", password: "", character: "" });
            fullReRender();
        });
    });

    document.querySelectorAll(".btn-del-acc").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const srv = parseInt((e.target as HTMLElement).getAttribute("data-srv")!);
            const acc = parseInt((e.target as HTMLElement).getAttribute("data-acc")!);
            currentState.servers[srv].accounts.splice(acc, 1);
            fullReRender();
        });
    });

    // Input bindings (Debounced data save)
    const bindInput = (className: string, field: keyof Account | keyof Server | 'run') => {
        document.querySelectorAll(`.${className}`).forEach(el => {
            el.addEventListener("input", (e) => {
                const target = e.target as HTMLInputElement;
                const srv = parseInt(target.getAttribute("data-srv")!);
                const accAttr = target.getAttribute("data-acc");

                if (accAttr !== null) {
                    const acc = parseInt(accAttr);
                    if (field === 'run') {
                        currentState.servers[srv].accounts[acc].run = target.checked;
                        fullReRender(); // Re-render to update the total start button count
                    } else {
                        // @ts-ignore
                        currentState.servers[srv].accounts[acc][field] = target.value;
                        requestSave();
                    }
                } else {
                    // @ts-ignore
                    currentState.servers[srv][field] = target.value;
                    requestSave();
                }
            });
        });
    };

    bindInput("server-name", "name");
    bindInput("server-path", "client_path");
    bindInput("acc-login", "login");
    bindInput("acc-pass", "password");
    bindInput("acc-char", "character");
    bindInput("run-checkbox", "run");

    // Rust OS Interactions
    document.querySelectorAll(".btn-browse").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const srv = parseInt((e.target as HTMLElement).getAttribute("data-srv")!);
            const selected = await openDialog({
                multiple: false,
                directory: false,
                filters: [{ name: 'Executable', extensions: ['exe'] }]
            });
            if (selected && typeof selected === 'string') {
                currentState.servers[srv].client_path = selected;
                fullReRender();
            }
        });
    });

    document.getElementById("btn-start-all")?.addEventListener("click", async () => {
        logVisible = true; render();
        logMsg("Starting global sequential launch...");
        await invoke("launch_all");
    });

    document.querySelectorAll(".btn-play-srv").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const srv = parseInt((e.target as HTMLElement).getAttribute("data-srv")!);
            logVisible = true; render();
            logMsg(`Starting server ${currentState.servers[srv].name}...`);
            await invoke("launch_server", { serverIndex: srv });
        });
    });

    document.querySelectorAll(".btn-play-acc").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const target = e.target as HTMLElement;
            const srv = parseInt(target.getAttribute("data-srv")!);
            const acc = parseInt(target.getAttribute("data-acc")!);
            logVisible = true; render();
            logMsg(`Launching ${currentState.servers[srv].accounts[acc].character}...`);
            await invoke("launch_account", { serverIndex: srv, accountIndex: acc });
        });
    });
}
