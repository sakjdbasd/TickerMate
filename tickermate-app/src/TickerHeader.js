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
            <div>
                <div>{ticker ? `Ticker: ${ticker}` : 'No ticker data available'}</div>
                <div>{name ? `Name: ${name}` : 'No name data available'}</div>
                <div>{price ? `Price: $${price}` : 'No price data available'}</div>
                <div>{change ? `Change: ${change}` : 'No change data available'}</div>
                <div>{sector ? `Sector: ${sector}` : 'No sector data available'}</div>
            </div>
            <div>
                <div>AI Highlight</div>
                <div>{highlight ? highlight : 'No AI highlight data available'}</div>
            </div>
        </div>

    );
};

export default TickerHeader;