import * as msal from "@azure/msal-browser";
import { msalConfig } from "./authConfig";

export const msalInstance = new msal.PublicClientApplication(msalConfig);

// Initialize the instance (for latest MSAL.js versions)
export const initializeMsal = async () => {
  await msalInstance.initialize();
  return msalInstance;
};
