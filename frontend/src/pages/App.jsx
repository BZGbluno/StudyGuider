import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';
import './App.css'
import Textbook from './../components/Textbook';

function App() {
    const [textbooks, setTextbooks] = useState([]);
    const navigate = useNavigate();

    // TODO if textbook has already been selected, essentially when I do the back arrow, dont recall the API, leverage session storage
    useEffect(() => {
        const storedTextbooks = sessionStorage.getItem("textbooks");
        if (storedTextbooks) {
          setTextbooks(JSON.parse(storedTextbooks));
        } else {
          fetch('http://localhost:8000/api/getTextbooks')
            .then(response => {
              if (!response.ok) throw new Error("Failed to fetch textbooks");
              return response.json();
            })
            .then(data => {
                console.log(data.response)
              setTextbooks(data.response);
              sessionStorage.setItem("textbooks", JSON.stringify(data.response));
            })
            .catch(error => console.error('Error fetching textbooks:', error));
        }
      }, []);

        // callback function: ???
        const handleSubmit = (textbook) => {
            navigate('/parameter_creation', {
                state: {
                    title: textbook.title,
                    image: textbook.image_path,
                },
            });
        }    

    return (
        <div className="container">
            <div className="welcome-container">
                <h1>StudyGuido</h1>
                <img 
                        src="../../public/guido2.png"
                        alt="GuidoBot"
                        className="img-g"
                />
                <p>A study helper to assist you in learning more effectively from textbooks by using AI-powered tools. </p>
            </div>
            <div>
                <div className="section-title">
                    <h2>Select a textbook <span className="celebrate-emoji">📚</span></h2>
                </div>
                <div className="textbook-container">
                    {textbooks.map((textbook, index) => (
                        <Textbook
                            key={index}
                            title={textbook.title}
                            desc={textbook.description}
                            author={textbook.author}
                            image={textbook.image_path}
                            handleSubmit={() => handleSubmit(textbook)}
                        />
                    ))}
                </div>
            </div>
        </div>
    )
}

export default App;
