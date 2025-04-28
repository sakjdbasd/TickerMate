import React, { useEffect, useState } from 'react';
import TickerHeader from './TickerHeader';
import NewsSummary from './NewsSummary';
import tickermateLogo from './tickermate_logo.png';

const SearchBar = ({onSearch}) => {
    const [ticker, setTicker] = useState('');

    const handleSearch = () => {
        if (ticker) {
            onSearch(ticker);
            setTicker('');
        }
    }

    const handleEnterKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    }

    return (
        <div>
            <input 
                type="text" 
                placeholder="Search Ticker..."
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                onKeyDown={handleEnterKeyPress}
            />
            <button onClick={handleSearch}>Search</button>
        </div>
    );
}

const MainPanel = () => {
    const [newsSummary, setNewsSummary] = useState({});
    const [ticker, setTicker] = useState('MSFT');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (ticker) {
            fetchNewsSummary();
        }
    }, [ticker]);

    const fetchNewsSummary = async () => {
        try {
            setLoading(true);
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
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (ticker) => {
        setTicker(ticker);
    };

    const mainContent = () => {
        if (loading) {
            return <div>Loading...</div>;
        } 
        return (
            <>
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
            </>
        )
    }

    return (
        <div>
            <img src={tickermateLogo} 
                style={{ width: '150px', height: 'auto', marginBottom: '10px' }} 
            />
            <h1>TickerMate AI</h1>
            <SearchBar
                onSearch={handleSearch}
            />
            {mainContent()}
        </div>
    );
};

export default MainPanel;