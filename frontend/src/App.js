import React, { useState } from "react";
import { msalInstance, initializeMsal } from "./msalInstance";
import { loginRequest } from "./authConfig";
import { callApi } from "./api";

function App() {
  const [userData, setUserData] = useState(null);

  const handleLogin = async () => {
    try {
      // Make sure MSAL is initialized
      const instance = await initializeMsal();

      const loginResponse = await instance.loginPopup(loginRequest);
      const account = loginResponse.account;
      instance.setActiveAccount(account);

      const tokenResponse = await instance.acquireTokenSilent({
        ...loginRequest,
        account
      });

      const data = await callApi(tokenResponse.accessToken);
      setUserData(data);
    } catch (err) {
      console.error("Login / API call error:", err);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Finance API POC</h1>
      {!userData ? (
        <button onClick={handleLogin}>Login & Call API</button>
      ) : (
        <pre>{JSON.stringify(userData, null, 2)}</pre>
      )}
    </div>
  );
}

export default App;
