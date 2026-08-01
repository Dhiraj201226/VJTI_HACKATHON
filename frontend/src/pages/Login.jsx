import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = ({ setRole }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    
    // Check for fixed password
    if (password !== 'admin123') {
      alert('Invalid password. Hint: admin123');
      return;
    }

    // Simple mock authentication for the hackathon
    const cleanUsername = username.trim().toLowerCase();
    
    if (cleanUsername === 'officer') {
      setRole('Desk Officer');
      navigate('/');
    } else if (cleanUsername === 'deputy') {
      setRole('Deputy Secretary');
      navigate('/');
    } else if (cleanUsername === 'secretary') {
      setRole('Secretary');
      navigate('/');
    } else {
      alert('Invalid username. Try: officer, deputy, or secretary');
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Govt. Auth Portal</h2>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
              placeholder="officer / deputy / secretary"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
              placeholder="Enter any password"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            Sign In
          </button>
        </form>
        <div className="mt-4 text-sm text-gray-500 text-center">
          <p>Hackathon Demo Credentials:</p>
          <p>Password (for all users): <b>admin123</b></p>
          <hr className="my-2" />
          <p>Username: <b>officer</b> (Desk Officer)</p>
          <p>Username: <b>deputy</b> (Deputy Secretary)</p>
          <p>Username: <b>secretary</b> (Secretary)</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
