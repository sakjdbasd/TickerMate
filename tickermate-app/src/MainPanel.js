import React from 'react';
import TickerHeader from './TickerHeader';
import NewsSummary from './NewsSummary';
import tickermateLogo from './tickermate_logo.png';

const MainPanel = () => {
    return (
        <div>
            <img src={tickermateLogo} 
                style={{ width: '150px', height: 'auto', marginBottom: '10px' }} 
            />
            <h1>TickerMate AI</h1>
            <TickerHeader />
            <NewsSummary />
        </div>
    );
};

export default MainPanel;