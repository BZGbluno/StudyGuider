import React from 'react';
import './Textbook.css'
import { useState } from 'react'

const Textbook = ({ title, image, desc, author, handleSubmit }) => {
const [popup, setPopup] = useState(false)

  return (
    <>
        <div className="textbook"
        onClick={() => setPopup(true)}
        >
            <img 
                src={image}
                alt={title} 
                className="img"
            />
            <h2>{title}</h2>
        </div>
        
            <div className={`popup-overlay ${popup ? 'open' : ''}`}>
                <div className="popup-content">
                    <button className="exit" onClick={() => setPopup(false)}>X</button>
                    <img 
                        src={image} 
                        alt={title} 
                        className="img"
                    />
                    <div>
                        <h1>{title}</h1>
                        <p>{author}</p>
                        <p className="desc">{desc}</p>
                    </div>
                    <button className="sub-btn" onClick={() => handleSubmit(title, image)}>Confirm ✔️</button>
                </div>
            </div>
    </>
  );

};

export default Textbook;
