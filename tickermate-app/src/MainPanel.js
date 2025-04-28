import React, { useEffect, useState } from 'react';
import TickerHeader from './TickerHeader';
import NewsSummary from './NewsSummary';
import tickermateLogo from './tickermate_logo.png';

const MainPanel = () => {
    const [newsSummary, setNewsSummary] = useState({});

    useEffect(() => {
        const fetchNewsSummary = async () => {
            try {
                const response = await fetch(
                    'http://127.0.0.1:8000/api/summary?ticker=MSFT&mode=day',
                    // {
                    //     method: 'GET',
                    //     headers: {
                    //         'Content-Type': 'application/json',
                    //     }
                    // }
                );
                const data = await response.json();
                setNewsSummary(data);
                console.log('News summary fetched:', data);
            } catch (error) {
                console.error('Error fetching news summary:', error);
            }
        };

        fetchNewsSummary();
    }
    , []);


    return (
        <div>
            <img src={tickermateLogo} 
                style={{ width: '150px', height: 'auto', marginBottom: '10px' }} 
            />
            <h1>TickerMate AI</h1>
            <TickerHeader
                data={newsSummary}
            />
            <NewsSummary
                data={newsSummary}
            />
        </div>
    );
};

export default MainPanel;