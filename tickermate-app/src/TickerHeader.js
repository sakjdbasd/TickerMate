import React from 'react';

const TickerHeader = ({
    ticker,
    name,
    price,
    change,
    sector,
    highlight
}) => {
    return (
        <div>
            <h2>Ticker Header</h2>
            <p>{ticker ? `Ticker: ${ticker}` : 'No ticker data available'}</p>
        </div>
    );
};

export default TickerHeader;