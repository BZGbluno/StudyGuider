import React, { useState } from 'react'
import './Flashcard.css'

function Flashcard({ Question, Answer }) {
    const [flipped, setFlipped] = useState(false)

    

    return (
        <div className="card"
        onClick={() => setFlipped(!flipped)}>
            <div className={`card-inner ${flipped ? 'flipped' : ''}`}>
                <div className="card-front">
                    {Question}
                </div>
                <div className="card-back">
                    {Answer}
                </div>
            </div>
        </div>
    )
}

export default Flashcard