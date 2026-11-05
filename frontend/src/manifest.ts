import { defineAddon, entityMenuItem } from "@ynput/ayon-addon/manifest";

export default defineAddon({
  contributes: [
    entityMenuItem({
      id: "noop_folder_menu",
      label: "Do nothing",
      icon: "event",   // where are those icons defined?
      entityTypes: ["folder"],
      run: () => import("./menu/noop"),
    }),
  ],
});