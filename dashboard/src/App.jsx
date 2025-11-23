import React, { useState, useEffect, useRef } from 'react';
import { Activity, TrendingUp, DollarSign, AlertTriangle, Power, RefreshCw, Shield, Zap } from 'lucide-react';
import axios from 'axios';
import { createChart } from 'lightweight-charts';
import ChatWidget from './ChatWidget';

// Get API URL from config or default
const API_URL = window.APEX_API_URL || 'http://localhost:8000';

function App() {
    const [status, setStatus] = useState(null);
    const [config, setConfig] = useState(null);
    const [recentTrades, setRecentTrades] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const candleSeriesRef = useRef(null);

    // Fetch data
    const fetchData = async () => {
        try {
            const [statusRes, configRes, tradesRes] = await Promise.all([
                axios.get(`${API_URL}/status`),
                axios.get(`${API_URL}/config`),
                axios.get(`${API_URL}/trades/recent`)
            ]);

            setStatus(statusRes.data);
            setConfig(configRes.data);
            setRecentTrades(tradesRes.data.trades);
            setError(null);
        } catch (err) {
            console.error("Error fetching data:", err);
            setError("Connection lost. Retrying...");
        } finally {
            setLoading(false);
        }
    };

    // Initial load and polling
    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 2000); // Poll every 2s
        return () => clearInterval(interval);
    }, []);

    // Chart setup (placeholder for now)
    useEffect(() => {
        if (chartContainerRef.current && !chartRef.current) {
            const chart = createChart(chartContainerRef.current, {
                layout: {
                    background: { type: 'Solid', color: 'transparent' },
                    textColor: '#94a3b8', // Slate 400
                },
                grid: {
                    vertLines: { color: '#334155' }, // Slate 700
                    horzLines: { color: '#334155' },
                },
                width: chartContainerRef.current.clientWidth,
                height: 300,
            });

            const candlestickSeries = chart.addCandlestickSeries({
                upColor: '#2dd4bf',   // Zen Teal
                downColor: '#fb7185', // Zen Rose
                borderVisible: false,
                wickUpColor: '#2dd4bf',
                wickDownColor: '#fb7185',
            });

            // Dummy data
            candlestickSeries.setData([
                { time: '2018-12-22', open: 75.16, high: 82.84, low: 36.16, close: 45.72 },
                { time: '2018-12-23', open: 45.12, high: 53.90, low: 45.12, close: 48.09 },
                { time: '2018-12-24', open: 60.71, high: 60.71, low: 53.39, close: 59.29 },
                { time: '2018-12-25', open: 68.26, high: 68.26, low: 59.04, close: 60.50 },
                { time: '2018-12-26', open: 67.71, high: 105.85, low: 66.67, close: 91.04 },
                { time: '2018-12-27', open: 91.04, high: 121.40, low: 82.70, close: 111.40 },
                { time: '2018-12-28', open: 111.51, high: 142.83, low: 103.34, close: 131.25 },
                { time: '2018-12-29', open: 131.33, high: 151.17, low: 77.68, close: 96.43 },
                { time: '2018-12-30', open: 106.33, high: 110.20, low: 90.39, close: 98.10 },
                { time: '2018-12-31', open: 109.87, high: 114.69, low: 85.66, close: 111.26 },
            ]);

            chartRef.current = chart;
            candleSeriesRef.current = candlestickSeries;

            const handleResize = () => {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            };

            window.addEventListener('resize', handleResize);
            return () => window.removeEventListener('resize', handleResize);
        }
    }, []);

    const toggleBot = async () => {
        if (!status) return;
        const endpoint = status.mode === 'LIVE' ? '/control/stop' : '/control/start'; // Logic might need adjustment based on actual running state
        // Currently API returns mode based on config, not running state. 
        // We need a running state in status endpoint.
        // Assuming status.running exists or we add it.
        try {
            // For now just log
            console.log("Toggle bot requested");
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="min-h-screen p-6">
            {/* Header */}
            <header className="flex justify-between items-center mb-8">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-zen-teal/10 border border-zen-teal/20 animate-pulse-slow">
                        <Activity className="w-8 h-8 text-zen-teal" />
                    </div>
                    <h1 className="text-3xl font-bold tracking-tighter text-white">
                        APEX <span className="text-zen-lavender">ZEN</span>
                    </h1>
                </div>
                <div className="flex items-center gap-4">
                    <div className={`px-3 py-1 rounded-full border ${status?.mode === 'LIVE' ? 'border-zen-teal text-zen-teal bg-zen-teal/10' : 'border-yellow-500 text-yellow-500 bg-yellow-500/10'} text-sm font-mono`}>
                        {status?.mode || 'CONNECTING...'}
                    </div>
                    <div className="text-xs text-slate-500 font-mono">
                        v2.0.0
                    </div>
                </div>
            </header>

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Left Column: Stats & Control */}
                <div className="space-y-6">
                    {/* Status Card */}
                    <div className="card relative overflow-hidden group hover:border-zen-teal/30 transition-colors">
                        <div className="absolute inset-0 bg-gradient-to-br from-zen-teal/5 to-transparent opacity-50 group-hover:opacity-100 transition-opacity" />
                        <div className="relative z-10">
                            <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-200">
                                <Zap className="w-5 h-5 text-zen-teal" /> SYSTEM STATUS
                            </h2>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-400">Engine State</span>
                                    <span className="text-white font-mono">RUNNING</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-400">Uptime</span>
                                    <span className="text-white font-mono">04:20:69</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-400">API Latency</span>
                                    <span className="text-zen-teal font-mono">12ms</span>
                                </div>
                            </div>
                            <button onClick={toggleBot} className="w-full mt-6 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 py-2 rounded-lg flex items-center justify-center gap-2 transition-colors">
                                <Power className="w-4 h-4" /> EMERGENCY STOP
                            </button>
                        </div>
                    </div>

                    {/* P&L Card */}
                    <div className="card hover:border-zen-blue/30 transition-colors">
                        <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-200">
                            <DollarSign className="w-5 h-5 text-zen-blue" /> PERFORMANCE
                        </h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-white/5 p-3 rounded-lg border border-white/5">
                                <div className="text-xs text-slate-400 mb-1">DAILY P&L</div>
                                <div className={`text-xl font-mono ${status?.daily?.total_profit_percent >= 0 ? 'text-zen-teal' : 'text-zen-rose'}`}>
                                    {status?.daily?.total_profit_percent > 0 ? '+' : ''}{status?.daily?.total_profit_percent?.toFixed(2)}%
                                </div>
                            </div>
                            <div className="bg-white/5 p-3 rounded-lg border border-white/5">
                                <div className="text-xs text-slate-400 mb-1">WIN RATE</div>
                                <div className="text-xl font-mono text-zen-lavender">
                                    {status?.daily?.win_rate?.toFixed(1)}%
                                </div>
                            </div>
                            <div className="bg-white/5 p-3 rounded-lg border border-white/5 col-span-2">
                                <div className="text-xs text-slate-400 mb-1">TOTAL BALANCE</div>
                                <div className="text-2xl font-mono text-white">
                                    $1,042.50
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Middle Column: Chart & Active Trade */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Chart */}
                    <div className="card h-[400px] flex flex-col hover:border-zen-lavender/30 transition-colors">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-bold flex items-center gap-2 text-slate-200">
                                <TrendingUp className="w-5 h-5 text-zen-lavender" /> MARKET OVERVIEW
                            </h2>
                            <div className="flex gap-2">
                                <span className="px-2 py-0.5 rounded bg-zen-lavender/10 text-zen-lavender text-xs border border-zen-lavender/20">BTC/USDT</span>
                                <span className="px-2 py-0.5 rounded bg-white/5 text-slate-400 text-xs border border-white/10">1H</span>
                            </div>
                        </div>
                        <div ref={chartContainerRef} className="flex-1 w-full" />
                    </div>

                    {/* Active Position */}
                    {status?.has_open_position ? (
                        <div className="card border-zen-teal/30 bg-zen-teal/5">
                            <h2 className="text-lg font-bold mb-4 text-zen-teal flex items-center gap-2">
                                <Activity className="w-5 h-5" /> ACTIVE POSITION
                            </h2>
                            <div className="grid grid-cols-4 gap-4">
                                <div>
                                    <div className="text-xs text-slate-400">SYMBOL</div>
                                    <div className="text-xl font-bold">{status.open_position.symbol}</div>
                                </div>
                                <div>
                                    <div className="text-xs text-slate-400">ENTRY</div>
                                    <div className="text-xl font-mono">${status.open_position.entry_price}</div>
                                </div>
                                <div>
                                    <div className="text-xs text-slate-400">CURRENT</div>
                                    <div className="text-xl font-mono text-white">${status.open_position.current_price || '---'}</div>
                                </div>
                                <div>
                                    <div className="text-xs text-slate-400">P&L</div>
                                    <div className="text-xl font-mono text-zen-teal">+1.2%</div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="card border-dashed border-slate-700 flex items-center justify-center h-32 text-slate-500">
                            NO ACTIVE POSITIONS
                        </div>
                    )}
                </div>
            </div>

            {/* Recent Trades */}
            <div className="mt-6 card">
                <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-200">
                    <RefreshCw className="w-5 h-5 text-slate-400" /> RECENT ACTIVITY
                </h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead>
                            <tr className="text-slate-500 border-b border-white/10">
                                <th className="pb-2">TIME</th>
                                <th className="pb-2">SYMBOL</th>
                                <th className="pb-2">TYPE</th>
                                <th className="pb-2">PRICE</th>
                                <th className="pb-2">P&L</th>
                                <th className="pb-2">STATUS</th>
                            </tr>
                        </thead>
                        <tbody className="font-mono">
                            {recentTrades.map((trade, i) => (
                                <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                    <td className="py-3 text-slate-400">{trade.entry_time}</td>
                                    <td className="py-3 font-bold">{trade.symbol}</td>
                                    <td className="py-3 text-zen-blue">LONG</td>
                                    <td className="py-3">${trade.entry_price}</td>
                                    <td className={`py-3 ${trade.profit_percent >= 0 ? 'text-zen-teal' : 'text-zen-rose'}`}>
                                        {trade.profit_percent ? `${trade.profit_percent}%` : '-'}
                                    </td>
                                    <td className="py-3">
                                        <span className={`px-2 py-0.5 rounded text-xs ${trade.status === 'CLOSED' ? 'bg-slate-700 text-slate-300' : 'bg-zen-teal/20 text-zen-teal'}`}>
                                            {trade.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                            {recentTrades.length === 0 && (
                                <tr>
                                    <td colSpan="6" className="py-4 text-center text-slate-500">No recent trades</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
            <ChatWidget />
        </div >
    );
}

export default App;
