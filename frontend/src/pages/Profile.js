import React, { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import '../styles/shared.css';

const THEME_KEY = 'pfa_theme';

const Profile = () => {
  const { user, isAuthenticated } = useAuth0();
  const [theme, setTheme] = useState(() => typeof window !== 'undefined' ? localStorage.getItem(THEME_KEY) || 'light' : 'light');

  useEffect(() => {
    // apply theme class to root element
    const root = document.documentElement;
    root.classList.remove('theme-light', 'theme-dark', 'theme-system');
    root.classList.add(theme === 'system' ? 'theme-system' : `theme-${theme}`);
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) {}
  }, [theme]);

  if (!isAuthenticated) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>Profile</h1>
        </div>
        <div className="card">Please sign in to view profile information.</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Profile</h1>
        <p className="muted">Basic user information from Auth0</p>
      </div>

      <div className="card">
        <div className="profile-grid">
          <img src={user.picture} alt="avatar" className="avatar-large" />

          <div className="profile-details">
            <div className="profile-row">
              <div className="profile-label">Name</div>
              <div className="profile-value">{user.name || '—'}</div>
            </div>

            <div className="profile-row">
              <div className="profile-label">Email</div>
              <div className="profile-value">{user.email}</div>
            </div>

            <div className="profile-row">
              <div className="profile-label">Nickname</div>
              <div className="profile-value">{user.nickname || '—'}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 18 }}>
        <h3 style={{ margin: 0, marginBottom: 8 }}>Settings</h3>
        <p className="muted" style={{ marginTop: 0 }}>Application preferences (placeholder)</p>

        <div style={{ marginTop: 12 }}>
          <label style={{ display: 'block', marginBottom: 8, fontWeight: 600, color: '#374151' }}>Theme</label>
          <div style={{ display: 'flex', gap: 10 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input type="radio" name="theme" value="light" checked={theme === 'light'} onChange={() => setTheme('light')} />
              Light
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input type="radio" name="theme" value="dark" checked={theme === 'dark'} onChange={() => setTheme('dark')} />
              Dark
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input type="radio" name="theme" value="system" checked={theme === 'system'} onChange={() => setTheme('system')} />
              System
            </label>
          </div>

          <div className="muted" style={{ marginTop: 10, fontSize: 13 }}>
            Theme is stored locally in your browser. To persist per-user across devices, we would need a backend setting and DB field (I can help wire that if you want).
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
