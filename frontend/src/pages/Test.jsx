import React from 'react'
import './Test.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft, faCheck, faXmark } from '@fortawesome/free-solid-svg-icons'
import { useNavigate, useLocation } from 'react-router-dom';
import Flashcard from '../components/Flashcard';
import { useState, useEffect } from 'react';

function Test() {
    const navigate = useNavigate();
       const location = useLocation();
        const { selectedTitle, selectedChapter } = location.state || {};
    
        const numQuestions = 10;
    
        // 1. POST Request: Summary Contents
        useEffect(() => {
            const fetchFlashcards = async () => {
              try {
                const response = await fetch('http://localhost:8000/api/generateFlashCard', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    chapter: selectedChapter,
                    textbook: selectedTitle,
                    count: numQuestions,
                  })
                });
          
                const data = await response.json();
                console.log("Response from server:", data);

                const flashcards = data.response;

                const formatted = Object.entries(flashcards).map(([key, [question, answer]]) => ({
                    question,
                    answer,
                    isCorrect: null
                }));

                setCards(formatted);
    
              } catch (error) {
                console.error("POST request failed:", error);
              }
            };
          
            if (selectedTitle && selectedChapter) {
              fetchFlashcards();
            }
        }, [selectedTitle, selectedChapter]);

    // 2. Render all the questions into cards: Array of Objects
    const [cards, setCards] = useState([
        { question: "What's your name?", answer: "Nivar", isCorrect: null },
        { question: "What's your poop color bro?", answer: "Brown", isCorrect: null },
        { question: "Mamaguevo or Mamahuevos?", answer: "Eggs", isCorrect: null },
      ])
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [correct, setCorrect] = useState(0);
    const [incorrect, setIncorrect] = useState(0);
    const [flipped, setFlipped] = useState(false);
    const [disableAnimation, setDisableAnimation] = useState(false);

    // 3. Handle user checking card, move onto the next
    const handleCheck = () => {
        const updated = [...cards]; // unpack all the current cards
        updated[currentQuestionIndex].isCorrect = true;
        setCards(updated)
        setFlipped(false)
        setDisableAnimation(true)

        setTimeout(() => {
            setDisableAnimation(false); // re-enable after render
          }, 0); // minimal timeout to allow render to complete

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
        setFlipped(false)
        setDisableAnimation(true)

        setTimeout(() => {
            setDisableAnimation(false); // re-enable after render
          }, 0); // minimal timeout to allow render to complete

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
        <div className="t-container">
            <div className="test-container">
                <div className="back-title">
                    <button
                    id="tst-btn"
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
                    flipped={flipped}
                    setFlipped={setFlipped}
                    disableAnimation={disableAnimation}
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