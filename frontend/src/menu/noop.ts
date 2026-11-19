import type { SlotContext } from "@ynput/ayon-addon";
import { addonUrl, applyTaskTemplate, getTaskTemplates } from "../api"
// import addonVersion from "../addonVersion"

const noop = async ({projectName, entities}: SlotContext<"entityMenuItem">) => {
  // intentionally empty
  console.log(projectName);
  console.log(entities);
  // console.log(addonVersion);

  // get applicable task templates
  const taskTemplates = await getTaskTemplates(projectName);
  console.log(taskTemplates);

  if (!taskTemplates.length) {
    console.log("No task templates available");
    return;
  }

  const templateNames = taskTemplates.map(template => template.name);
  const selectedTemplateName = window.prompt("Select a task template", templateNames.join(", "));
  if (!selectedTemplateName) {
    console.log("No task template selected");
    return;
  }
  console.log(selectedTemplateName);
  const selectedTemplate = taskTemplates.find(template => template.name === selectedTemplateName);

  const folderIds = entities.map(entity => entity.id);
  const applyTemplateData = await applyTaskTemplate(projectName, selectedTemplateName, folderIds, selectedTemplate);
  console.log(applyTemplateData);
};

export default noop;