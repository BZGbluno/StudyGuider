import React from 'react'
import './Summary.css';
import { useEffect, useRef, useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons'
import { useNavigate, useLocation } from 'react-router-dom';
import { useTypewriter } from '../hooks/useTypewriter';
import FileUpload from '../components/FileUpload';

function Admin() {
    return (
      <div>
        <h1>Admin Dashboard</h1>
        <FileUpload></FileUpload>
      </div>
    );
  }

export default Admin