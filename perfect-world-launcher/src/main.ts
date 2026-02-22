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
let currentState: Settings = { delay: 5, servers: [] };
let logVisible = false;
let expandedServers: Set<number> = new Set([0]);

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
        <header style="background: transparent; border: none; box-shadow: none; padding: 24px 32px 12px 32px;">
            <div style="display: flex; gap: 12px; align-items: center; justify-content: flex-start; width: 100%;">
                <button id="btn-add-server">Add Server</button>
                
                <div style="display: flex; align-items: center; margin-left: auto;">
                    <label style="font-size: 12px; color: var(--text-muted); font-weight: 500; margin-right: 12px;">Delay (s):</label>
                    <span style="font-size: 13px; width: 16px; text-align: center; color: var(--text-white); font-weight: 600; margin-right: 12px;">${currentState.delay}</span>
                    <div style="display: flex; align-items: center; background: var(--btn-surface); border-radius: 9999px; overflow: hidden; border: 1px solid var(--border-subtle);">
                        <button id="btn-delay-dec" style="padding: 0; width: 40px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 16px; border-radius: 0; border: none; background: transparent; border-right: 1px solid rgba(255,255,255,0.05);">-</button>
                        <button id="btn-delay-inc" style="padding: 0; width: 40px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 16px; border-radius: 0; border: none; background: transparent;">+</button>
                    </div>
                </div>
            </div>
        </header>

        <main class="content-area" id="server-list" style="padding: 0 32px;"></main>

        <footer style="background: transparent; border: none; box-shadow: none; padding: 16px 32px 32px 32px; display: flex; gap: 12px; align-items: stretch;">
            <button id="btn-start-all" class="btn-success" style="flex: 1.5; font-size: 16px; box-shadow: 0 4px 14px rgba(48, 213, 252, 0.2);">Start ${activeAccountsCount} accounts</button>
            <button id="btn-import" style="flex: 1;">Import Settings</button>
            <button id="btn-export" style="flex: 1;">Export Settings</button>
            <button id="btn-save-close" style="flex: 1;">Save and Close</button>
            <button id="btn-toggle-log" style="flex: 1;">${logVisible ? "Hide Log" : "Show Log"}</button>
        </footer>

        <div class="log-panel ${logVisible ? 'visible' : ''}" id="log-panel" style="bottom: 90px; left: 32px; width: 400px; background: #16181A; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 40px rgba(0,0,0,0.8);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                <span style="font-weight: 600; color: var(--text-white)">Launch Log</span>
                <button id="btn-close-log" style="padding: 2px 8px; font-size: 11px">Close</button>
            </div>
            <div class="log-content" id="log-content"></div>
        </div>
        <div style="position: absolute; bottom: 12px; left: 32px; font-size: 12px; color: var(--text-muted); font-family: monospace;" id="mini-log">
            [${new Date().toLocaleTimeString('en-GB')}] Settings loaded
        </div>
    `;

    // Render Server List
    const serverListEl = document.getElementById("server-list")!;
    currentState.servers.forEach((server, serverIdx) => {
        const isExpanded = expandedServers.has(serverIdx);

        let accountsHtml = server.accounts.map((acc, accIdx) => `
            <div class="account-row">
                <div class="center"><input type="checkbox" class="run-checkbox" data-srv="${serverIdx}" data-acc="${accIdx}" ${acc.run ? 'checked' : ''} /></div>
                <div class="center"><button class="btn-primary btn-play-acc" data-srv="${serverIdx}" data-acc="${accIdx}" style="width: 100%; border-radius: 9999px;">Play</button></div>
                <div><input type="text" class="acc-login" data-srv="${serverIdx}" data-acc="${accIdx}" value="${escapeHtml(acc.login)}" placeholder="Login"/></div>
                <div><input type="password" class="acc-pass" data-srv="${serverIdx}" data-acc="${accIdx}" value="${escapeHtml(acc.password)}" placeholder="Password"/></div>
                <div><input type="text" class="acc-char" data-srv="${serverIdx}" data-acc="${accIdx}" value="${escapeHtml(acc.character)}" placeholder="Character"/></div>
                <div class="center"><button class="btn-danger btn-del-acc" data-srv="${serverIdx}" data-acc="${accIdx}" style="width: 100%; border-radius: 9999px; background: var(--btn-surface); color: white;">Remove</button></div>
            </div>
        `).join("");

        const card = document.createElement("div");
        card.className = "server-card";

        const toggleBtnText = isExpanded ? "Hide" : "Show";

        let innerHTML = `
            <div class="server-header" style="transition: margin-bottom var(--md-sys-motion-duration-medium4) var(--md-sys-motion-easing-emphasized); margin-bottom: ${isExpanded ? '24px' : '0'}; display: flex; gap: 16px; align-items: center; justify-content: flex-start;">
                <button class="btn-toggle-srv" data-srv="${serverIdx}" style="background: var(--btn-surface); border: none; font-weight: 700; border-radius: 9999px; color: white; width: 100px;">${toggleBtnText}</button>
                <input type="text" class="server-name" data-srv="${serverIdx}" value="${escapeHtml(server.name)}" placeholder="Server name" style="flex: 1; max-width: 600px; background: var(--bg-input); font-size: 13px; border: 1px solid rgba(255,255,255,0.03); border-radius: 9999px;" />
                <button class="btn-primary btn-play-srv" data-srv="${serverIdx}" style="font-size: 13px; font-weight: 700; border-radius: 9999px;">Play ${escapeHtml(server.name)}</button>
                <button class="btn-danger btn-del-srv" data-srv="${serverIdx}" style="font-size: 13px; border-radius: 9999px; background: var(--btn-surface); color: white;">Remove ${escapeHtml(server.name)}</button>
            </div>
            
            <div class="expand-container ${isExpanded ? 'expanded' : ''}">
                <div class="expand-content">
                    <div class="client-path-row" style="background: transparent; padding: 0; margin-bottom: 24px; border: none; gap: 16px;">
                        <label style="font-weight: 600; font-size: 12px; color: var(--text-muted); white-space: nowrap; width: 140px; text-align: left; padding-left: 12px;">Client Path Server ${serverIdx + 1}:</label>
                        <input type="text" class="server-path" data-srv="${serverIdx}" value="${escapeHtml(server.client_path)}" placeholder="Select elementclient.exe" style="flex: 1; max-width: -webkit-fill-available; background: var(--bg-input); border: 1px solid rgba(255,255,255,0.03); padding: 0 16px; height: 40px; border-radius: 9999px;"/>
                        <button class="btn-browse" data-srv="${serverIdx}" style="background: var(--btn-surface); border: none; font-weight: 600; border-radius: 9999px; color: white;">Browse</button>
                    </div>
                
                    <div class="accounts-grid" style="border: none; background: transparent;">
                        <div class="table-header">
                            <div class="center">Run?</div>
                            <div class="center">Play</div>
                            <div>Login</div>
                            <div>Password</div>
                            <div>Character</div>
                            <div class="center">Remove</div>
                        </div>
                        ${accountsHtml}
                    </div>
                    <div style="margin-top: 24px;">
                        <button class="btn-add-acc" data-srv="${serverIdx}" style="background: var(--btn-surface); border: none; font-weight: 600; border-radius: 9999px; color: white;">Add Account</button>
                    </div>
                    <div style="margin-top: 32px; border-top: 1px solid rgba(255,255,255,0.02); margin-left: -24px; margin-right: -24px; margin-bottom: -24px;"></div>
                </div>
            </div>
        `;

        card.innerHTML = innerHTML;
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
    const timeStr = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')} `;

    const el = document.createElement("div");
    el.className = "log-entry";
    el.innerHTML = `< span class="timestamp" > [${timeStr}] < /span> <span class="${htmlClass}">${escapeHtml(msg)}</span > `;

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
    document.getElementById("btn-delay-inc")?.addEventListener("click", () => {
        currentState.delay = Math.min(60, currentState.delay + 1);
        fullReRender();
    });

    document.getElementById("btn-delay-dec")?.addEventListener("click", () => {
        currentState.delay = Math.max(0, currentState.delay - 1);
        fullReRender();
    });

    document.getElementById("btn-save-close")?.addEventListener("click", async () => {
        try {
            await invoke("save_config", { newConfig: currentState });
            window.close(); // or appWindow.close() from tauri API
        } catch (e) {
            logMsg(`Failed to save settings: ${e} `, "error");
        }
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
    document.querySelectorAll(".btn-toggle-srv").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const idx = parseInt((e.target as HTMLElement).getAttribute("data-srv")!);
            const targetBtn = e.target as HTMLElement;
            const serverCard = targetBtn.closest(".server-card");
            const expandContainer = serverCard?.querySelector(".expand-container");
            const header = serverCard?.querySelector(".server-header") as HTMLElement;

            if (expandedServers.has(idx)) {
                expandedServers.delete(idx);
                targetBtn.innerText = "Show";
                if (expandContainer) expandContainer.classList.remove("expanded");
                if (header) header.style.marginBottom = "0";
            } else {
                expandedServers.add(idx);
                targetBtn.innerText = "Hide";
                if (expandContainer) expandContainer.classList.add("expanded");
                if (header) header.style.marginBottom = "24px";
            }
            // Skipping render() call to allow CSS grid transitions to run
        });
    });
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
        document.querySelectorAll(`.${className} `).forEach(el => {
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
