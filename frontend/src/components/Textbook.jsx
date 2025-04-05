import React from 'react';
import './Textbook.css'

const Textbook = ({ title, handleSubmit }) => {
  return (
    <div className="textbook"
    onClick={handleSubmit}
    >
      {/* <img 
        src={image} 
        alt={title} 
        style={{ width: '100%', borderRadius: '4px' }} 
      /> */}
      <h3>{title}</h3>
    </div>
  );
};

export default Textbook;
