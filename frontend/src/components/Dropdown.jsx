import React, { useState, useEffect } from 'react'
import './Dropdown.css'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCaretDown, faCaretUp } from '@fortawesome/free-solid-svg-icons'

function Dropdown({ options = [], onSelect, value }) {
  const [isOpen, setIsOpen] = useState(false)
  const [selected, setSelected] = useState("Select an option")

  const handleSelect = (option) => {
    setSelected(option)
    setIsOpen(false)
    if (onSelect) {
      onSelect(option) // call the parent callback
    }
  }

    // Whenever value changes (from session or user), update the local display
    useEffect(() => {
      if (value) {
        setSelected(value);
      }
    }, [value]);

  return (
    <div className="dropdown">
      <button className="dropdown-toggle" onClick={() => setIsOpen(!isOpen)}>
        <div className="chapter-arrow">
            <h3>
            {selected}
            </h3>
            <div className="img-container">
                {
                isOpen
                    ? <FontAwesomeIcon icon={faCaretUp} size="xl" />
                    : <FontAwesomeIcon icon={faCaretDown} size="xl" />
                }
            </div>
        </div>
      </button>

      {isOpen && (
        <ul className="dropdown-menu">
          {options.map((option, index) => (
            <li key={index} onClick={() => handleSelect(option)}>
              {option}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default Dropdown
