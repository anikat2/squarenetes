import React, { useState } from 'react';
import { Box, Home, Layers, Settings, Activity, Bell } from 'lucide-react';
import './App.css';

export default function SquarenetesDashboard() {
  const [currentPage, setCurrentPage] = useState('home');
  const [subprompt, setSubprompt] = useState('');
  const [n, setN] = useState(3);
  const [sphereTexts, setSphereTexts] = useState(['', '', '']); // start empty for security
  const [editingSphere, setEditingSphere] = useState(null);
  const [status, setStatus] = useState("");

  const handleSphereClick = (index) => {
    setEditingSphere(index);
  };

  const handleSphereTextChange = (e) => {
    const newTexts = [...sphereTexts];
    newTexts[editingSphere] = e.target.value;
    setSphereTexts(newTexts);
  };

  const handleSphereBlur = () => {
    setEditingSphere(null);
  };

  const handleSubmit = async () => {
    setStatus("Submitting...");
    try {
      const response = await fetch("http://localhost:8000/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subprompt: subprompt,
          api_keys: sphereTexts,
          n: n,
        }),
      });
      const data = await response.json();
      console.log("Response from backend:", data);
      setStatus("Submitted successfully!");
      
      const downloadLink = document.createElement('a');
      downloadLink.href = 'http://localhost:8000/download';
      downloadLink.download = 'output.zip';
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      
      alert("Prompt submitted successfully! Download starting...");
    } catch (error) {
      console.error("Error submitting prompt:", error);
      setStatus("Submission failed.");
      alert("Error submitting prompt. Check console for details.");
    }
  };

  const handleReset = () => {
    setSubprompt('');
    setN(3);
    setSphereTexts(['', '', '']); // clear API keys for security
  };

  return (
    <div className="dashboard">
      <nav className="top-nav">
        <div className="nav-left">
          <div className="logo-small">
            <Box className="icon-sm" />
          </div>
          <span className="brand">squarenetes</span>
        </div>
        <div className="nav-center">
          <a href="#" className={`nav-link ${currentPage === 'home' ? 'active' : ''}`} onClick={() => setCurrentPage('home')}>
            <Home className="icon-sm" />
            <span>Home</span>
          </a>
          <a href="#" className={`nav-link ${currentPage === 'input' ? 'active' : ''}`} onClick={() => setCurrentPage('input')}>
            <Layers className="icon-sm" />
            <span>Execute</span>
          </a>
          <a href="#" className="nav-link">
            <Activity className="icon-sm" />
            <span>Monitor</span>
          </a>
          <a href="#" className="nav-link">
            <Settings className="icon-sm" />
            <span>Settings</span>
          </a>
        </div>
        <div className="nav-right">
          <button className="icon-btn">
            <Bell className="icon-sm" />
          </button>
          <div className="avatar">SQ</div>
        </div>
      </nav>

      {currentPage === 'home' && (
        <div className="main-layout">
          <div className="graphic-side">
            <div className="graphic-container">
              <div className="cube-scene">
                <div className="cube">
                  <div className="cube-face front"></div>
                  <div className="cube-face back"></div>
                  <div className="cube-face right"></div>
                  <div className="cube-face left"></div>
                  <div className="cube-face top"></div>
                  <div className="cube-face bottom"></div>
                </div>
              </div>
              <div className="floating-orbs">
                <div className="orb orb-1"></div>
                <div className="orb orb-2"></div>
                <div className="orb orb-3"></div>
              </div>
              <div className="grid-lines">
                <div className="grid-line h-line" style={{top: '20%'}}></div>
                <div className="grid-line h-line" style={{top: '40%'}}></div>
                <div className="grid-line h-line" style={{top: '60%'}}></div>
                <div className="grid-line h-line" style={{top: '80%'}}></div>
                <div className="grid-line v-line" style={{left: '20%'}}></div>
                <div className="grid-line v-line" style={{left: '40%'}}></div>
                <div className="grid-line v-line" style={{left: '60%'}}></div>
                <div className="grid-line v-line" style={{left: '80%'}}></div>
              </div>
            </div>
          </div>

          <div className="content-side">
            <div className="hero-content">
              <div className="hero-badge">
                <span className="badge-dot"></span>
                Next-Gen Container Orchestration
              </div>
              <h1 className="hero-title">
                welcome to<br />
                <span className="gradient-text">squarenetes</span>
              </h1>
              <p className="hero-description">
                a Kubernetes-powered platform that intelligently distributes AI workloads across multiple LLM providers (OpenAI, Anthropic, Google) based on their response speeds.
              </p>
              <div className="hero-actions">
                <button className="btn btn-primary" onClick={() => setCurrentPage('input')}>start prompting</button>
              </div>
              <div className="hero-stats">
                <div className="stat-item">
                  <div className="stat-number">99.9%</div>
                  <div className="stat-label">Uptime</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">10k+</div>
                  <div className="stat-label">Deployments</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">50ms</div>
                  <div className="stat-label">Response Time</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'input' && (
        <div className="input-page">
          <div className="input-container">
            <h2 className="page-title">execute multi-agent prompt</h2>
            
            <div className="form-section">
              <label className="form-label">enter your subprompt (the prompt each pod should complete)</label>
              <textarea
                className="text-input"
                placeholder="Summarize the main arguments supporting AI regulation in the U.S.,&#10;Summarize the arguments opposing AI regulation in the U.S.,&#10;Analyze potential compromises or middle-ground approaches to AI policy."
                value={subprompt}
                onChange={(e) => setSubprompt(e.target.value)}
                rows={4}
              />
            </div>
            <div className="form-section">
              <label className="form-label">number of times to execute</label>
              <textarea
                className="text-input"
                placeholder="3"
                value={n}
                onChange={(e) => setN(e.target.value)}
                rows={1}
              />
            </div>

            <div className="form-section">
              <label className="form-label">API Keys</label>
              <p className="form-hint">click on a sphere to enter API keys securely</p>
              
              <div className="spheres-container">
                {[0, 1, 2].map((index) => (
                  <div
                    key={index}
                    className={`sphere ${editingSphere === index ? 'sphere-editing' : ''} sphere-filled`}
                    onClick={() => handleSphereClick(index)}
                  >
                    {editingSphere === index ? (
                      <input
                        type="password"
                        className="sphere-input"
                        value={sphereTexts[index]}
                        onChange={handleSphereTextChange}
                        onBlur={handleSphereBlur}
                        autoFocus
                        placeholder="Enter API key..."
                      />
                    ) : (
                      <span className="sphere-text">
                        {sphereTexts[index] ? '•'.repeat(sphereTexts[index].length) : 'Enter API key'}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="form-actions">
              <button className="btn btn-primary" onClick={handleSubmit}>Submit</button>
              <button className="btn btn-secondary" onClick={handleReset}>Reset</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
