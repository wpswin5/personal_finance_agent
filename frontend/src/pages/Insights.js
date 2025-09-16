import React from 'react';
import './Insights.css';

const Insights = () => {
  return (
    <div className="insights-container">
      <div className="insights-header">
        <h1>Financial Insights</h1>
        <p>AI-powered analysis of your financial data</p>
      </div>
      
      <div className="insights-content">
        <div className="coming-soon">
          <div className="coming-soon-icon">📊</div>
          <h2>Coming Soon</h2>
          <p>
            We're working on bringing you powerful AI-driven insights about your spending patterns, 
            budget recommendations, and financial health analysis.
          </p>
          <div className="features-preview">
            <div className="feature-item">
              <span className="feature-icon">💡</span>
              <span>Spending Pattern Analysis</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🎯</span>
              <span>Budget Recommendations</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📈</span>
              <span>Financial Health Score</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">⚠️</span>
              <span>Anomaly Detection</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Insights;