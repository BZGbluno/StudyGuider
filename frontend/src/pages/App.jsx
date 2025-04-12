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
              setTextbooks(data.response);
              sessionStorage.setItem("textbooks", JSON.stringify(data.response));
            })
            .catch(error => console.error('Error fetching textbooks:', error));
        }
      }, []);

      const imgs = ["https://greenteapress.com/thinkpython2/think_python2_medium.jpg"];
      
    // callback function: ???
    const handleSubmit = (title, image) => {
        navigate('/parameter_creation', { state: { title, image } });
    }

    return (
        <div className="container">
            <div className="welcome-container">
                <h1>StudyGuido</h1>
                <p>A study helper to assist you in learning more effectively from textbooks by using AI-powered tools. </p>
            </div>
            <div>
                <div className="section-title">
                    <h2>Select a textbook <span className="celebrate-emoji">📚</span></h2>
                </div>
                <div className="textbook-container">
                    {textbooks.map((title, index) => (
                        <Textbook
                            image={imgs[index]} // set the image prop
                            key={index}
                            title={title}
                            handleSubmit={() => handleSubmit(title, imgs[index])}
                        />
                    ))}
                </div>
            </div>
        </div>
    )
}

export default App;
