export const msalConfig = {
  auth: {
    clientId: process.env.REACT_APP_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${process.env.REACT_APP_TENANT_ID}/${process.env.AZURE_EXTERNAL_USER_FLOW}`,
    redirectUri: window.location.origin
  }
};

export const loginRequest = {
  scopes: [process.env.REACT_APP_API_SCOPE]
};
