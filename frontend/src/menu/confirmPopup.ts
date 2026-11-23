export type ConfirmPopupOptions = {
  title: string;
  description: string;
  /** Optional extra node appended under the description (e.g. a `<select>`). */
  body?: HTMLElement;
  okLabel?: string;
  cancelLabel?: string;
};

/** Minimal centered confirm dialog. Resolves `true` on OK, `false` on Cancel / Escape / backdrop. */
export function confirmPopup({
  title,
  description,
  body,
  okLabel = "OK",
  cancelLabel = "Cancel",
}: ConfirmPopupOptions): Promise<boolean> {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    Object.assign(overlay.style, {
      position: "fixed",
      inset: "0",
      zIndex: "10000",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "rgba(0, 0, 0, 0.45)",
    });

    const dialog = document.createElement("div");
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    Object.assign(dialog.style, {
      minWidth: "280px",
      maxWidth: "420px",
      padding: "16px 18px",
      borderRadius: "8px",
      background: "var(--md-sys-color-surface-container-high, #2a2a2a)",
      color: "var(--md-sys-color-on-surface, #f0f0f0)",
      boxShadow: "0 8px 28px rgba(0, 0, 0, 0.35)",
      fontFamily: "inherit",
    });

    const heading = document.createElement("div");
    heading.textContent = title;
    Object.assign(heading.style, {
      fontWeight: "600",
      fontSize: "15px",
      marginBottom: "8px",
    });

    const text = document.createElement("div");
    text.textContent = description;
    Object.assign(text.style, {
      fontSize: "13px",
      lineHeight: "1.4",
      opacity: "0.9",
      marginBottom: body ? "12px" : "16px",
    });

    const actions = document.createElement("div");
    Object.assign(actions.style, {
      display: "flex",
      justifyContent: "flex-end",
      gap: "8px",
      marginTop: "16px",
    });

    const buttonStyle = (primary: boolean): Partial<CSSStyleDeclaration> => ({
      all: "unset",
      cursor: "pointer",
      padding: "6px 14px",
      borderRadius: "4px",
      fontSize: "13px",
      fontWeight: "500",
      background: primary
        ? "var(--md-sys-color-primary, #7eb8ff)"
        : "var(--md-sys-color-surface-container-highest, #3a3a3a)",
      color: primary
        ? "var(--md-sys-color-on-primary, #003258)"
        : "var(--md-sys-color-on-surface, #f0f0f0)",
    });

    const cancelBtn = document.createElement("button");
    cancelBtn.type = "button";
    cancelBtn.textContent = cancelLabel;
    Object.assign(cancelBtn.style, buttonStyle(false));

    const okBtn = document.createElement("button");
    okBtn.type = "button";
    okBtn.textContent = okLabel;
    Object.assign(okBtn.style, buttonStyle(true));

    const close = (ok: boolean) => {
      document.removeEventListener("keydown", onKey);
      overlay.remove();
      resolve(ok);
    };

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        close(false);
      }
      if (e.key === "Enter") {
        e.preventDefault();
        close(true);
      }
    };

    cancelBtn.onclick = () => close(false);
    okBtn.onclick = () => close(true);
    overlay.onclick = (e) => {
      if (e.target === overlay) close(false);
    };

    actions.append(cancelBtn, okBtn);
    dialog.append(heading, text);
    if (body) dialog.append(body);
    dialog.append(actions);
    overlay.append(dialog);
    document.body.append(overlay);
    document.addEventListener("keydown", onKey);
    okBtn.focus();
  });
}
