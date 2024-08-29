import React from 'react';
import Chat from './Chat';
import './Home.css';

const Home: React.FC = () => {
  return (
    <div className="home-container">
      <header className="home-header">
        <img src="./images/logo.jpeg" alt="Initech Logo" className="company-logo" />
        <h1>Knowledge Portal</h1>
      </header>
      <main className="main-content">
        <section className="welcome-section">
          <h2>Welcome to Initech's Internal Resource Center</h2>
          <p>Streamlining processes and enhancing productivity across all departments</p>
        </section>
        <section className="chat-section">
          <h3>Ask the Initech AI Assistant</h3>
          <p>Need help with company policies, TPS reports, or office equipment? I'm here to assist!</p>
          <Chat />
        </section>
      </main>
      <footer className="home-footer">
        <p>&copy; 2024 Initech Corporation. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Home;