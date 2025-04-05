import { useState } from 'react'
import { useNavigate } from 'react-router-dom';
import './App.css'
import Textbook from './../components/Textbook';

function App() {

    // 1. GET hardcoded textbooks from API

    // 2. Display them all on the page inside textbook-container as a textbook component

    // 3. On textbook click, POST that specific book to the backend
    const navigate = useNavigate();
    const handleSubmit = (title) => {
        navigate('/parameter_creation', {state: { title } });
    }

    return (
        <div className="container">
            <div className="section-title">
                <h2>Select a textbook</h2>
            </div>
            <div className="textbook-container">
                <Textbook 
                // image="https://via.placeholder.com/300x200" 
                title="Introduction to React" 
                handleSubmit={() => handleSubmit("Introduction to React")}
                />
                <Textbook 
                // image="https://via.placeholder.com/300x200" 
                title="Introduction to Making 4000 Quid Overnight Millionaire"
                handleSubmit={() => handleSubmit("Introduction to Making 4000 Quid Overnight Millionaire")} 
                />
                <Textbook 
                // image="https://via.placeholder.com/300x200" 
                title="How to Shit Your Pants Effectively"
                handleSubmit={() => handleSubmit("How to Shit Your Pants Effectively")}
                />
            </div>
        </div>
    )
}

export default App
