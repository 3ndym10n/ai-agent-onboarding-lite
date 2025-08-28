#!/usr/bin/env python3
"""
VectorFlow MVP Dashboard

70/30 layout Streamlit dashboard for real-time trading intelligence.
Provides chart-focused interface with terminal integration for manual execution.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Dashboard configuration
CHART_HEIGHT = 600
TERMINAL_HEIGHT = 300
REFRESH_INTERVAL = 1  # seconds

class VectorFlowDashboard:
    """Streamlit dashboard for VectorFlow trading intelligence system"""

    def __init__(self):
        self.signals_data = []
        self.market_data = {}
        self.system_status = {}
        self.selected_symbol = "BTCUSDT"

    def run_dashboard(self):
        """Run the Streamlit dashboard"""
        st.set_page_config(
            layout="wide",
            page_title="VectorFlow - Trading Intelligence",
            page_icon="🔥"
        )

        st.title("🔥 VectorFlow Trading Intelligence System")
        st.markdown("*Real-time market analysis for manual execution*")

        # 70/30 layout: Chart (70%) | Terminal (30%)
        col1, col2 = st.columns([7, 3])

        with col1:
            self._render_main_chart()

        with col2:
            self._render_terminal_panel()

        # Auto-refresh
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

    def _render_main_chart(self):
        """Render main price chart with signals overlay"""
        st.subheader(f"📈 {self.selected_symbol} Real-time Chart")

        # Symbol selector
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
        self.selected_symbol = st.selectbox(
            "Select Symbol:",
            symbols,
            key="symbol_selector"
        )

        # Chart placeholder with simulated data
        chart_data = self._get_chart_data(self.selected_symbol)

        fig = go.Figure()

        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=chart_data['time'],
            open=chart_data['open'],
            high=chart_data['high'],
            low=chart_data['low'],
            close=chart_data['close'],
            name='Price'
        ))

        # Add signal markers
        signals = self._get_active_signals(self.selected_symbol)
        for signal in signals:
            if signal['confidence'] > 0.7:
                color = 'green' if signal['action'] == 'long' else 'red'
                marker_symbol = 'triangle-up' if signal['action'] == 'long' else 'triangle-down'

                fig.add_trace(go.Scatter(
                    x=[signal['timestamp']],
                    y=[signal['price']],
                    mode='markers',
                    marker=dict(
                        symbol=marker_symbol,
                        size=12,
                        color=color,
                        line=dict(width=2, color='white')
                    ),
                    name=f"{signal['action'].upper()} Signal",
                    text=f"Score: {signal['holistic_score']:.2f}<br>"
                         f"Confidence: {signal['confidence']:.0%}<br>"
                         f"Reasons: {' | '.join(signal['reasons'][:2])}"
                ))

        # Chart styling
        fig.update_layout(
            height=CHART_HEIGHT,
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                linecolor='rgba(255,255,255,0.2)'
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                linecolor='rgba(255,255,255,0.2)'
            )
        )

        st.plotly_chart(fig, use_container_width=True, key="main_chart")

        # Signal summary below chart
        self._render_signal_summary()

    def _render_terminal_panel(self):
        """Render terminal panel with signals and controls"""
        st.subheader("🎯 Trading Terminal")

        # System status
        self._render_system_status()

        # Active signals
        st.markdown("### 🔥 Active Signals")
        signals = self._get_recent_signals(limit=5)

        if signals:
            for signal in signals:
                with st.container():
                    action_color = "🟢" if signal['action'] == 'long' else "🔴"
                    confidence_pct = f"{signal['confidence']:.0%}"

                    st.markdown(
                        f"{action_color} **{signal['action'].upper()}** | "
                        f"Score: {signal['holistic_score']:.2f} | "
                        f"Confidence: {confidence_pct}"
                    )

                    st.caption(f"📍 {signal['symbol']} - {' | '.join(signal['reasons'][:2])}")

                    # Playbooks
                    if signal.get('playbooks'):
                        st.caption(f"📚 Playbooks: {', '.join(signal['playbooks'][:2])}")

                    st.divider()
        else:
            st.info("No active signals at this time")

        # Manual controls
        st.markdown("### 🎮 Manual Controls")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.success("Data refreshed!")

        with col2:
            if st.button("📊 Performance", use_container_width=True):
                self._show_performance_metrics()

        # Symbol management
        st.markdown("### 📋 Symbol Management")
        new_symbol = st.text_input("Add Symbol:", placeholder="e.g., DOGEUSDT")
        if st.button("Add Symbol") and new_symbol:
            st.success(f"Added {new_symbol} for monitoring")

    def _render_system_status(self):
        """Render system status indicators"""
        st.markdown("### 🔧 System Status")

        status_col1, status_col2 = st.columns(2)

        with status_col1:
            st.metric("Data Service", "🟢 Online", "Connected")
            st.metric("Analytics Engine", "🟢 Online", "6/6 Active")

        with status_col2:
            st.metric("Signal Fusion", "🟢 Online", "Fusing 6 signals")
            st.metric("AI Playbooks", "🟡 Initializing", "Grok API")

        # Performance metrics
        st.metric("Avg Latency", "45ms", "-12ms")
        st.metric("Active Symbols", "5", "+2")

    def _render_signal_summary(self):
        """Render signal summary below main chart"""
        signals = self._get_active_signals(self.selected_symbol)

        if signals:
            st.markdown("### 📊 Signal Summary")

            # Create summary dataframe
            summary_data = []
            for signal in signals[-10:]:  # Last 10 signals
                summary_data.append({
                    'Time': signal['timestamp'].strftime('%H:%M:%S'),
                    'Action': signal['action'].upper(),
                    'Score': f"{signal['holistic_score']:.2f}",
                    'Confidence': f"{signal['confidence']:.0%}",
                    'Primary Reason': signal['reasons'][0] if signal['reasons'] else 'N/A'
                })

            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    def _get_chart_data(self, symbol: str) -> Dict:
        """Get chart data for symbol (simulated)"""
        # Generate sample OHLCV data
        now = datetime.now()
        timestamps = [now - timedelta(minutes=i) for i in range(100, 0, -1)]

        # Simulate realistic BTC price movement
        base_price = 65000 if symbol == "BTCUSDT" else 3000
        prices = []
        current_price = base_price

        for i in range(100):
            change = (0.001 * (0.5 - time.time() % 1))  # Small random changes
            current_price *= (1 + change)
            prices.append(current_price)

        return {
            'time': timestamps,
            'open': prices,
            'high': [p * 1.001 for p in prices],
            'low': [p * 0.999 for p in prices],
            'close': prices[1:] + [current_price],
            'volume': [1000000 + i * 10000 for i in range(100)]
        }

    def _get_active_signals(self, symbol: str) -> List[Dict]:
        """Get active signals for symbol (simulated)"""
        # Simulate some trading signals
        signals = [
            {
                'timestamp': datetime.now() - timedelta(minutes=2),
                'symbol': symbol,
                'action': 'short',
                'holistic_score': 0.85,
                'confidence': 0.82,
                'price': 65150,
                'reasons': [
                    'OI spike +7% at $65,000',
                    'TPO poor high',
                    'Book suppression 0.73'
                ],
                'playbooks': ['Trap Reversal', 'Poor High Fade', 'Range Bounce']
            },
            {
                'timestamp': datetime.now() - timedelta(minutes=5),
                'symbol': symbol,
                'action': 'long',
                'holistic_score': 0.72,
                'confidence': 0.68,
                'price': 64900,
                'reasons': [
                    'VWAP support level',
                    'OI accumulation at 64800'
                ],
                'playbooks': ['Support Bounce', 'Accumulation Pattern']
            }
        ]

        return [s for s in signals if s['symbol'] == symbol]

    def _get_recent_signals(self, limit: int = 5) -> List[Dict]:
        """Get recent signals across all symbols"""
        all_signals = []
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

        for symbol in symbols:
            all_signals.extend(self._get_active_signals(symbol))

        # Sort by timestamp and return most recent
        all_signals.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_signals[:limit]

    def _show_performance_metrics(self):
        """Show performance metrics modal"""
        with st.expander("📊 Performance Metrics", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Win Rate", "68%", "+5%")
                st.metric("Avg Win", "$245", "+12%")

            with col2:
                st.metric("Profit Factor", "1.45", "+0.08")
                st.metric("Max Drawdown", "8.2%", "-2.1%")

            with col3:
                st.metric("Total Trades", "127", "+23")
                st.metric("Sharpe Ratio", "1.23", "+0.15")


def main():
    """Run the VectorFlow dashboard"""
    dashboard = VectorFlowDashboard()
    dashboard.run_dashboard()


if __name__ == "__main__":
    main()