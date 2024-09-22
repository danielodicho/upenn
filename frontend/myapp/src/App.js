// src/App.js
import React from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Content from "./components/Content";
import Chatbot from "./components/Chatbot";
import './App.css';
  
function App() {
  return (
    <div className="app">
      <Header />
      <div className="main">
        <Sidebar />
        <div className="content-wrapper">
          <Content />
          <Chatbot />
        </div>
      </div>
    </div>
  );
}

export default App;
