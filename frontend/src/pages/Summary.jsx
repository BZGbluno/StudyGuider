import React from 'react'
import './Summary.css';
import { useEffect, useRef, useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons'
import { useNavigate, useLocation } from 'react-router-dom';
import { useTypewriter } from '../hooks/useTypewriter';
import Chatbot from '../components/Chatbot';

function Summary() {

    const navigate = useNavigate();
    const location = useLocation();
    const scrollRef = useRef(null);
    const { selectedTitle, selectedChapter } = location.state || {};

    // 1. POST Request: Summary Contents
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


    const fullSummary = `Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
  
    Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
  
    Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
    `;

    const typedText = useTypewriter(fullSummary, 10); // Speed (ms per character)
    const [isUserScrolling, setIsUserScrolling] = useState(false);
    // const [showChatbot, setShowChatbot] = useState(false);

    // useEffect(() => {
    //     if (typedText === fullSummary) {
    //       setShowChatbot(true);
    //     }
    //   }, [typedText, fullSummary]);

    // 1. Handle user scrolling manually
    useEffect(() => {
        const handleScroll = () => {
        if (!scrollRef.current) return;
    
        const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
        const isNearBottom = scrollHeight - scrollTop <= clientHeight + 10;
    
        if (!isNearBottom) {
            setIsUserScrolling(true);
        } else {
            setIsUserScrolling(false); // if they scroll back to bottom
        }
        };
    
        const scrollEl = scrollRef.current;
        scrollEl?.addEventListener('scroll', handleScroll);
        return () => scrollEl?.removeEventListener('scroll', handleScroll);
    }, []);
    
    // 2. Auto-scroll only if user hasn’t manually scrolled up
    useEffect(() => {
        if (!scrollRef.current || isUserScrolling) return;
    
        // Use requestAnimationFrame to ensure DOM is ready
        requestAnimationFrame(() => {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        });
    }, [typedText, isUserScrolling]);

    return (
        <div className="s-container">
            <div className="summary-container">
                <div className="back-title">
                    <button
                    id="sum-btn"
                    onClick={() => navigate(-1)}>
                        <FontAwesomeIcon icon={faArrowLeft} size="2x" />
                    </button>
                    <div>
                        <h2>Summary 📝</h2>
                    </div>
                </div>
                <div className="summary-scroll" ref={scrollRef}>
                <p className="typing-summary">{typedText}
                {typedText !== fullSummary && <span className="blinking-cursor">|</span>}
                </p>
                </div>
            </div>
            <Chatbot />
        </div>
    )
}

export default Summary