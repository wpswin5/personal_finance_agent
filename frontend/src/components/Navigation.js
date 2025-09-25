import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import routes from "../navigation/routes"; 
import "./Navigation.css";

const Navigation = () => {
  const { logout, user, isAuthenticated } = useAuth0();
  const location = useLocation();

  if (!isAuthenticated) return null;

  const isActive = (path) =>
    location.pathname === path ? "nav-link active" : "nav-link";

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/" className="brand-link">
            Finance Assistant
          </Link>
        </div>

        <div className="nav-menu">
          {routes.map(({ path, name, icon: Icon }) => (
            <Link key={path} to={path} className={isActive(path)}>
              <span className="nav-icon">
                <Icon size={18} />
              </span>
              {name}
            </Link>
          ))}
        </div>

        <div className="nav-user">
          <div className="user-info">
            <img
              src={user.picture || "/default-avatar.png"}
              alt="User Avatar"
              className="user-avatar"
            />
            <span className="user-name">{user.name || user.email}</span>
          </div>
          <button
            onClick={() => logout({ returnTo: window.location.origin })}
            className="logout-btn"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
