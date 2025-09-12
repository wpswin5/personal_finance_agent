import React, { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import axios from "axios";
import "./App.css";

function App() {
  const { loginWithPopup, logout, getAccessTokenSilently, user, isAuthenticated } = useAuth0();
  const [me, setMe] = useState(null);

  useEffect(() => {
    const fetchMe = async () => {
      if (isAuthenticated) {
        try {
          const token = await getAccessTokenSilently({
            audience: "https://fastapiexample.com",  // MUST match your API identifier
            scope: "test:read"                   // optional, depends on API
          });
          const response = await axios.get("http://localhost:8000/user/me", {
            headers: { Authorization: `Bearer ${token}` },
          });
          setMe(response.data);
        } catch (err) {
          console.error(err);
        }
      }
    };
    fetchMe();
  }, [isAuthenticated, getAccessTokenSilently]);

  return (
    <div className="app-container">
      <h1 className="app-title">Personal Finance Dashboard</h1>
      {!isAuthenticated && <button onClick={loginWithPopup}>Log In / Sign Up</button>}
      {isAuthenticated && (
        <>
          <h2>Hello, {user.name || user.email}</h2>
          <pre>{JSON.stringify(me, null, 2)}</pre>
          <button onClick={() => logout({ returnTo: window.location.origin })}>Logout</button>
        </>
      )}
    </div>
  );
}

export default App;
