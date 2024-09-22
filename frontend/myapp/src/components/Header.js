// src/components/Header.js
import React, { useState } from "react";
import './Header.css'; // Add custom styles here

const Header = () => {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const toggleDropdown = () => setDropdownOpen(!dropdownOpen);

  return (
    <header className="header">
      <h1 className="logo">HiveMind.ai</h1>
      <div className="profile-menu">
        <img 
          src="/path-to-pfp.jpg" 
          alt="profile" 
          className="profile-pic" 
          onClick={toggleDropdown} 
        />
        {dropdownOpen && (
          <div className="dropdown">
            <ul>
              <li>Profile</li>
              <li>Logout</li>
            </ul>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
