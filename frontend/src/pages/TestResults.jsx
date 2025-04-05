import React from 'react'
import './TestResults.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft, faCheck, faXmark } from '@fortawesome/free-solid-svg-icons'
import { useNavigate, useLocation } from 'react-router-dom';
import { useState } from 'react';

function TestResults() {

    const location = useLocation();
    const { cards = [] } = location.state || {};
    console.log(cards)

    const incorrectCards = cards.filter(card => card.isCorrect === false);

    const navigate = useNavigate();

    return (
        <div className="container">
            <div className="result-container">
                <div className="back-title">
                    <div>
                        <h2>{cards.length - incorrectCards.length} Correct ✅</h2>
                        <h2>{incorrectCards.length} Wrong ❌</h2>
                    </div>
                </div>
                {
                    incorrectCards.length > 0 ? (
                        <>
                            <h3>Questions you missed:</h3>
                            <div className="incorrect-container">
                            {incorrectCards.map((card, index) => (
                                <div className="incorrect-card" key={index}>
                                    <strong>Q:</strong> {card.question}<br />
                                    <strong>A:</strong> {card.answer}
                                </div>
                            ))}
                            </div>
                        </>
                    ) : (
                        <h3>You got everything right 🎉</h3>
                    )
                }
                <div className="button-container">
                    <button
                    onClick={() => navigate(-1)}>
                        Try Again
                    </button>
                    <button
                    onClick={() => navigate(-2)}>
                        Exit Flashcards
                    </button>
                </div>
            </div>
        </div>
    )
}

export default TestResults
