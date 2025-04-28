import React, { useEffect, useState } from 'react';
import TickerHeader from './TickerHeader';
import NewsSummary from './NewsSummary';
import tickermateLogo from './tickermate_logo.png';

const SearchBar = ({onSearch}) => {
    const [ticker, setTicker] = useState('');
    return (
        <div>
            <input 
                type="text" 
                placeholder="Search Ticker..."
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
            />
            <button onClick={() => onSearch(ticker)}>Search</button>
        </div>
    );
}

const MainPanel = () => {
    const [newsSummary, setNewsSummary] = useState({});
    const [ticker, setTicker] = useState('');

    useEffect(() => {
        if (ticker) {
            fetchNewsSummary();
        }
    }, [ticker]);

    const fetchNewsSummary = async () => {
        try {
            const response = await fetch(
                `http://127.0.0.1:8000/api/summary?ticker=${ticker}&mode=day`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );
            const data = await response.json();
            setNewsSummary(data);
        } catch (error) {
            console.error('Error fetching news summary:', error);
        }
    };

    const handleSearch = (ticker) => {
        setTicker(ticker);
    };

    return (
        <div>
            <img src={tickermateLogo} 
                style={{ width: '150px', height: 'auto', marginBottom: '10px' }} 
            />
            <h1>TickerMate AI</h1>
            <SearchBar
                onSearch={handleSearch}
            />
            <TickerHeader
                ticker={newsSummary["ticker"]}
                name={newsSummary["name"]}
                price={newsSummary["price"]}
                change={newsSummary["change"]}
                sector={newsSummary["sector"]}
                highlight={newsSummary["AI Hightlight"]}
            />
            <NewsSummary
                news={newsSummary["News Summary"]}
            />
        </div>
    );
};

export default MainPanel;