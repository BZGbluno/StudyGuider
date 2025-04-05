import React from 'react'
import './Test.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft, faCheck, faXmark } from '@fortawesome/free-solid-svg-icons'
import { useNavigate } from 'react-router-dom';
import Flashcard from '../components/Flashcard';
import { useState } from 'react';

function Test() {
    const navigate = useNavigate();

    // 1. Extract GET Request of Questions

    // 2. Render all the questions into cards: Array of Objects
    const [cards, setCards] = useState([
        { question: "What's your name?", answer: "Nivar", isCorrect: null },
        { question: "What's your poop color bro?", answer: "Brown", isCorrect: null },
        { question: "Mamaguevo or Mamahuevos?", answer: "Eggs", isCorrect: null },
      ])
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [correct, setCorrect] = useState(0);
    const [incorrect, setIncorrect] = useState(0);

    // 3. Handle user checking card, move onto the next
    const handleCheck = () => {
        const updated = [...cards]; // unpack all the current cards
        updated[currentQuestionIndex].isCorrect = true;
        setCards(updated)

        if (currentQuestionIndex < cards.length - 1) {
            setCorrect(correct + 1)
            setCurrentQuestionIndex(currentQuestionIndex + 1)
        } else if (currentQuestionIndex === cards.length - 1) {
            navigate('/results', {state: {cards: updated} }) // passing the updated object (react nuance)
        }
    }

    // 4. Handle user x'ing card, move onto the next
    const handleX = () => {

        const updated = [...cards]; // unpack all the current cards
        updated[currentQuestionIndex].isCorrect = false;
        setCards(updated)

        if (currentQuestionIndex < cards.length - 1) {
            setIncorrect(incorrect + 1)
            setCurrentQuestionIndex(currentQuestionIndex + 1)
        } else if (currentQuestionIndex === cards.length - 1) {
            // 5. IF FINAL CARD, once moved forward, navigate to Test Summary Page
            // Pass # of correct/incorrect to next page to display (useLocation() probably)
            navigate('/results', {state: {cards: updated} }) // passing the updated object (react nuance)
        }
    }

    return (
        <div className="container">
            <div className="test-container">
                <div className="back-title">
                    <button
                    onClick={() => navigate(-1)}>
                        <FontAwesomeIcon icon={faArrowLeft} size="2x" />
                    </button>
                    <div>
                        <h2>{currentQuestionIndex + 1} / {cards.length}</h2>
                    </div>
                </div>

                {/* Render Flashcards Dynamically */}
                <Flashcard
                    Question={cards[currentQuestionIndex].question}
                    Answer={cards[currentQuestionIndex].answer}
                />
                <div className="button-container">
                    <button
                    id="x"
                    onClick={handleX}>
                        <FontAwesomeIcon icon={faXmark} size="2x" />
                    </button>
                    <button 
                    id="check"
                    onClick={handleCheck}>
                        <FontAwesomeIcon icon={faCheck} size="2x" />
                    </button>
                </div>
            </div>
        </div>
    )
}

export default Test