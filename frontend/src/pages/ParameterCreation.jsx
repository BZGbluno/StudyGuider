import React from 'react'
import { useState, useEffect } from 'react'
import './ParameterCreation.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons'
import { useNavigate, useLocation } from 'react-router-dom';
import Dropdown from '../components/Dropdown';

function ParameterCreation() {
    const location = useLocation();
    const { title, image } = location.state || { title: "No title received" };
    const navigate = useNavigate();
    const [chapters, setChapters] = useState([]);
    const [selectedChapter, setSelectedChapter] = useState(null)
    const [selectFlag, setSelectFlag] = useState(false)

    // Get Request of Selected Book Table of Contents
    useEffect(() => {
        if (!title) return; // wait for textbook to be selected

        fetch(`http://localhost:8000/api/getChapters?textbook=${encodeURIComponent(title)}`)
            .then(response => {
                if (!response.ok) throw new Error("Failed to fetch chapters");
                return response.json();
            })
            .then(data => setChapters(data.response))
            .catch(error => console.error('Error fetching chapters:', error));
    }, [title]);

    const handleChapterSelect = (option) => {
        setSelectedChapter(option)
        setSelectFlag(false)
        sessionStorage.setItem("selectedChapter", option);
      }

      useEffect(() => {
        const storedChapter = sessionStorage.getItem("selectedChapter");
        if (storedChapter) {
          setSelectedChapter(storedChapter);
        }
      }, []);

    // redirect to summary pass textbook & ch object to summary
    const handleSummary = () => {
        if (selectedChapter) {

            const textbookData = {
                selectedTitle: title,
                selectedChapter: selectedChapter,
            };

            navigate('/summary', { state: textbookData });
        } else {
            setSelectFlag(true);
        }
    }

    // redirect to flashcards pass textbook & ch object to summary
    const handleFlashCards = () => {
        if (selectedChapter) {

            const textbookData = {
                selectedTitle: title,
                selectedChapter: selectedChapter,
            };

            navigate('/test', { state: textbookData })
        } else {
            setSelectFlag(true);
        }
    }

    return (
        <div className="p-container">
            <div className="back-title">
                <button
                onClick={() => navigate(-1)}>
                    <FontAwesomeIcon icon={faArrowLeft} size="2x" />
                </button>
                <h2 className="section-title">
                    Selected textbook 📚
                </h2>
            </div>
            <div className="selected-book">
                <img 
                    src={image} 
                    alt={title} 
                    className="img"
                />
                <h2>{title}</h2>
            </div>
            <div className="parameter-container">
                <h2>Choose a chapter</h2>
                {selectFlag && (
                    <p className="error-message">Please select a chapter from the given list</p>
                )}
                <Dropdown options={chapters} onSelect={handleChapterSelect} value={selectedChapter}/>
                <div className="button-container">
                    <button
                    onClick={handleSummary}>
                        <h2>
                        Create Summary 📝
                        </h2>
                    </button>
                    <button 
                    onClick={handleFlashCards}>
                        <h2>
                            Test your knowledge 🧠
                        </h2>
                    </button>
                </div>
            </div>
        </div>
    )
}

export default ParameterCreation