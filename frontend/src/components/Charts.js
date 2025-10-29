import React from 'react';

// Small, dependency-free SVG chart components. These are intentionally simple
// and accept `data` and `labels` props so they can be swapped out later for
// a library (Recharts / Chart.js) without changing callers.

export const LineChart = ({ data = [], width = 520, height = 160, stroke = '#0ea5ff', fill = 'rgba(14,165,255,0.08)' }) => {
  if (!data || data.length === 0) {
    return <div style={{width, height, display: 'flex', alignItems: 'center', justifyContent: 'center', color:'#9aa4b2'}}>No data</div>;
  }

  const max = Math.max(...data);
  const min = Math.min(...data);
  const len = data.length;
  const padding = 8;
  const scaleX = (i) => padding + (i / (len - 1)) * (width - padding * 2);
  const scaleY = (v) => {
    if (max === min) return height / 2;
    return padding + (1 - (v - min) / (max - min)) * (height - padding * 2);
  };

  const points = data.map((v, i) => `${scaleX(i)},${scaleY(v)}`).join(' ');

  // area path for smooth-ish filled background (using polyline approximation)
  const areaPath = `M ${padding},${height - padding} L ${points.split(' ').map(p => p).join(' L ')} L ${width - padding},${height - padding} Z`;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" role="img" aria-label="line chart">
      <path d={areaPath} fill={fill} stroke="none" />
      <polyline points={points} fill="none" stroke={stroke} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      {data.map((v, i) => (
        <circle key={i} cx={scaleX(i)} cy={scaleY(v)} r={2.2} fill={stroke} />
      ))}
    </svg>
  );
};

export const MiniSparkline = ({ data = [], width = 140, height = 48, stroke = '#06b6d4' }) => {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const len = data.length;
  const padding = 4;
  const scaleX = (i) => padding + (i / (len - 1)) * (width - padding * 2);
  const scaleY = (v) => (max === min ? height / 2 : padding + (1 - (v - min) / (max - min)) * (height - padding * 2));
  const points = data.map((v, i) => `${scaleX(i)},${scaleY(v)}`).join(' ');

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" aria-hidden>
      <polyline points={points} fill="none" stroke={stroke} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" opacity={0.95} />
    </svg>
  );
};

export default LineChart;
