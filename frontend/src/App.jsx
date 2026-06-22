import { useState, useEffect } from "react";

const API = "https://jobbotpro.org/api";

const getToken = () => localStorage.getItem("jobbot_token");
const authHeaders = () => ({
  "Content-Type": "application/json",
  "Authorization": `Bearer ${getToken()}`
});

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: #050a0f;
    color: #e0f0ff;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
  }

  .app { display: flex; min-height: 100vh; }

  .sidebar {
    width: 220px;
    background: #0d1a2b;
    border-right: 1px solid #0066ff22;
    padding: 32px 0;
    display: flex;
    flex-direction: column;
    position: fixed;
    height: 100vh;
  }

  .logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #00ff88;
    padding: 0 24px 32px;
    letter-spacing: -0.5px;
  }

  .logo span { color: #0066ff; }

  .nav-item {
    padding: 12px 24px;
    cursor: pointer;
    color: #7090b0;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.15s;
    border-left: 3px solid transparent;
  }

  .nav-item:hover { color: #e0f0ff; background: #0066ff11; }
  .nav-item.active { color: #00ff88; border-left-color: #00ff88; background: #00ff8811; }

  .main { margin-left: 220px; flex: 1; padding: 40px; }

  .page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #e0f0ff;
  }

  .page-sub { color: #7090b0; font-size: 14px; margin-bottom: 32px; }

  .card {
    background: #0d1a2b;
    border: 1px solid #0066ff22;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
  }

  .card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    color: #00ff88;
  }

  input, textarea {
    width: 100%;
    background: #050a0f;
    border: 1px solid #0066ff33;
    border-radius: 8px;
    padding: 12px 16px;
    color: #e0f0ff;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    margin-bottom: 12px;
    outline: none;
    transition: border 0.15s;
  }

  input:focus, textarea:focus { border-color: #00ff88; }

  .btn {
    padding: 12px 24px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.15s;
  }

  .btn-primary { background: #00ff88; color: #050a0f; }
  .btn-primary:hover { background: #00e077; transform: translateY(-1px); }
  .btn-secondary { background: transparent; color: #00ff88; border: 1px solid #00ff88; margin-left: 12px; }
  .btn-secondary:hover { background: #00ff8811; }
  .btn-blue { background: #0066ff; color: #fff; }
  .btn-blue:hover { background: #0055dd; }

  .tag-input-wrapper { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }

  .tag {
    background: #0066ff22;
    border: 1px solid #0066ff44;
    color: #0066ff;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .tag-remove { cursor: pointer; color: #7090b0; font-size: 16px; line-height: 1; }
  .tag-remove:hover { color: #ff4466; }

  .toggle-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }

  .toggle {
    width: 44px; height: 24px;
    background: #1a2a3a;
    border-radius: 12px;
    cursor: pointer;
    position: relative;
    transition: background 0.2s;
    border: none;
  }

  .toggle.on { background: #00ff88; }
  .toggle::after {
    content: '';
    position: absolute;
    width: 18px; height: 18px;
    background: #fff;
    border-radius: 50%;
    top: 3px; left: 3px;
    transition: left 0.2s;
  }
  .toggle.on::after { left: 23px; }
  .toggle-label { font-size: 14px; color: #7090b0; }

  .applications-table { width: 100%; border-collapse: collapse; }
  .applications-table th {
    text-align: left; padding: 12px 16px;
    font-size: 12px; font-weight: 600;
    color: #7090b0; text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #0066ff22;
  }
  .applications-table td { padding: 14px 16px; font-size: 14px; border-bottom: 1px solid #0066ff11; }

  .status-applied { color: #00ff88; background: #00ff8811; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
  .status-failed { color: #ff4466; background: #ff446611; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }

  .stat-row { display: flex; gap: 16px; margin-bottom: 24px; }
  .stat-card { flex: 1; background: #0d1a2b; border: 1px solid #0066ff22; border-radius: 12px; padding: 20px; }
  .stat-number { font-family: 'Space Grotesk', sans-serif; font-size: 36px; font-weight: 700; color: #00ff88; }
  .stat-label { font-size: 12px; color: #7090b0; margin-top: 4px; }

  .auth-wrap { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: #050a0f; }
  .auth-card { background: #0d1a2b; border: 1px solid #0066ff22; border-radius: 16px; padding: 40px; width: 100%; max-width: 400px; }
  .auth-title { font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; margin-bottom: 4px; color: #e0f0ff; }
  .auth-sub { color: #7090b0; font-size: 14px; margin-bottom: 28px; }
  .auth-switch { text-align: center; margin-top: 20px; font-size: 14px; color: #7090b0; }
  .auth-switch span { color: #00ff88; cursor: pointer; }

  .error { color: #ff4466; font-size: 13px; margin-bottom: 12px; }
  .success { color: #00ff88; font-size: 13px; margin-bottom: 12px; }

  .run-btn-wrap { display: flex; align-items: center; gap: 16px; }
  .running-indicator { color: #00ff88; font-size: 13px; display: flex; align-items: center; gap: 6px; }
  .dot { width: 8px; height: 8px; background: #00ff88; border-radius: 50%; animation: pulse 1s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

  .upload-area {
    border: 2px dashed #0066ff44; border-radius: 8px;
    padding: 32px; text-align: center; cursor: pointer;
    transition: border-color 0.15s; margin-bottom: 12px;
  }
  .upload-area:hover { border-color: #00ff88; }
  .upload-icon { font-size: 32px; margin-bottom: 8px; }
  .upload-text { color: #7090b0; font-size: 14px; }
  .upload-text span { color: #00ff88; }

  .resume-status {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 16px; border-radius: 8px;
    background: #00ff8811; border: 1px solid #00ff8833;
    color: #00ff88; font-size: 13px; margin-bottom: 16px;
  }

  .link { color: #0066ff; text-decoration: none; font-size: 13px; }
  .link:hover { color: #00ff88; }

  .empty-state { text-align: center; padding: 60px; color: #7090b0; }
  .empty-icon { font-size: 48px; margin-bottom: 12px; }
  .empty-text { font-size: 14px; }

  .landing {
    min-height: 100vh; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center; padding: 40px;
    background: radial-gradient(ellipse at 50% 0%, #0066ff15 0%, #050a0f 60%);
  }
  .landing-logo { font-family: 'Space Grotesk', sans-serif; font-size: 48px; font-weight: 700; color: #e0f0ff; margin-bottom: 16px; }
  .landing-logo span { color: #00ff88; }
  .landing-sub { font-size: 18px; color: #7090b0; max-width: 480px; margin-bottom: 40px; line-height: 1.6; }
  .landing-price { font-family: 'Space Grotesk', sans-serif; font-size: 14px; color: #7090b0; margin-top: 16px; }
  .landing-price span { color: #00ff88; font-weight: 600; }
  .glow { text-shadow: 0 0 40px #00ff8844; }
`;

export default function App() {
  const [page, setPage] = useState("landing");
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState("login");

  useEffect(() => {
    const token = localStorage.getItem("jobbot_token");
    const email = localStorage.getItem("jobbot_email");
    if (token && email) {
      setUser({ token, email });
      setPage("dashboard");
    }
  }, []);

  const logout = () => {
    localStorage.removeItem("jobbot_token");
    localStorage.removeItem("jobbot_email");
    setUser(null);
    setPage("landing");
  };

  const onAuth = (data) => {
    localStorage.setItem("jobbot_token", data.token);
    localStorage.setItem("jobbot_email", data.email);
    setUser({ token: data.token, email: data.email });
    setPage("dashboard");
  };

  return (
    <>
      <style>{styles}</style>
      {page === "landing" && <Landing onGetStarted={() => { setAuthMode("register"); setPage("auth"); }} onLogin={() => { setAuthMode("login"); setPage("auth"); }} />}
      {page === "auth" && <Auth mode={authMode} setMode={setAuthMode} onSuccess={onAuth} />}
      {page !== "landing" && page !== "auth" && (
        <div className="app">
          <Sidebar page={page} setPage={setPage} logout={logout} />
          <div className="main">
            {page === "dashboard" && <Dashboard />}
            {page === "applications" && <Applications />}
            {page === "preferences" && <Preferences />}
            {page === "resume" && <Resume />}
          </div>
        </div>
      )}
    </>
  );
}

function Landing({ onGetStarted, onLogin }) {
  return (
    <div className="landing">
      <div className="landing-logo glow">Job<span>Bot</span></div>
      <div className="landing-sub">Stop applying manually. JobBot finds matching jobs on Greenhouse, Lever, and Workable and applies for you automatically — 24/7.</div>
      <div style={{ display: "flex", gap: "12px" }}>
        <button className="btn btn-primary" onClick={onGetStarted}>Get Started</button>
        <button className="btn btn-secondary" onClick={onLogin}>Log In</button>
      </div>
      <div className="landing-price">Starting at <span>$19.99/mo</span> — cancel anytime</div>
    </div>
  );
}

function Auth({ mode, setMode, onSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API}/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (data.error) { setError(data.error); setLoading(false); return; }
      onSuccess(data);
    } catch {
      setError("Connection error");
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <div className="auth-title">{mode === "login" ? "Welcome back" : "Create account"}</div>
        <div className="auth-sub">{mode === "login" ? "Log in to your JobBot account" : "Start applying automatically today"}</div>
        {error && <div className="error">{error}</div>}
        <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} type="email" />
        <input placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} type="password" onKeyDown={e => e.key === "Enter" && submit()} />
        <button className="btn btn-primary" style={{ width: "100%" }} onClick={submit} disabled={loading}>
          {loading ? "..." : mode === "login" ? "Log In" : "Create Account"}
        </button>
        <div className="auth-switch">
          {mode === "login" ? <>No account? <span onClick={() => setMode("register")}>Sign up</span></> : <>Have an account? <span onClick={() => setMode("login")}>Log in</span></>}
        </div>
      </div>
    </div>
  );
}

function Sidebar({ page, setPage, logout }) {
  const items = [
    { id: "dashboard", label: "Dashboard" },
    { id: "resume", label: "Resume" },
    { id: "preferences", label: "Preferences" },
    { id: "applications", label: "Applications" },
  ];
  return (
    <div className="sidebar">
      <div className="logo">Job<span>Bot</span></div>
      {items.map(item => (
        <div key={item.id} className={`nav-item ${page === item.id ? "active" : ""}`} onClick={() => setPage(item.id)}>
          {item.label}
        </div>
      ))}
      <div style={{ flex: 1 }} />
      <div className="nav-item" onClick={logout}>Log Out</div>
    </div>
  );
}

function Dashboard() {
  const [apps, setApps] = useState([]);
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    fetch(`${API}/applications`, { headers: authHeaders() })
      .then(r => r.json()).then(data => { if (Array.isArray(data)) setApps(data); });
  }, []);

  const runBot = async () => {
    setRunning(true);
    setMsg("");
    try {
      const res = await fetch(`${API}/run`, { method: "POST", headers: authHeaders() });
      const data = await res.json();
      setMsg(data.message || data.error);
    } catch { setMsg("Connection error"); }
    setTimeout(() => setRunning(false), 3000);
  };

  const total = apps.length;
  const applied = apps.filter(a => a.status === "applied").length;
  const failed = apps.filter(a => a.status === "failed").length;

  return (
    <>
      <div className="page-title">Dashboard</div>
      <div className="page-sub">Your job application overview</div>
      <div className="stat-row">
        <div className="stat-card"><div className="stat-number">{total}</div><div className="stat-label">Total Applications</div></div>
        <div className="stat-card"><div className="stat-number">{applied}</div><div className="stat-label">Successful</div></div>
        <div className="stat-card"><div className="stat-number" style={{ color: failed > 0 ? "#ff4466" : "#00ff88" }}>{failed}</div><div className="stat-label">Failed</div></div>
      </div>
      <div className="card">
        <div className="card-title">Run Bot</div>
        <p style={{ color: "#7090b0", fontSize: "14px", marginBottom: "20px" }}>Bot will scrape Greenhouse, Lever, and Workable for matching jobs and auto-apply using your resume and preferences.</p>
        <div className="run-btn-wrap">
          <button className="btn btn-primary" onClick={runBot} disabled={running}>{running ? "Running..." : "Run Now"}</button>
          {running && <div className="running-indicator"><div className="dot" />Applying to jobs...</div>}
          {msg && !running && <div style={{ fontSize: "13px", color: "#00ff88" }}>{msg}</div>}
        </div>
      </div>
    </>
  );
}

function Resume() {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [uploaded, setUploaded] = useState(false);

  useEffect(() => {
    fetch(`${API}/resume-status`, { headers: authHeaders() })
      .then(r => r.json()).then(data => setUploaded(data.uploaded));
  }, []);

  const upload = async () => {
    if (!file) return;
    const form = new FormData();
    form.append("resume", file);
    try {
      const res = await fetch(`${API}/upload-resume`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${getToken()}` },
        body: form
      });
      const data = await res.json();
      if (data.success) { setMsg("Resume uploaded and saved"); setUploaded(true); }
      else setError(data.error);
    } catch { setError("Upload failed"); }
  };

  return (
    <>
      <div className="page-title">Resume</div>
      <div className="page-sub">Upload your resume so JobBot can apply on your behalf</div>
      <div className="card">
        <div className="card-title">Upload Resume</div>
        {uploaded && <div className="resume-status">✓ Resume on file — JobBot is using this to apply</div>}
        <div className="upload-area" onClick={() => document.getElementById("resume-input").click()}>
          <div className="upload-icon">📄</div>
          <div className="upload-text">{file ? file.name : <><span>Click to upload</span> your resume (PDF)</>}</div>
        </div>
        <input id="resume-input" type="file" accept=".pdf" style={{ display: "none" }} onChange={e => { setFile(e.target.files[0]); setMsg(""); setError(""); }} />
        {error && <div className="error">{error}</div>}
        {msg && <div className="success">{msg}</div>}
        <button className="btn btn-primary" onClick={upload} disabled={!file}>Upload Resume</button>
      </div>
    </>
  );
}

function Preferences() {
  const [keywords, setKeywords] = useState([]);
  const [kwInput, setKwInput] = useState("");
  const [location, setLocation] = useState("");
  const [remote, setRemote] = useState(false);
  const [companies, setCompanies] = useState([]);
  const [compInput, setCompInput] = useState("");
  const [msg, setMsg] = useState("");
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetch(`${API}/preferences`, { headers: authHeaders() })
      .then(r => r.json()).then(data => {
        if (data.keywords) setKeywords(data.keywords);
        if (data.location) setLocation(data.location);
        if (data.remote !== undefined) setRemote(data.remote);
        if (data.companies) setCompanies(data.companies);
        setLoaded(true);
      });
  }, []);

  const addKeyword = () => { if (kwInput.trim()) { setKeywords([...keywords, kwInput.trim()]); setKwInput(""); } };
  const addCompany = () => { if (compInput.trim()) { setCompanies([...companies, compInput.trim()]); setCompInput(""); } };

  const save = async () => {
    const res = await fetch(`${API}/preferences`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ keywords, location, remote, companies })
    });
    const data = await res.json();
    if (data.success) setMsg("Preferences saved");
  };

  return (
    <>
      <div className="page-title">Preferences</div>
      <div className="page-sub">Tell JobBot what roles to apply for</div>
      {loaded && (keywords.length > 0 || location) && (
        <div className="resume-status" style={{ marginBottom: "20px" }}>✓ Preferences saved — JobBot is using these settings</div>
      )}
      <div className="card">
        <div className="card-title">Job Keywords</div>
        <div className="tag-input-wrapper">
          {keywords.map((k, i) => (
            <div key={i} className="tag">{k}<span className="tag-remove" onClick={() => setKeywords(keywords.filter((_, j) => j !== i))}>×</span></div>
          ))}
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <input placeholder="e.g. Software Engineer" value={kwInput} onChange={e => setKwInput(e.target.value)} onKeyDown={e => e.key === "Enter" && addKeyword()} style={{ marginBottom: 0 }} />
          <button className="btn btn-blue" onClick={addKeyword}>Add</button>
        </div>
      </div>
      <div className="card">
        <div className="card-title">Location</div>
        <input placeholder="e.g. Los Angeles" value={location} onChange={e => setLocation(e.target.value)} />
        <div className="toggle-row">
          <button className={`toggle ${remote ? "on" : ""}`} onClick={() => setRemote(!remote)} />
          <span className="toggle-label">Remote only</span>
        </div>
      </div>
      <div className="card">
        <div className="card-title">Target Companies</div>
        <p style={{ color: "#7090b0", fontSize: "13px", marginBottom: "12px" }}>Enter company slugs from Greenhouse, Lever, or Workable (e.g. "stripe", "airbnb")</p>
        <div className="tag-input-wrapper">
          {companies.map((c, i) => (
            <div key={i} className="tag">{c}<span className="tag-remove" onClick={() => setCompanies(companies.filter((_, j) => j !== i))}>×</span></div>
          ))}
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <input placeholder="e.g. stripe" value={compInput} onChange={e => setCompInput(e.target.value)} onKeyDown={e => e.key === "Enter" && addCompany()} style={{ marginBottom: 0 }} />
          <button className="btn btn-blue" onClick={addCompany}>Add</button>
        </div>
      </div>
      {msg && <div className="success">{msg}</div>}
      <button className="btn btn-primary" onClick={save}>Save Preferences</button>
    </>
  );
}

function Applications() {
  const [apps, setApps] = useState([]);

  useEffect(() => {
    fetch(`${API}/applications`, { headers: authHeaders() })
      .then(r => r.json()).then(data => { if (Array.isArray(data)) setApps(data); });
  }, []);

  return (
    <>
      <div className="page-title">Applications</div>
      <div className="page-sub">Jobs JobBot has applied to on your behalf</div>
      <div className="card">
        {apps.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🤖</div>
            <div className="empty-text">No applications yet. Run the bot from the dashboard to get started.</div>
          </div>
        ) : (
          <table className="applications-table">
            <thead>
              <tr>
                <th>Job Title</th><th>Company</th><th>Status</th><th>Date</th><th>Link</th>
              </tr>
            </thead>
            <tbody>
              {apps.map((a, i) => (
                <tr key={i}>
                  <td>{a.title}</td>
                  <td>{a.company}</td>
                  <td><span className={a.status === "applied" ? "status-applied" : "status-failed"}>{a.status}</span></td>
                  <td style={{ color: "#7090b0", fontSize: "12px" }}>{new Date(a.date).toLocaleDateString()}</td>
                  <td><a href={a.url} target="_blank" rel="noreferrer" className="link">View</a></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
