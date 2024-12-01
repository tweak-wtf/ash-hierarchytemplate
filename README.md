# ash-hierarchytemplate
An AYON Addon for creating initial project folder hierarchies and task templates.

Depends on a running AYON service instance and the `ashHierarchyTemplate` project attribute.
The service handles all interaction with entities. It acts if new projects or folders are created.

> 📝 The `ashHierarchyTemplate` attribute will be created on first caught `entity.project.created` event which requires a server reboot.

## Settings

> ⚠️ If new templates have been configured please ensure these are available as keys in the `ashHierarchyTemplate` attribute's `enum` property.

### Task Template Settings

![image](https://github.com/user-attachments/assets/daf9d2f6-b7e3-4009-a481-2af14c2d61b0)

### Hierarchy Template Settings

![image](https://github.com/user-attachments/assets/bab49552-ea22-4990-8a8c-1ac2fc6e2b4e)
