import type { SlotContext } from "@ynput/ayon-addon";

const noop = async (_ctx: SlotContext<"entityMenuItem">) => {
  // intentionally empty
};

export default noop;