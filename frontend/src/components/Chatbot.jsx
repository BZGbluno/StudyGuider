import React, { useState } from 'react'
import './Chatbot.css'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowUp } from '@fortawesome/free-solid-svg-icons'

function Chatbot() {
    const [inputValue, setInputValue] = useState('');

    const handleSend = () => {
        if (!inputValue.trim()) return;
    
        if (inputValue.length > 50) {
            alert("Please limit your message to 50 characters or fewer.");
            return;
        }
    
        // Process the message here...
        // 1. POST request: message and return the response
        // use custom react hook to do typing effect

    // useEffect(() => {
    //     const sendPostRequest = async () => {
    //       try {
    //         const response = await fetch('https://your-api.com/summary', {
    //           method: 'POST',
    //           headers: {
    //             'Content-Type': 'application/json',
    //           },
    //           body: JSON.stringify({
    //             title: selectedTitle,
    //             chapter: selectedChapter,
    //           }),
    //         });
      
    //         const data = await response.json();
    //         console.log("Response from server:", data);

    //       } catch (error) {
    //         console.error("POST request failed:", error);
    //       }
    //     };
      
    //     if (selectedTitle && selectedChapter) {
    //       sendPostRequest();
    //     }
    //   }, [selectedTitle, selectedChapter]);

        console.log("Sending message:", inputValue);
    
        setInputValue('');
    };
    

    return (
        <div className="chatbot-container chatbot-fade-in">
            <div>
                <h2>Ask AI</h2>
            </div>
            <div className="summary-scroll-chatbot">
                <p className="typing-summary">
                    Ask my goat for advice!
                </p>
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