import React, { useState } from 'react'
import './Chatbot.css'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowUp } from '@fortawesome/free-solid-svg-icons'
import { useTypewriter } from '../hooks/useTypewriter';

function Chatbot({ selectedChapter, selectedTitle}) {
    const [inputValue, setInputValue] = useState('');
    const [responseText, setResponseText] = useState('');
    const [questionText, setQuestionText] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        setLoading(true);
        if (!inputValue.trim()) return;
    
        if (inputValue.length > 50) {
            alert("Please limit your message to 50 characters or fewer.");
            return;
        }
    
        // Process the message here...
        // 1. POST request: message and return the response
        // use custom react hook to do typing effect

        try {
            setQuestionText(inputValue);
            setInputValue('');
            const response = await fetch('http://localhost:8000/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: inputValue,
                    chapter: selectedChapter,
                    textbook: selectedTitle,
                }),
            });

            const data = await response.json();
            console.log("Response from server:", data);

            setResponseText(data.response || "No response received.");
        } catch (error) {
            console.error("POST request failed:", error);
            setResponseText("Oops! Something went wrong.");
        } finally {
            setLoading(false);
        }
    };

    const typedText = useTypewriter(responseText, 10); // Speed (ms per character)
    

    return (
        <div className="chatbot-container chatbot-fade-in">
            <div>
                <h2>Ask AI</h2>
            </div>
            <div className="summary-scroll-chatbot">
                <div className="typing-summary-chat">
                    {loading ? (
                        <img className="giffy-chat" src="../../public/spin.gif" alt="loading animation" />
                ) : (
                        <>
                            {questionText && (
                            <div className="chat-question">
                                <strong>You asked:</strong> {questionText}
                            </div>
                            )}
                            <div className="chat-response">
                            {typedText}
                            </div>
                        </>
                    )}
                </div>
            </div>
            <div className="text-send">
                <input 
                        className="textbox"
                        type="text"
                        placeholder="Ask something..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSend();
                        }}
                    />
                <button id="sum-btn" onClick={handleSend}>
                    <FontAwesomeIcon icon={faArrowUp} size="2x" />
                </button>
            </div>
        </div>
    )
}

export default Chatbot