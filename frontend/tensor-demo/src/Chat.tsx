import React, { useState, useEffect, useRef } from 'react';
import './Chat.css';

interface Message {
  text: string;
  fromUser: boolean;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = { text: input, fromUser: true };
      setMessages(prevMessages => [...prevMessages, userMessage]);
      setInput('');

      try {
        const response = await fetch('/api/generate_text', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Token': 'wApHyPeLdaNtORDownsEPIcKinARTHO', // TODO: Store this securely when not just demoing
          },
          body: JSON.stringify({ seed_text: input }),
        });

        if (!response.ok) {
          throw new Error('Failed to generate text');
        }

        const data = await response.json();
        const llmMessage = { text: data.generated_text, fromUser: false };
        setMessages(prevMessages => [...prevMessages, llmMessage]);
      } catch (error) {
        console.error('Error:', error);
        const errorMessage = { text: 'Sorry, an error occurred. Please try again.', fromUser: false };
        setMessages(prevMessages => [...prevMessages, errorMessage]);
      }
    }
  };

  return (
      <div className="chat-container">
        <div className="chat-window">
          <div className="chat-messages">
            {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.fromUser ? 'from-user' : 'from-llm'}`}>
                  {msg.text}
                </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <div className="chat-input">
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your message..."
            />
            <button onClick={handleSend}>Send</button>
          </div>
        </div>
      </div>
  );
};

export default Chat;