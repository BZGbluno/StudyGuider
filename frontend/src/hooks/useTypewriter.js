import {useState, useEffect } from 'react';

// default value of 10
export function useTypewriter(text, speed = 10) {
    const [displayedText, setDisplayedText] = useState('');

    useEffect(() => {
        let index = 0;
        const interval = setInterval(() => {
            setDisplayedText(text.slice(0, index + 1));
            index++;
            if (index === text.length) clearInterval(interval);
        }, speed); // repeat interval every [speed] ms
        return () => clearInterval(interval);
    }, [text, speed]); // Ensures only interval is active

    return displayedText;
}

// This is a custom react hook a piece of JavaScript that I can use as a function

// React re-runs components every time the screen updates, therefore there would be multiple intervals, useEffect() controls that