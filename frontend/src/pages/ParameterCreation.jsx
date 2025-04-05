import React from 'react'
import './ParameterCreation.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons'
import { useNavigate, useLocation } from 'react-router-dom';
import Dropdown from '../components/Dropdown';


function ParameterCreation() {
    const location = useLocation();
    const { title } = location.state || { title: "No title received" };
    const navigate = useNavigate();

    // 1. Get Request of Selected Book Table of Contents

    // 2. Render those contents onto dropdown menu

    // 3. POST chapter and summary option to API
    const handleSummary = () => {
        navigate('/summary');
    }

    // 4. POST chapter and Test option to API
    const handleFlashCards = () => {
        navigate('/test')
    }

    return (
        <div className="container">
            <div className="back-title">
                <button
                onClick={() => navigate(-1)}>
                    <FontAwesomeIcon icon={faArrowLeft} size="2x" />
                </button>
                <h2 className="section-title">
                    Selected textbook
                </h2>
            </div>
            <div className="selected-book">
                <h3>{title}</h3>
            </div>
            <div className="parameter-container">
                <h2>Choose a chapter</h2>
                <Dropdown />
                <div className="button-container">
                    <button
                    onClick={handleSummary}>
                        Create Summary
                    </button>
                    <button 
                    onClick={handleFlashCards}>
                        Test your knowledge
                    </button>
                </div>
            </div>
        </div>
    )
}

export default ParameterCreation