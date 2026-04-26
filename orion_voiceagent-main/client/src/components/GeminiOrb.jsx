import React from 'react';
import './GeminiOrb.css';

const GeminiOrb = ({ state }) => {
    return (
        <div className={`gemini-orb-container ${state}`}>
            <div className="gemini-orb">
                <div className="smooth-gradient-fill"></div>
                <div className="orb-shine"></div>
            </div>

            {/* Soft subtle glow */}
            <div className="orb-glow-external"></div>
        </div>
    );
};

export default GeminiOrb;
 
 
 
 
 
 
 
 
 
 
 
