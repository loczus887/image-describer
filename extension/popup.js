// Extension popup script with JWT Authentication
const API_URL = 'http://localhost:8000';
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_data';

let currentToken = null;
let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
  initializeExtension();
});

async function initializeExtension() {
  // Load token from chrome storage
  chrome.storage.local.get([TOKEN_KEY, USER_KEY], async (result) => {
    currentToken = result[TOKEN_KEY];
    currentUser = result[USER_KEY];

    if (currentToken) {
      const isValid = await verifyToken(currentToken);
      if (isValid) {
        showMainInterface();
        checkPendingImage();
      } else {
        showLoginInterface();
      }
    } else {
      showLoginInterface();
    }
  });
}

async function verifyToken(token) {
  try {
    const response = await fetch(`${API_URL}/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      const userData = await response.json();
      currentUser = userData;
      chrome.storage.local.set({ [USER_KEY]: userData });
      return true;
    }
    return false;
  } catch (error) {
    return false;
  }
}

function showLoginInterface() {
  document.body.innerHTML = `
    <div class="auth-container">
      <div class="extension-header">
        <h1>Image Describer</h1>
      </div>

      <div id="login-form" class="auth-form">
        <h2>Login</h2>
        <input type="text" id="username" placeholder="Username" class="auth-input" />
        <input type="password" id="password" placeholder="Password" class="auth-input" />
        <button id="login-btn" class="auth-button">Login</button>
        <p class="auth-switch">
          Don't have an account?
          <button id="show-register" class="link-button">Register</button>
        </p>
        <div id="auth-error" class="error-message" style="display: none;"></div>
      </div>

      <div id="register-form" class="auth-form" style="display: none;">
        <h2>Register</h2>
        <input type="text" id="reg-username" placeholder="Username" class="auth-input" />
        <input type="email" id="reg-email" placeholder="Email" class="auth-input" />
        <input type="password" id="reg-password" placeholder="Password (8+ chars)" class="auth-input" />
        <input type="password" id="reg-confirm" placeholder="Confirm Password" class="auth-input" />
        <button id="register-btn" class="auth-button">Register</button>
        <p class="auth-switch">
          Already have an account?
          <button id="show-login" class="link-button">Login</button>
        </p>
        <div id="reg-error" class="error-message" style="display: none;"></div>
      </div>
    </div>
  `;

  // Wait for DOM to be ready before adding event listeners
  setTimeout(() => {
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const showRegisterBtn = document.getElementById('show-register');
    const showLoginBtn = document.getElementById('show-login');
    const passwordInput = document.getElementById('password');

    if (loginBtn) loginBtn.addEventListener('click', handleLogin);
    if (registerBtn) registerBtn.addEventListener('click', handleRegister);
    if (showRegisterBtn) {
      showRegisterBtn.addEventListener('click', () => {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('register-form').style.display = 'block';
      });
    }
    if (showLoginBtn) {
      showLoginBtn.addEventListener('click', () => {
        document.getElementById('register-form').style.display = 'none';
        document.getElementById('login-form').style.display = 'block';
      });
    }
    if (passwordInput) {
      passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleLogin();
      });
    }
  }, 0);
}

async function handleLogin() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const errorDiv = document.getElementById('auth-error');

  if (!username || !password) {
    showError(errorDiv, 'Please enter username and password');
    return;
  }

  try {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (response.ok) {
      const data = await response.json();
      currentToken = data.access_token;
      chrome.storage.local.set({ [TOKEN_KEY]: currentToken });
      await verifyToken(currentToken);
      showMainInterface();
      checkPendingImage();
    } else {
      const error = await response.json();
      showError(errorDiv, error.detail || 'Login failed');
    }
  } catch (error) {
    showError(errorDiv, 'Connection error. Is backend running?');
  }
}

async function handleRegister() {
  const username = document.getElementById('reg-username').value;
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;
  const confirm = document.getElementById('reg-confirm').value;
  const errorDiv = document.getElementById('reg-error');

  if (!username || !email || !password || !confirm) {
    showError(errorDiv, 'Please fill all fields');
    return;
  }

  if (password !== confirm) {
    showError(errorDiv, 'Passwords do not match');
    return;
  }

  if (password.length < 8) {
    showError(errorDiv, 'Password must be 8+ characters');
    return;
  }

  try {
    const response = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });

    if (response.ok) {
      // Auto-login
      const loginResp = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await loginResp.json();
      currentToken = data.access_token;
      chrome.storage.local.set({ [TOKEN_KEY]: currentToken });
      await verifyToken(currentToken);
      showMainInterface();
      checkPendingImage();
    } else {
      const error = await response.json();
      showError(errorDiv, error.detail || 'Registration failed');
    }
  } catch (error) {
    showError(errorDiv, 'Connection error');
  }
}

function showMainInterface() {
  document.body.innerHTML = `
    <div id="root">
      <div class="extension-header">
        <h1>Image Describer</h1>
        <div class="user-controls">
          <span class="user-name">${currentUser?.username}</span>
          <button id="logout-btn" class="logout-btn">Logout</button>
        </div>
      </div>
      <div class="extension-content">
        <div id="upload-area" class="upload-area">
          <p>Right-click image → "Describe Image"</p>
          <p>Or upload below:</p>
          <input type="file" id="file-input" accept="image/*" />
        </div>
        <div id="description-area" class="description-area" style="display: none;">
          <h2>Description</h2>
          <div id="description-text"></div>
          <button id="read-aloud-btn">🔊 Read Aloud</button>
        </div>
        <div id="error-area" class="error-area" style="display: none;"></div>
      </div>
    </div>
  `;

  // Wait for DOM to be ready before adding event listeners
  setTimeout(() => {
    const fileInput = document.getElementById('file-input');
    const readAloudBtn = document.getElementById('read-aloud-btn');
    const logoutBtn = document.getElementById('logout-btn');

    if (fileInput) {
      fileInput.addEventListener('change', async (e) => {
        const file = e.target.files?.[0];
        if (file) await describeImage(file);
      });
    }

    if (readAloudBtn) {
      readAloudBtn.addEventListener('click', () => {
        const text = document.getElementById('description-text')?.textContent;
        if (text && 'speechSynthesis' in window) {
          window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
        }
      });
    }

    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        chrome.storage.local.remove([TOKEN_KEY, USER_KEY]);
        currentToken = null;
        currentUser = null;
        showLoginInterface();
      });
    }
  }, 0);
}

async function describeImage(file) {
  const errorArea = document.getElementById('error-area');
  const descriptionArea = document.getElementById('description-area');
  const uploadArea = document.getElementById('upload-area');

  errorArea.style.display = 'none';
  descriptionArea.style.display = 'none';

  const originalContent = uploadArea.innerHTML;
  uploadArea.innerHTML = '<p>⏳ Processing...<br><small>May take a few minutes</small></p>';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_URL}/describe`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${currentToken}` },
      body: formData,
    });

    if (response.status === 401) {
      // Token expired
      chrome.storage.local.remove([TOKEN_KEY, USER_KEY]);
      showLoginInterface();
      return;
    }

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
      document.getElementById('description-text').innerHTML = data.description.replace(/\n/g, '<br>');
      descriptionArea.style.display = 'block';
      descriptionArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      throw new Error(data.error || 'Failed to generate description');
    }

    uploadArea.innerHTML = originalContent;
    // Re-attach event listener after restoring HTML
    setTimeout(() => {
      const fileInput = document.getElementById('file-input');
      if (fileInput) {
        fileInput.addEventListener('change', async (e) => {
          const file = e.target.files?.[0];
          if (file) await describeImage(file);
        });
      }
    }, 0);

  } catch (error) {
    uploadArea.innerHTML = originalContent;
    showError(errorArea, error.message);
    // Re-attach event listener after restoring HTML
    setTimeout(() => {
      const fileInput = document.getElementById('file-input');
      if (fileInput) {
        fileInput.addEventListener('change', async (e) => {
          const file = e.target.files?.[0];
          if (file) await describeImage(file);
        });
      }
    }, 0);
  }
}

function checkPendingImage() {
  chrome.storage.local.get(['pendingImageUrl'], (result) => {
    if (result.pendingImageUrl) {
      chrome.storage.local.remove(['pendingImageUrl']);
      const uploadArea = document.getElementById('upload-area');
      uploadArea.innerHTML = '<p>⏳ Loading image...</p>';

      fetch(result.pendingImageUrl)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], 'image.jpg', { type: blob.type || 'image/jpeg' });
          describeImage(file);
        })
        .catch(err => {
          const errorArea = document.getElementById('error-area');
          showError(errorArea, `Error loading image: ${err.message}`);
          uploadArea.innerHTML = `
            <p>Right-click image → "Describe Image"</p>
            <p>Or upload below:</p>
            <input type="file" id="file-input" accept="image/*" />
          `;
          // Re-attach event listener after restoring HTML
          setTimeout(() => {
            const fileInput = document.getElementById('file-input');
            if (fileInput) {
              fileInput.addEventListener('change', async (e) => {
                const file = e.target.files?.[0];
                if (file) await describeImage(file);
              });
            }
          }, 0);
        });
    }
  });
}

function showError(element, message) {
  element.textContent = message;
  element.style.display = 'block';
}

// Listen for messages from context menu
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'describeImage' && request.imageUrl) {
    fetch(request.imageUrl)
      .then(res => res.blob())
      .then(blob => {
        const file = new File([blob], 'image.jpg', { type: blob.type });
        describeImage(file);
      })
      .catch(err => {
        const errorArea = document.getElementById('error-area');
        if (errorArea) showError(errorArea, `Error: ${err.message}`);
      });
    return true;
  }
});
