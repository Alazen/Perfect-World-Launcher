import { invoke } from "@tauri-apps/api/core";
import { open as openDialog, save as saveDialog } from "@tauri-apps/plugin-dialog";
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

// Internal UI state flags
type AccountWithUIState = Account & {
    _isNew?: boolean;
    _isRemoving?: boolean;
};

type ServerWithUIState = Omit<Server, 'accounts'> & {
    accounts: AccountWithUIState[];
    _isNew?: boolean;
    _isRemoving?: boolean;
    _removeHeight?: number;
};

type Settings = {
    delay: number;
    servers: ServerWithUIState[];
};

// --- State Management ---
let currentState: Settings = { delay: 5, servers: [] };
let logVisible = false;
let expandedServers: Set<number> = new Set([0]);

// --- DOM Elements ---
const appEl = document.getElementById("app")!;

// --- Initialization ---
window.addEventListener("DOMContentLoaded", async () => {
    // Prevent default drag and drop behaviors on the window to allow our custom drag/drop to work inside the app
    window.addEventListener("dragover", (e) => e.preventDefault());
    window.addEventListener("drop", (e) => e.preventDefault());

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



function updateStartAllButton() {
    let activeAccountsCount = 0;
    currentState.servers.forEach(s => {
        s.accounts.forEach(a => { if (a.run) activeAccountsCount++; });
    });
    const btn = document.getElementById("btn-start-all");
    if (btn) btn.innerText = `Start ${activeAccountsCount} accounts`;
}

function setLogVisible(visible: boolean) {
    logVisible = visible;
    const panel = document.getElementById("log-panel");
    const btn = document.getElementById("btn-toggle-log");
    if (visible) {
        panel?.classList.add("visible");
        if (btn) btn.innerText = "Hide Log";
    } else {
        panel?.classList.remove("visible");
        if (btn) btn.innerText = "Show Log";
    }
}

// --- Render Engine ---
function render() {
    const oldServerListEl = document.getElementById("server-list");
    const preservedScrollTop = oldServerListEl ? oldServerListEl.scrollTop : 0;

    let activeAccountsCount = 0;
    currentState.servers.forEach(s => {
        s.accounts.forEach(a => { if (a.run) activeAccountsCount++; });
    });

    appEl.innerHTML = `
        <header style="background: transparent; border: none; box-shadow: none; padding: 24px 42px 12px 32px;">
            <div style="display: flex; gap: 12px; align-items: center; justify-content: flex-start; width: 100%;">
                <button id="btn-add-server">Add Server</button>
                
                <div style="display: flex; align-items: center; margin-left: auto;">
                    <label style="font-size: 12px; color: var(--text-muted); font-weight: 500; margin-right: 12px;">Delay (s):</label>
                    <span id="delay-val" style="font-size: 13px; width: 16px; text-align: center; color: var(--text-white); font-weight: 600; margin-right: 12px;">${currentState.delay}</span>
                    <div style="display: flex; align-items: center; background: var(--btn-surface); border-radius: 9999px; overflow: hidden; border: 1px solid var(--border-subtle); height: 40px;">
                        <button id="btn-delay-dec" style="padding: 0; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 16px; border-radius: 0; border: none; border-right: 1px solid rgba(255,255,255,0.05);"><span style="margin-top: -2px;">-</span></button>
                        <button id="btn-delay-inc" style="padding: 0; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 16px; border-radius: 0; border: none;"><span style="margin-top: -2px;">+</span></button>
                    </div>
                </div>
            </div>
        </header>

        <main class="content-area" id="server-list"></main>

        <footer style="background: transparent; border: none; box-shadow: none; padding: 16px 42px 32px 32px; display: flex; gap: 12px; align-items: stretch; position: relative; flex-shrink: 0;">
            <button id="btn-start-all" class="btn-success" style="flex: 1.5; box-shadow: 0 4px 14px rgba(48, 213, 252, 0.2);">Start ${activeAccountsCount} accounts</button>
            <button id="btn-import" style="flex: 1;">Import Settings</button>
            <button id="btn-export" style="flex: 1;">Export Settings</button>
            <button id="btn-save-close" style="flex: 1;">Save and Close</button>
            <button id="btn-toggle-log" style="flex: 1;">${logVisible ? "Hide Log" : "Show Log"}</button>
            
            <div style="position: absolute; bottom: 8px; right: 42px; font-size: 12px; color: var(--text-muted); font-family: monospace; text-align: right; pointer-events: none;" id="mini-log">
                [${new Date().toLocaleTimeString('en-GB')}] Settings loaded
            </div>
        </footer>

        <div class="log-panel ${logVisible ? 'visible' : ''}" id="log-panel">
            <div class="log-content" id="log-content"></div>
        </div>
    `;

    // Render Server List
    const serverListEl = document.getElementById("server-list")!;
    currentState.servers.forEach((server, serverIdx) => {
        const isExpanded = expandedServers.has(serverIdx);

        let accountsHtml = server.accounts.map((acc, accIdx) => {
            let rowClass = "account-row";
            if (acc._isNew) rowClass += " slide-down-in";
            else if (acc._isRemoving) rowClass += " slide-up-out";

            return `
            <div class="${rowClass}">
                <div class="center"><input type="checkbox" class="run-checkbox" data-srv="${serverIdx}" data-acc="${accIdx}" ${acc.run ? 'checked' : ''} /></div>
                <div class="center"><button class="btn-primary btn-play-acc" data-srv="${serverIdx}" data-acc="${accIdx}" style="width: 100%; border-radius: 9999px;">Play</button></div>
                <div><input type="text" class="acc-login" data-srv="${serverIdx}" data-acc="${accIdx}" value="${escapeHtml(acc.login)}" placeholder="Login"/></div>
                <div><input type="password" class="acc-pass" data-srv="${serverIdx}" data-acc="${accIdx}" value="${escapeHtml(acc.password)}" placeholder="Password"/></div>
                <div><input type="text" class="acc-char" data-srv="${serverIdx}" data-acc="${accIdx}" value="${escapeHtml(acc.character)}" placeholder="Character"/></div>
                <div class="center"><button class="btn-danger btn-del-acc" data-srv="${serverIdx}" data-acc="${accIdx}" style="width: 100%; border-radius: 9999px; color: white;">Remove</button></div>
            </div>
            `;
        }).join("");

        let cardClass = "server-card";
        let cardStyle = "";
        if (server._isNew) {
            cardClass += " slide-down-in";
        } else if (server._isRemoving) {
            cardClass += " slide-up-out";
            if (server._removeHeight) {
                cardStyle = `--removal-height: ${server._removeHeight}px;`;
            }
        }

        const card = document.createElement("div");
        card.className = cardClass;
        if (cardStyle) card.style.cssText = cardStyle;
        card.draggable = true;
        card.dataset.srvIndex = serverIdx.toString();

        const toggleBtnText = isExpanded ? "Hide" : "Show";

        let innerHTML = `
            <div class="server-header" style="transition: margin-bottom var(--md-sys-motion-duration-medium4) var(--md-sys-motion-easing-emphasized); margin-bottom: ${isExpanded ? '24px' : '0'}; display: flex; gap: 16px; align-items: center; justify-content: flex-start;">
                <button class="btn-toggle-srv" data-srv="${serverIdx}" style="border: none; font-weight: 700; border-radius: 9999px; color: white; width: 100px;">${toggleBtnText}</button>
                <input type="text" class="server-name" data-srv="${serverIdx}" value="${escapeHtml(server.name)}" placeholder="Server name" style="flex: 1; font-size: 13px; border-radius: 9999px;" />
                <button class="btn-primary btn-play-srv" data-srv="${serverIdx}" style="font-size: 13px; font-weight: 700; border-radius: 9999px;">Play ${escapeHtml(server.name)}</button>
            </div>
            
            <div class="expand-container ${isExpanded ? 'expanded' : ''}">
                <div class="expand-content">
                    <div class="client-path-row" style="background: transparent; padding: 4px 0; margin-bottom: 24px; border: none; gap: 16px;">
                        <label style="font-weight: 600; font-size: 12px; color: var(--text-muted); white-space: nowrap; width: 140px; text-align: left; padding-left: 12px;">Client Path Server ${serverIdx + 1}:</label>
                        <input type="text" class="server-path" data-srv="${serverIdx}" value="${escapeHtml(server.client_path)}" placeholder="Select elementclient.exe" style="flex: 1; max-width: -webkit-fill-available; padding: 0 16px; height: 40px; border-radius: 9999px;"/>
                        <button class="btn-browse" data-srv="${serverIdx}" style="border: none; font-weight: 600; border-radius: 9999px; color: white;">Browse</button>
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
                    <div style="margin-top: 24px; display: flex; gap: 12px; align-items: center;">
                        <button class="btn-add-acc" data-srv="${serverIdx}" style="border: none; font-weight: 600; border-radius: 9999px; color: white;">Add Account</button>
                        <button class="btn-server-launcher" data-srv="${serverIdx}" style="border: none; font-weight: 600; border-radius: 9999px; color: white;">Server Launcher</button>
                        <button class="btn-danger btn-del-srv" data-srv="${serverIdx}" style="font-size: 13px; border: none; font-weight: 600; border-radius: 9999px; color: white;">Remove ${escapeHtml(server.name)}</button>
                    </div>
                    <div style="margin-top: 24px; border-top: 1px solid rgba(255,255,255,0.02); margin-left: -24px; margin-right: -24px; margin-bottom: -24px;"></div>
                </div>
            </div>
        `;

        card.innerHTML = innerHTML;
        serverListEl.appendChild(card);

        // Add interactive class slightly after render to avoid initial transition glitch
        setTimeout(() => card.classList.add("interactive"), 50);
    });

    attachListeners();

    const newServerListEl = document.getElementById("server-list");
    if (newServerListEl) {
        newServerListEl.scrollTop = preservedScrollTop;
    }
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
    el.innerHTML = `<span class="timestamp">[${timeStr}] </span><span class="${htmlClass}">${escapeHtml(msg)}</span>`;

    logContent.appendChild(el);
    logContent.scrollTop = logContent.scrollHeight;
}

async function setupLogListener() {
    await listen<string>("launch-log", (payload) => {
        let type: 'info' | 'success' | 'error' = 'info';
        const msg = payload.payload.toLowerCase();
        if (msg.includes("success")) type = 'success';
        if (msg.includes("fail") || msg.includes("aborting") || msg.includes("no enabled")) {
            type = 'error';
            setLogVisible(true);
        }
        logMsg(payload.payload, type);
    });
}

// --- Event Binding ---
function attachListeners() {
    // Top Controls
    document.getElementById("btn-delay-inc")?.addEventListener("click", () => {
        currentState.delay = Math.min(60, currentState.delay + 1);
        const span = document.getElementById("delay-val");
        if (span) span.innerText = currentState.delay.toString();
        requestSave();
    });

    document.getElementById("btn-delay-dec")?.addEventListener("click", () => {
        currentState.delay = Math.max(0, currentState.delay - 1);
        const span = document.getElementById("delay-val");
        if (span) span.innerText = currentState.delay.toString();
        requestSave();
    });

    document.getElementById("btn-save-close")?.addEventListener("click", async () => {
        try {
            await invoke("save_config", { newConfig: currentState });
            window.close(); // or appWindow.close() from tauri API
        } catch (e) {
            logMsg(`Failed to save settings: ${e} `, "error");
        }
    });

    document.getElementById("btn-import")?.addEventListener("click", async () => {
        const selected = await openDialog({
            multiple: false,
            directory: false,
            filters: [{ name: 'JSON Config', extensions: ['json'] }]
        });
        if (selected && typeof selected === 'string') {
            try {
                // @ts-ignore
                currentState = await invoke("import_settings_from_file", { path: selected });
                fullReRender();
                logMsg(`Settings imported from ${selected}`, "success");
            } catch (e) {
                logMsg(`Failed to import settings: ${e}`, "error");
            }
        }
    });

    document.getElementById("btn-export")?.addEventListener("click", async () => {
        const selected = await saveDialog({
            filters: [{ name: 'JSON Config', extensions: ['json'] }]
        });
        if (selected && typeof selected === 'string') {
            try {
                await invoke("export_settings_to_file", { path: selected });
                logMsg(`Settings exported to ${selected}`, "success");
            } catch (e) {
                logMsg(`Failed to export settings: ${e}`, "error");
            }
        }
    });

    document.getElementById("btn-toggle-log")?.addEventListener("click", () => {
        setLogVisible(!logVisible);
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
        currentState.servers.push({
            name: "New Server",
            client_path: "",
            accounts: [{ run: true, login: "", password: "", character: "" }],
            _isNew: true
        });
        render();
        const srvIdx = currentState.servers.length - 1;
        setTimeout(() => {
            currentState.servers[srvIdx]._isNew = false;
        }, 400); // Wait for transition
    });

    document.querySelectorAll(".btn-del-srv").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const btnEl = e.target as HTMLElement;
            const idx = parseInt(btnEl.getAttribute("data-srv")!);

            const card = btnEl.closest(".server-card") as HTMLElement;

            if (card) {
                // Get rect before touching anything
                const rect = card.getBoundingClientRect();

                // Create a fixed clone for the visual fade out on top of everything
                const clone = card.cloneNode(true) as HTMLElement;
                clone.style.position = 'fixed';
                clone.style.top = `${rect.top}px`;
                clone.style.left = `${rect.left}px`;
                clone.style.width = `${rect.width}px`;
                clone.style.height = `${rect.height}px`;
                clone.style.margin = '0';
                clone.style.zIndex = '100';
                clone.style.pointerEvents = 'none';
                document.body.appendChild(clone);

                // Hide original card's visible content but KEEP its physical space exactly as is
                card.style.visibility = 'hidden';
                card.style.height = `${rect.height}px`;
                card.style.minHeight = `${rect.height}px`;
                card.style.overflow = 'hidden';
                card.style.transition = "all 400ms var(--md-sys-motion-easing-emphasized)";

                // 1. Kick off the fade on the ghost clone using Web Animations API
                const fadeAnimation = clone.animate([
                    { opacity: 1 },
                    { opacity: 0 }
                ], {
                    duration: 400,
                    easing: 'cubic-bezier(0.2, 0.0, 0, 1.0)', // MD emphasize
                    fill: 'forwards'
                });

                // 2. Wait for fade to finish, then collapse the original card's space
                fadeAnimation.onfinish = () => {
                    if (document.body.contains(clone)) clone.remove();
                    card.style.minHeight = '0px';
                    card.style.height = '0px';
                    card.style.paddingTop = '0px';
                    card.style.paddingBottom = '0px';
                    card.style.marginTop = '0px';
                    card.style.marginBottom = '-12px'; // compensate for flex gap
                    card.style.border = 'none';
                };
            }

            const removingServer = currentState.servers[idx];
            removingServer._isRemoving = true;
            // Native render runs after total animation time (400ms + 400ms + buffer)
            setTimeout(() => {
                const actualIdx = currentState.servers.indexOf(removingServer);
                if (actualIdx !== -1) {
                    currentState.servers.splice(actualIdx, 1);
                    // Adjust expandedServers indexes backwards
                    const newExpanded = new Set<number>();
                    expandedServers.forEach(v => {
                        if (v < actualIdx) newExpanded.add(v);
                        if (v > actualIdx) newExpanded.add(v - 1);
                    });
                    expandedServers = newExpanded;
                }
                render();
            }, 850); // Wait for transition
        });
    });

    // Account list actions
    document.querySelectorAll(".btn-add-acc").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const idx = parseInt((e.target as HTMLElement).getAttribute("data-srv")!);
            currentState.servers[idx].accounts.push({ run: true, login: "", password: "", character: "", _isNew: true });
            render();
            const accIdx = currentState.servers[idx].accounts.length - 1;
            setTimeout(() => {
                if (currentState.servers[idx] && currentState.servers[idx].accounts[accIdx]) {
                    currentState.servers[idx].accounts[accIdx]._isNew = false;
                }
            }, 400);
        });
    });

    document.querySelectorAll(".btn-del-acc").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const btnEl = e.target as HTMLElement;
            const srv = parseInt(btnEl.getAttribute("data-srv")!);
            const acc = parseInt(btnEl.getAttribute("data-acc")!);

            const server = currentState.servers[srv];
            if (!server || !server.accounts[acc]) return;

            const accountRow = btnEl.closest(".account-row") as HTMLElement;
            if (accountRow) {
                // Get rect before touching anything
                const rect = accountRow.getBoundingClientRect();

                // Create a fixed ghost clone for the visual fade
                const clone = accountRow.cloneNode(true) as HTMLElement;
                clone.style.position = 'fixed';
                clone.style.top = `${rect.top}px`;
                clone.style.left = `${rect.left}px`;
                clone.style.width = `${rect.width}px`;
                clone.style.height = `${rect.height}px`;
                clone.style.margin = '0';
                clone.style.zIndex = '100';
                clone.style.pointerEvents = 'none';
                document.body.appendChild(clone);

                // Hide original row's visible content but lock its physical space
                accountRow.style.visibility = 'hidden';
                accountRow.style.height = `${rect.height}px`;
                accountRow.style.minHeight = `${rect.height}px`;
                accountRow.style.overflow = 'hidden';
                accountRow.style.transition = "all 400ms var(--md-sys-motion-easing-emphasized)";

                // 1. Start the fade out on the clone using Web Animations API
                const fadeAnimation = clone.animate([
                    { opacity: 1 },
                    { opacity: 0 }
                ], {
                    duration: 400,
                    easing: 'cubic-bezier(0.2, 0.0, 0, 1.0)',
                    fill: 'forwards'
                });

                // 2. Wait for fade to finish, then securely collapse the original space
                fadeAnimation.onfinish = () => {
                    if (document.body.contains(clone)) clone.remove();
                    accountRow.style.minHeight = '0px';
                    accountRow.style.height = '0px';
                    accountRow.style.paddingTop = '0px';
                    accountRow.style.paddingBottom = '0px';
                    accountRow.style.marginTop = '0px';
                    accountRow.style.marginBottom = '-12px'; // compensate for grid/flex gap
                    accountRow.style.border = 'none';
                };
            }

            const removingAccount = server.accounts[acc];
            removingAccount._isRemoving = true;
            // Native replacement finishes after full animation (400ms + 400ms + buffer)
            setTimeout(() => {
                if (currentState.servers[srv]) {
                    const actualAccIdx = server.accounts.indexOf(removingAccount);
                    if (actualAccIdx !== -1) {
                        server.accounts.splice(actualAccIdx, 1);
                    }
                    render();
                }
            }, 850);
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
                        updateStartAllButton();
                        requestSave();
                    } else {
                        // @ts-ignore
                        currentState.servers[srv].accounts[acc][field] = target.value;
                        requestSave();
                    }
                } else {
                    // @ts-ignore
                    currentState.servers[srv][field] = target.value;
                    if (field === 'name') {
                        const srvName = escapeHtml(target.value || "New Server");
                        const playBtn = document.querySelector(`.btn-play-srv[data-srv="${srv}"]`);
                        const delBtn = document.querySelector(`.btn-del-srv[data-srv="${srv}"]`);
                        if (playBtn) playBtn.innerHTML = `Play ${srvName}`;
                        if (delBtn) delBtn.innerHTML = `Remove ${srvName}`;
                    }
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
        logMsg("Starting global sequential launch...");
        await invoke("launch_all");
    });

    document.querySelectorAll(".btn-play-srv").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const srv = parseInt((e.target as HTMLElement).getAttribute("data-srv")!);
            logMsg(`Starting server ${currentState.servers[srv].name}...`);
            await invoke("launch_server", { serverIndex: srv });
        });
    });

    document.querySelectorAll(".btn-play-acc").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const target = e.target as HTMLElement;
            const srv = parseInt(target.getAttribute("data-srv")!);
            const acc = parseInt(target.getAttribute("data-acc")!);
            logMsg(`Launching ${currentState.servers[srv].accounts[acc].character}...`);
            await invoke("launch_account", { serverIndex: srv, accountIndex: acc });
        });
    });

    document.querySelectorAll(".btn-server-launcher").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const target = e.target as HTMLElement;
            const srv = parseInt(target.getAttribute("data-srv")!);
            logMsg(`Launching Server Launcher for ${currentState.servers[srv].name}...`);
            await invoke("launch_server_launcher", { serverIndex: srv });
        });
    });

    // --- HTML5 Drag and Drop for Server Cards ---
    let draggedServerIdx: number | null = null;
    document.querySelectorAll(".server-card").forEach(card => {
        card.addEventListener("mousedown", (e) => {
            // Prevent dragging when interacting with form elements
            if (['INPUT', 'BUTTON', 'TEXTAREA', 'LABEL'].includes((e.target as HTMLElement).tagName)) {
                (card as HTMLElement).draggable = false;
            } else {
                (card as HTMLElement).draggable = true;
            }
        });

        card.addEventListener("dragstart", (e) => {
            const dragEvent = e as DragEvent;
            const target = e.target as HTMLElement;
            // Prevent dragging from form elements directly
            if (['INPUT', 'BUTTON', 'TEXTAREA', 'LABEL'].includes((e.target as HTMLElement).tagName)) {
                e.preventDefault();
                return;
            }
            draggedServerIdx = parseInt(target.dataset.srvIndex!);
            if (dragEvent.dataTransfer) {
                dragEvent.dataTransfer.effectAllowed = 'move';
                dragEvent.dataTransfer.setData('text/plain', draggedServerIdx.toString());
            }
            target.style.opacity = '0.5';
            target.style.transform = 'scale(0.98)';
        });
        card.addEventListener("dragend", (e) => {
            const target = e.target as HTMLElement;
            target.style.opacity = '1';
            target.style.transform = 'scale(1)';
            draggedServerIdx = null;
            document.querySelectorAll(".server-card").forEach(c => {
                (c as HTMLElement).style.borderBottom = '';
                (c as HTMLElement).style.borderTop = '';
            });
        });
        card.addEventListener("dragenter", (e) => {
            e.preventDefault(); // Necessary to allow dropping
        });
        card.addEventListener("dragover", (e) => {
            e.preventDefault(); // Necessary to allow dropping
            const target = (e.currentTarget as HTMLElement);
            if (draggedServerIdx === null || draggedServerIdx === parseInt(target.dataset.srvIndex!)) return;

            const bounding = target.getBoundingClientRect();
            const offset = bounding.y + (bounding.height / 2);
            if ((e as DragEvent).clientY - offset > 0) {
                target.style.borderBottom = `2px solid var(--text-accent)`;
                target.style.borderTop = '';
            } else {
                target.style.borderTop = `2px solid var(--text-accent)`;
                target.style.borderBottom = '';
            }
        });
        card.addEventListener("dragleave", (e) => {
            const target = (e.currentTarget as HTMLElement);
            target.style.borderBottom = '';
            target.style.borderTop = '';
        });
        card.addEventListener("drop", (e) => {
            e.preventDefault();
            const target = (e.currentTarget as HTMLElement);
            target.style.borderBottom = '';
            target.style.borderTop = '';
            if (draggedServerIdx === null) return;
            const targetIdx = parseInt(target.dataset.srvIndex!);
            if (draggedServerIdx === targetIdx) return;

            // Determine if dropped above or below
            const bounding = target.getBoundingClientRect();
            const offset = bounding.y + (bounding.height / 2);
            const dropAbove = (e as DragEvent).clientY - offset <= 0;

            let insertIdx = targetIdx;
            if (!dropAbove) insertIdx++;
            if (draggedServerIdx < insertIdx) insertIdx--;

            // Splice array
            const [moved] = currentState.servers.splice(draggedServerIdx, 1);
            currentState.servers.splice(insertIdx, 0, moved);

            // Remap expanded servers indices
            const newExpanded = new Set<number>();
            expandedServers.forEach(v => {
                if (v === draggedServerIdx) {
                    newExpanded.add(insertIdx);
                } else {
                    let newV = v;
                    if (draggedServerIdx! < v) newV--;
                    if (insertIdx <= newV && draggedServerIdx !== v) newV++;
                    newExpanded.add(newV);
                }
            });
            expandedServers = newExpanded;

            requestSave();
            render();
        });
    });
}
