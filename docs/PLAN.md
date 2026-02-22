# Perfect World Launcher UI Redesign Plan

## Goal Description
The objective is to completely redesign the Perfect World Launcher UI to exactly match the provided target screenshot. The new theme transitions from a typical rectangular, multi-gradient dashboard to a highly refined, premium dark-charcoal aesthetic with bright cyan/blue accents and heavily rounded (pill-shaped) elements.

## Design Tokens & Aesthetic Principles
To achieve a "1:1" match with the screenshot, the following design principles must be implemented:

1.  **Color Palette**:
    *   **Background (App)**: Very dark, almost black charcoal (e.g., `#16181A` or `#18181B`).
    *   **Surface/Cards (Server blocks)**: Slightly lighter dark gray (e.g., `#212429` or `#1E1E1E`).
    *   **Inputs / Secondary Buttons**: Muted dark gray with subtle borders (e.g., `#2A2D35`).
    *   **Primary Accent**: Bright Cyan/Light Blue for primary actions like "Play" and "Start 2 accounts" (e.g., `#3BDFE4` or `#2bd2ff`).
    *   **Text**: White for headings and primary values (`#FFFFFF`), slightly muted gray for labels (`#A0A5B1`).

2.  **Typography**:
    *   Modern sans-serif (Inter, Roboto, or Segoe UI) with strong weight distinctions. Labels (`Hide`, `Server name`) are semi-bold, while inputs are regular weight.

3.  **Shapes & Borders**:
    *   **Pill-Shapes**: Almost all interactive elements (buttons, inputs) must have maximum border-radius (`border-radius: 9999px` or `24px` to achieve the pill look).
    *   **Server Cards**: Should have a generous border-radius (e.g., `24px`) with a subtle border outline (e.g., `1px solid rgba(255, 255, 255, 0.05)`).
    *   **Checkboxes**: Specialized rounded-square or circular checkboxes filled with cyan when checked, featuring a distinct checkmark.

## Proposed Changes

### 1. `perfect-world-launcher/src/styles.css`
*   **[MODIFY]**: Redefine all CSS variables (`--bg-app`, `--bg-card`, `--btn-primary`, `--btn-surface`, etc.) to match the new dark charcoal and cyan palette.
*   **[MODIFY]**: Update `button` and `input` global styles to enforce pill-shaped `border-radius: 30px`, specific paddings, and the new background colors.
*   **[MODIFY]**: Revamp the `.server-card` classes. Remove heavy drop-shadows in favor of clean, subtle borders and flat dark backgrounds.
*   **[MODIFY]**: Create a custom `.run-checkbox` style to exactly match the rounded, bright cyan checkbox in the screenshot.
*   **[MODIFY]**: Adjust grid layouts for the `.accounts-grid` to ensure inputs and buttons align properly with the new pill shapes. Remove the sharp table-header background, replacing it with a transparent, text-only header layout.

### 2. `perfect-world-launcher/src/main.ts`
*   **[MODIFY]**: **State Management**: Introduce an `expandedServers` state (e.g., `Set<number>`) to track which server cards are expanded (showing the client path and accounts) versus collapsed.
*   **[MODIFY]**: **Header Rendering**: Update the `appEl.innerHTML` template. Transform the header to match the top row:
    *   "Import Settings" and "Export Settings" as distinct pill buttons.
    *   Delay container with the label, the number, and `-` / `+` circular buttons to increment/decrement the delay.
*   **[MODIFY]**: **Server Card Template**:
    *   Create a conditional rendering flow based on the `expandedServers` state.
    *   **Collapsed View**: Show a single horizontal row containing the "Show" button, Server Name input, "Play [Server Name]" cyan button, and "Remove [Server Name]" button.
    *   **Expanded View**: Show "Hide", Server Name input, Play, Remove. Below it, show the "Client Path:" row, the Accounts table, and the "Add Account" button inside a distinct nested layout.
*   **[MODIFY]**: **Footer Rendering**: Rebuild the bottom row. It must contain the massive cyan "Start X accounts" button on the left, followed by "Add Server", "Save and Close", and "Show Log" buttons aligned horizontally. The launch log should appear seamlessly at the bottom left.
*   **[MODIFY]**: **Event Listeners**: Bind the new toggles ("Show"/"Hide"), the new Delay `-` / `+` buttons, and the "Save and Close" action.

## Verification Plan
*   **Automated Verification**: Build process ensures no TypeScript compilation errors occur with the updated models and state structure.
*   **Manual UI Matching**: Start the app, expand one server, collapse another, and place the application window side-by-side with the reference screenshot. Verify colors, borders, toggles, button shapes, and flex-gaps match the reference.
