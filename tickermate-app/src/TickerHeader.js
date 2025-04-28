import React from 'react';

const TickerHeader = ({data}) => {
    return (
        <div>
            <h2>Ticker Header</h2>
            <p>{data.ticker ? `Ticker: ${data.ticker}` : 'No ticker data available'}</p>
        </div>
    );
};

export default TickerHeader;