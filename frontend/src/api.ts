import addonVersion from "./addonVersion"

const addonName = "hierarchytemplate"

export function addonUrl(path: string) {
    if (!path.startsWith("/")) {
        path = "/" + path;
    }
    return `/api/addons/${addonName}/${addonVersion}${path}`;
}

export async function getTaskTemplates(projectName: string) {
    const res = await fetch(addonUrl(`/task-templates/${projectName}`));
    const data = await res.json();
    if (!res.ok) {
        throw new Error(`Failed to fetch task template settings: ${res.statusText}`);
    }
    return data;
}

export async function applyTaskTemplate(
    projectName: string, templateName: string, folderIds: string[], selectedTemplate: any
) {
    const res = await fetch(addonUrl(`/apply-task-template`), {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ projectName, templateName, folderIds, selectedTemplate }),
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(`Failed to apply task template: ${res.statusText}`);
    }
    return data;
}