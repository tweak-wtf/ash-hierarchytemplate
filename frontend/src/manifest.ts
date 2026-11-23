import { defineAddon, entityMenuItem, slicerMenuItem } from "@ynput/ayon-addon/manifest";

export default defineAddon({
  contributes: [
    entityMenuItem({
      id: "apply_task_template_popup",
      label: "Task Templates",
      icon: "account_tree",
      entityTypes: ["folder"],
      run: () => import("./menu/applyTaskTemplatePopup"),
    }),
    slicerMenuItem({
      id: "apply_task_template_popup",
      label: "Task Templates",
      icon: "account_tree",
      sliceTypes: ["hierarchy"],
      in: ["context", "dropdown"],
      run: () => import("./menu/applyTaskTemplatePopup"),
    }),
  ],
});