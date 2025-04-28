import React from 'react';

const NewsSummary = ({news}) => {
    if (!Array.isArray(news) || news.length === 0) {
        // return <div>No news summary available</div>;
        news = [
            {
            "time": "2 hrs ago",
            "source": "Reuters",
            "sentiment": "Bullish",
            "summary": "Apple increased R&D spending by 12%, signaling strong innovation push."
            },
            {
            "time": "5 hrs ago",
            "source": "Bloomberg",
            "sentiment": "Neutral",
            "summary": "Supply chain remains stable amid broader tech sector uncertainty."
            },
            {
            "time": "1 day ago",
            "source": "CNBC",
            "sentiment": "Bearish",
            "summary": "Q1 iPad sales fell short of expectations by 8%."
            }
        ]
    }

    return (
        <div>
            <h2>News Summary</h2>
            <div>
                {news.map((item, index) => (
                    <SummaryCard
                        key={index}
                        time={item["time"]}
                        source={item["source"]}
                        sentiment={item["sentiment"]}
                        summary={item["summary"]}
                    />
                ))}
            </div>
        </div>
    );
};

const SummaryCard = ({
    time,
    source,
    sentiment,
    summary,
    }) => {
    return (
        <div>
            <p>{time ? `Time: ${time}` : 'No time data available'}</p>
            <p>{source ? `Source: ${source}` : 'No source data available'}</p>
            <p>{sentiment ? `Sentiment: ${sentiment}` : 'No sentiment data available'}</p>
            <p>{summary ? `Summary: ${summary}` : 'No summary data available'}</p>
        </div>
    );

}

export default NewsSummary;