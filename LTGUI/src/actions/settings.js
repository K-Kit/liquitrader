import * as SettingsActionTypes from "../actiontypes/settings";

export const addBuyStrategy = strategy => {
  return {
    type: SettingsActionTypes.ADD_BUY_STRATEGY,
    strategy
  };
};
