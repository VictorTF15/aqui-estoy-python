### 1. Project Structure

First, let's define a basic project structure:

```
/my_web_app
│
├── /src
│   ├── /components
│   │   ├── Modal.js
│   │   ├── Card.js
│   │   └── ...
│   ├── /pages
│   │   ├── LoginPage.js
│   │   ├── UserDashboard.js
│   │   └── AdminDashboard.js
│   ├── /api
│   │   ├── api.js
│   ├── App.js
│   └── index.js
│
├── /public
│   └── index.html
│
└── package.json
```

### 2. Setting Up API Consumption

Create an API utility to handle API requests. This will be used in both the user and admin versions.

**src/api/api.js**
```javascript
const API_BASE_URL = 'https://api.example.com'; // Replace with your API base URL

export const api = {
  login: async (credentials) => {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });
    return response.json();
  },
  // Add other API methods as needed
};
```

### 3. Creating the Login Page

Create a login page for normal users that consumes the login API.

**src/pages/LoginPage.js**
```javascript
import React, { useState } from 'react';
import { api } from '../api/api';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await api.login({ email, password });
      if (response.success) {
        // Handle successful login (e.g., redirect to dashboard)
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default LoginPage;
```

### 4. Creating Reusable Components

Create reusable components like modals and cards to keep the code concise.

**src/components/Modal.js**
```javascript
import React from 'react';

const Modal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button onClick={onClose}>Close</button>
        {children}
      </div>
    </div>
  );
};

export default Modal;
```

**src/components/Card.js**
```javascript
import React from 'react';

const Card = ({ title, content }) => {
  return (
    <div className="card">
      <h2>{title}</h2>
      <p>{content}</p>
    </div>
  );
};

export default Card;
```

### 5. Modifying the Admin Dashboard

Update the existing admin dashboard to consume APIs as well.

**src/pages/AdminDashboard.js**
```javascript
import React, { useEffect, useState } from 'react';
import { api } from '../api/api';
import Card from '../components/Card';

const AdminDashboard = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const response = await api.getAdminData(); // Example API call
      setData(response.data);
    };
    fetchData();
  }, []);

  return (
    <div className="admin-dashboard">
      <h1>Admin Dashboard</h1>
      {data.map((item) => (
        <Card key={item.id} title={item.title} content={item.content} />
      ))}
    </div>
  );
};

export default AdminDashboard;
```

### 6. Main Application File

Finally, set up the main application file to route between the login page and the admin dashboard.

**src/App.js**
```javascript
import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import AdminDashboard from './pages/AdminDashboard';

const App = () => {
  return (
    <Router>
      <Switch>
        <Route path="/login" component={LoginPage} />
        <Route path="/admin" component={AdminDashboard} />
        {/* Add other routes as needed */}
      </Switch>
    </Router>
  );
};

export default App;
```

### 7. Styling

Add CSS styles for the components and pages to ensure a good user experience. You can use Tailwind CSS or any other CSS framework.

### 8. Running the Application

Make sure to install the necessary dependencies (like React Router) and run your application:

```bash
npm install
npm start
```

### Conclusion

This setup provides a basic structure for a web application with a login page for normal users and an admin dashboard that consumes APIs. You can expand upon this by adding more features, improving error handling, and enhancing the UI/UX.