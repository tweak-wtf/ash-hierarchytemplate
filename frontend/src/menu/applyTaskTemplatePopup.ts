import { toast, type EntityRef } from "@ynput/ayon-addon";
import { applyTaskTemplate, getTaskTemplates } from "../api";
import { confirmPopup } from "./confirmPopup";

type TaskTemplate = {
  name: string;
  tasks?: Array<{ name: string; type: string }>;
  [key: string]: unknown;
};

type ApplyResult = {
  success?: boolean;
  operations?: Array<{ success?: boolean; detail?: string | null }>;
};

function toastApplyResult(templateName: string, result: ApplyResult) {
  const operations = result.operations ?? [];
  const created = operations.filter((op) => op.success);
  const failed = operations.filter((op) => !op.success);

  if (created.length) {
    toast.success(
      `Created ${created.length} task${created.length === 1 ? "" : "s"} from "${templateName}"`,
    );
  }
  if (failed.length) {
    const details = failed
      .map((op) => op.detail)
      .filter(Boolean)
      .slice(0, 3)
      .join("; ");
    toast.error(
      `Did not create ${failed.length} task${failed.length === 1 ? "" : "s"} from "${templateName}"` +
        (details ? `: ${details}` : ""),
    );
  }
  if (!created.length && !failed.length) {
    toast.info(`No tasks created from "${templateName}"`);
  }
}

/** Shared by entityMenuItem and slicer.menuItem (hierarchy). */
const applyTaskTemplatePopup = async ({
  projectName,
  entities,
}: {
  projectName: string;
  entities: EntityRef[];
}) => {
  const folders = entities.filter((entity) => entity.entityType === "folder");
  if (!folders.length) {
    toast.warn("Select one or more folders");
    return;
  }

  const templates = (await getTaskTemplates(projectName)) as TaskTemplate[];
  if (!Array.isArray(templates) || !templates.length) {
    toast.warn("No task templates available");
    return;
  }

  const folderCount = folders.length;
  const folderLabel = folderCount === 1 ? "folder" : "folders";

  let selected = templates[0];
  let body: HTMLElement | undefined;

  if (templates.length > 1) {
    const select = document.createElement("select");
    Object.assign(select.style, {
      width: "100%",
      padding: "6px 8px",
      borderRadius: "4px",
      border: "1px solid var(--md-sys-color-outline-variant, #555)",
      background: "var(--md-sys-color-surface-container, #1e1e1e)",
      color: "inherit",
      font: "inherit",
    });
    for (const template of templates) {
      const option = document.createElement("option");
      option.value = template.name;
      option.textContent = template.name;
      select.append(option);
    }
    select.onchange = () => {
      selected = templates.find((t) => t.name === select.value) ?? templates[0];
    };
    body = select;
  }

  const taskCount = selected.tasks?.length ?? 0;
  const ok = await confirmPopup({
    title: "Apply task template",
    description:
      templates.length === 1
        ? `Apply "${selected.name}" (${taskCount} task${taskCount === 1 ? "" : "s"}) to ${folderCount} selected ${folderLabel}?`
        : `Choose a template and apply its tasks to ${folderCount} selected ${folderLabel}.`,
    body,
    okLabel: "Apply",
    cancelLabel: "Cancel",
  });

  if (!ok) return;

  if (body instanceof HTMLSelectElement) {
    selected = templates.find((t) => t.name === body.value) ?? templates[0];
  }

  const result = (await applyTaskTemplate(
    projectName,
    selected.name,
    folders.map((e) => e.id),
    selected,
  )) as ApplyResult;
  toastApplyResult(selected.name, result);
};

export default applyTaskTemplatePopup;
