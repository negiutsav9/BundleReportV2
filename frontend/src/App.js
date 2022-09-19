//Importing React Modules
import React from 'react';
import {Route, Routes, Navigate} from 'react-router-dom'

//Additional Stylesheets
import './App.css';

//Import Components
import Home from './Components/Home'
import Dashboard from './Components/Dashboard'

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/dashboard" element={<Dashboard/>}/>
      </Routes>
    </div>
  );
}

export default App;
