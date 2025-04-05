import React, { useState } from 'react'
import './Dropdown.css'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCaretDown, faCaretUp } from '@fortawesome/free-solid-svg-icons'

function Dropdown() {
  const [isOpen, setIsOpen] = useState(false)
  const [selected, setSelected] = useState("Select an option")

  const options = ["Chapter 1: Introduction to Blank", "ch2", "ch3", "ch4"]

  return (
    <div className="dropdown">
      <button className="dropdown-toggle" onClick={() => setIsOpen(!isOpen)}>
        <div className="chapter-arrow">
            {selected}
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
            <li key={index} onClick={() => {
              setSelected(option)
              setIsOpen(false)
            }}>
              {option}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default Dropdown
