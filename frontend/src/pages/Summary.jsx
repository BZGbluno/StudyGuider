import React from 'react'
import './Summary.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons'
import { useNavigate } from 'react-router-dom';
import { useTypewriter } from '../hooks/useTypewriter';

function Summary() {

    const navigate = useNavigate();

    // 1. Get Request Summary Contents

    const fullSummary = `
    Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
  
    Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
  
    Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos.
    `;

    const typedText = useTypewriter(fullSummary, 10); // Speed (ms per character)

    return (
        <div className="container">
            <div className="summary-container">
                <div className="back-title">
                    <button
                    onClick={() => navigate(-1)}>
                        <FontAwesomeIcon icon={faArrowLeft} size="2x" />
                    </button>
                    <div>
                        <h2>Summary</h2>
                    </div>
                </div>
                <p className="typing-summary">{typedText}
                {typedText !== fullSummary && <span className="blinking-cursor">|</span>}
                </p>
            </div>
        </div>
    )
}

export default Summary