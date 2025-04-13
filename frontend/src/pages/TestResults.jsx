import React from 'react'
import './TestResults.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft, faCheck, faXmark } from '@fortawesome/free-solid-svg-icons'
import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Confetti from 'react-confetti';
import { useWindowSize } from '@react-hook/window-size';


function TestResults() {

    const [width, height] = useWindowSize();
    const location = useLocation();

    const [showConfetti, setShowConfetti] = useState(false);
    const { cards = [] } = location.state || {};
    const incorrectCards = cards.filter(card => card.isCorrect === false);

    useEffect(() => {
      // only show confetti if all answers are correct
  
      if (cards.length > 0 && incorrectCards.length === 0) {
        setShowConfetti(true);
        const timeout = setTimeout(() => {
          setShowConfetti(false);
        }, 9000); // 🎉 confetti time
  
        return () => clearTimeout(timeout);
      }
    }, []);

    const handleReshuffle = () => {

        sessionStorage.setItem("reshuffle", "true");
        navigate(-1)

        // pass true to previous page
        // navigate('/test', {
        //     replace: true,
        //     state: { reshuffle: true }
        // });
    };

    const navigate = useNavigate();

    return (
        <div className="tr-container">
            {showConfetti && <Confetti width={width} height={height} numberOfPieces={200} recycle={false} />}
            <div className="result-container">
                {
                    incorrectCards.length > 0 ? (
                        <h3>{cards.length - incorrectCards.length}/{cards.length} Correct</h3>
                    ) : (
                        <h3>You got everything right <span className="celebrate-emoji">🎉</span></h3>
                    )
                }
                <div className="card-container">
                    {cards.map((card, index) => {
                        if (card.isCorrect === true) {
                            return (
                                <div className="correct-card" key={index}>
                                    <strong>Q:</strong> {card.question}<br />
                                    <strong>A:</strong> {card.answer}
                                </div>
                            );
                        } else {
                            return (
                                <div className="incorrect-card" key={index}>
                                    <strong>Q:</strong> {card.question}<br />
                                    <strong>A:</strong> {card.answer}
                                </div>
                            );
                        }
                    })}
                </div>
                <div className="button-container">
                    {/* {
                        incorrectCards.length > 0 ? ( // new behavior:
                            <button
                            id="try"
                            
                            onClick={() => navigate(-1)}>
                                <h2>
                                    Try Again & Shuffle 🔁
                                </h2>
                            </button>
                        ) : ( // default behavior: is to generate new deck based on that subject
                            <button
                            id="try"
                            onClick={() => navigate(-1)}>
                                <h2>
                                    
                                    Generate New Deck 🔁 
                                </h2>
                            </button>
                        )
                    } */}
                    <button
                        id="try"
                        onClick={() => handleReshuffle()}>
                            <h2>
                                Try Again & Shuffle 🔁
                            </h2>
                    </button>
                    <button
                    id="try"
                    onClick={() => navigate(-2)}>
                        <h2>
                            Exit flashcards 🚪👋
                        </h2>
                    </button>
                </div>
            </div>
        </div>
    )
}

export default TestResults
