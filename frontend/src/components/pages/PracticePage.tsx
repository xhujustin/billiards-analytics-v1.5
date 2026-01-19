import { useState } from 'react';
import './PracticePage.css';
import { PageType } from '../Sidebar';

type PracticeMode = 'menu' | 'single' | 'pattern';
type PracticePattern = 'straight' | 'cut' | 'bank' | 'combo';

interface PracticeStats {
    attempts: number;
    successes: number;
    success_rate: number;
}

interface PracticePageProps {
    onNavigate: (page: PageType) => void;
}

export default function PracticePage({ onNavigate }: PracticePageProps) {
    const [mode, setMode] = useState<PracticeMode>('menu');
    const [pattern, setPattern] = useState<PracticePattern>('straight');
    const [isActive, setIsActive] = useState(false);
    const [stats, setStats] = useState<PracticeStats>({ attempts: 0, successes: 0, success_rate: 0 });

    // 開始練習
    const handleStartPractice = async (practiceMode: 'single' | 'pattern') => {
        try {
            const response = await fetch('/api/practice/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: practiceMode,
                    pattern: practiceMode === 'pattern' ? pattern : null
                })
            });

            if (response.ok) {
                setMode(practiceMode);
                setIsActive(true);
                setStats({ attempts: 0, successes: 0, success_rate: 0 });
            }
        } catch (error) {
            console.error('Failed to start practice:', error);
        }
    };

    // 記錄練習結果
    const handleRecordAttempt = async (success: boolean) => {
        try {
            const response = await fetch('/api/practice/record', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ success })
            });

            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (error) {
            console.error('Failed to record attempt:', error);
        }
    };

    // 結束練習
    const handleEndPractice = async () => {
        try {
            await fetch('/api/practice/end', { method: 'POST' });
            setIsActive(false);
            setMode('menu');
        } catch (error) {
            console.error('Failed to end practice:', error);
        }
    };

    // 返回選單
    const handleBackToMenu = () => {
        handleEndPractice();
    };

    // 渲染選單
    if (mode === 'menu') {
        return (
            <div className="practice-page">
                <div className="practice-header">
                    <h1>練習模式</h1>
                    <p>選擇練習類型，提升撞球技巧</p>
                </div>

                <div className="practice-menu">
                    <div className="practice-card" onClick={() => handleStartPractice('single')}>
                        <div className="card-icon">🎱</div>
                        <h2>單球練習</h2>
                        <p className="card-description">專注於基本技巧,適合新手建立基礎</p>
                        <div className="card-badge">推薦初學者</div>
                    </div>

                    <div className="practice-card" onClick={() => handleStartPractice('pattern')}>
                        <div className="card-icon">🎲</div>
                        <h2>球型練習</h2>
                        <p className="card-description">訓練特定球型,提升進階技術</p>
                        <div className="card-badge">適合進階</div>
                    </div>
                </div>

                <div className="practice-footer">
                    <button className="btn-secondary" onClick={() => onNavigate('stream')}>
                        ← 返回即時影像
                    </button>
                </div>
            </div>
        );
    }

    // 渲染練習畫面
    return (
        <div className="practice-page">
            <div className="practice-header-active">
                <div className="header-left">
                    <h1>🎯 {mode === 'single' ? '單球練習' : '球型練習'}</h1>
                    {mode === 'pattern' && (
                        <span className="pattern-badge">
                            {pattern === 'straight' ? '直線球' :
                                pattern === 'cut' ? '切球' :
                                    pattern === 'bank' ? '反彈球' : '組合球'}
                        </span>
                    )}
                </div>
                <div className="header-right">
                    <div className={`status-badge ${isActive ? 'active' : 'paused'}`}>
                        {isActive ? '● 練習中' : '⏸ 已暫停'}
                    </div>
                </div>
            </div>

            <div className="practice-content">
                {/* 統計面板 */}
                <div className="stats-panel">
                    <h3>📊 練習統計</h3>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-icon">🎯</div>
                            <div className="stat-info">
                                <span className="stat-label">嘗試次數</span>
                                <span className="stat-value">{stats.attempts}</span>
                            </div>
                        </div>
                        <div className="stat-card success">
                            <div className="stat-icon">✅</div>
                            <div className="stat-info">
                                <span className="stat-label">成功次數</span>
                                <span className="stat-value">{stats.successes}</span>
                            </div>
                        </div>
                        <div className="stat-card rate">
                            <div className="stat-icon">📈</div>
                            <div className="stat-info">
                                <span className="stat-label">成功率</span>
                                <span className="stat-value">{Math.round(stats.success_rate * 100)}%</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 實時影像區域 */}
                <div className="video-container">
                    <img
                        src="/burnin/camera1.mjpg?quality=med"
                        alt="Practice Stream"
                        className="practice-stream"
                    />
                    {!isActive && (
                        <div className="video-overlay">
                            <div className="overlay-message">
                                ⏸ 練習已暫停
                                <button className="btn-resume" onClick={() => setIsActive(true)}>
                                    繼續練習
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* 球型選擇 (僅球型練習) */}
                {mode === 'pattern' && (
                    <div className="pattern-selector">
                        <h3>🎲 球型選擇</h3>
                        <div className="pattern-buttons">
                            <button
                                className={`pattern-btn ${pattern === 'straight' ? 'active' : ''}`}
                                onClick={() => setPattern('straight')}
                                disabled={isActive}
                            >
                                <span className="pattern-icon">━</span>
                                <span>直線球</span>
                            </button>
                            <button
                                className={`pattern-btn ${pattern === 'cut' ? 'active' : ''}`}
                                onClick={() => setPattern('cut')}
                                disabled={isActive}
                            >
                                <span className="pattern-icon">╱</span>
                                <span>切球</span>
                            </button>
                            <button
                                className={`pattern-btn ${pattern === 'bank' ? 'active' : ''}`}
                                onClick={() => setPattern('bank')}
                                disabled={isActive}
                            >
                                <span className="pattern-icon">⤵</span>
                                <span>反彈球</span>
                            </button>
                            <button
                                className={`pattern-btn ${pattern === 'combo' ? 'active' : ''}`}
                                onClick={() => setPattern('combo')}
                                disabled
                            >
                                <span className="pattern-icon">◎</span>
                                <span>組合球(預留)</span>
                            </button>
                        </div>
                        {isActive && (
                            <p className="pattern-hint">💡 暫停練習後可切換球型</p>
                        )}
                    </div>
                )}

                {/* 操作面板 */}
                <div className="action-panel">
                    <h3>⚡ 記錄結果</h3>
                    <div className="action-buttons">
                        <button
                            className="btn-success"
                            onClick={() => handleRecordAttempt(true)}
                            disabled={!isActive}
                        >
                            <span className="btn-icon">✅</span>
                            <span>成功</span>
                            <span className="btn-hint">Space</span>
                        </button>
                        <button
                            className="btn-danger"
                            onClick={() => handleRecordAttempt(false)}
                            disabled={!isActive}
                        >
                            <span className="btn-icon">❌</span>
                            <span>失敗</span>
                            <span className="btn-hint">X</span>
                        </button>
                    </div>
                    <div className="action-controls">
                        <button
                            className="btn-control"
                            onClick={() => setIsActive(!isActive)}
                        >
                            {isActive ? '⏸ 暫停' : '▶ 繼續'}
                        </button>
                        <button
                            className="btn-control end"
                            onClick={handleBackToMenu}
                        >
                            🏁 結束練習
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
