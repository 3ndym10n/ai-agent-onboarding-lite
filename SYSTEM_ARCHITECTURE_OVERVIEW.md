# 🏗️ VectorFlow System Architecture Overview

**High-Level System Design and Component Relationships**

## 🎯 **ARCHITECTURE PRINCIPLES**

### **Three-Tier Microservices Design**
1. **Data Layer** - Multi-exchange real-time data collection
2. **Analytics Layer** - Specialized analysis modules
3. **Coordination Layer** - Signal fusion and AI integration

### **Event-Driven Architecture**
- **Asynchronous processing** for high performance
- **Event streaming** between components
- **Loose coupling** for scalability
- **Fault tolerance** with graceful degradation

## 🏗️ **SYSTEM COMPONENTS**

### **Data Layer**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Binance API   │    │    Bybit API    │    │    MEXC API     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Unified Data    │
                    │ Service V2      │
                    │ (Smart Polling) │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ PostgreSQL DB   │
                    │ + Redis Cache   │
                    └─────────────────┘
```

### **Analytics Layer**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ TPO Market      │    │ Regime          │    │ Trap/Spoof      │
│ Profile         │    │ Detector        │    │ Detector        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ OI 5s           │
                    │ Aggregator      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Supply/Demand   │
                    │ Detector        │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Velocity        │
                    │ Analyzer        │
                    └─────────────────┘
```

### **Coordination Layer**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Signal Fusion   │    │ AI Playbook     │    │ Signal Arbiter  │
│ Engine          │    │ Generator       │    │ (Priority)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Streamlit       │
                    │ Dashboard       │
                    └─────────────────┘
```

## 🔄 **DATA FLOW**

### **Real-Time Processing Pipeline**
```
Exchange APIs → Unified Data Service → Analytics Modules → Signal Fusion → AI Playbooks → Dashboard
     ↓                ↓                    ↓                ↓              ↓            ↓
WebSocket/REST → Smart Polling → TPO/Regime/Trap → Holistic Score → Grok AI → Real-time Charts
```

### **Performance Requirements**
- **<100ms** end-to-end latency
- **5-second** OI aggregation windows
- **50+ coins** simultaneous processing
- **80-90%** accuracy on regime detection

## 🛠️ **TECHNOLOGY STACK**

### **Backend**
- **Python 3.11+** with async/await
- **PostgreSQL** for data persistence
- **Redis** for caching and pub/sub
- **asyncio** for concurrent processing
- **NumPy/Pandas** for data analysis

### **Frontend**
- **Streamlit** for MVP dashboard
- **Plotly.js** for real-time charts
- **WebSocket** for live updates

### **External Services**
- **Grok AI** for playbook suggestions
- **VectorBT** for backtesting
- **Multi-exchange APIs** (Binance, Bybit, MEXC, Gate, HTX)

## 🔧 **KEY ALGORITHMS**

### **Smart Polling System**
- **Adaptive intervals** based on market activity
- **Multi-factor detection** for significant events
- **Rate limiting** to respect API limits
- **WebSocket fallback** for real-time data

### **Signal Fusion Engine**
- **Weighted combination** of 6+ analytics
- **Confidence scoring** for each signal
- **Conflict resolution** between signals
- **Priority processing** for high-impact events

### **OI 5s Aggregation**
- **Sliding window** processing
- **Whole number detection** at psychological levels
- **Spike classification** for big player activity
- **Cross-exchange correlation** analysis

## 🚨 **CRITICAL CONSTRAINTS**

### **Performance**
- **<100ms** signal generation latency
- **80-90%** accuracy on regime/zone detection
- **>60%** hit rate on AI playbook suggestions
- **50+ coins** simultaneous processing

### **Reliability**
- **Graceful degradation** when services fail
- **Data persistence** for historical analysis
- **Error handling** for API failures
- **Monitoring** for system health

### **Scalability**
- **Horizontal scaling** of analytics modules
- **Database optimization** for high throughput
- **Caching strategy** for frequently accessed data
- **Load balancing** for multiple instances

## 🎯 **DEPLOYMENT ARCHITECTURE**

### **Render Services**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ vectorflow-api  │    │ vectorflow-     │    │ vectorflow-     │
│ (Main API)      │    │ enhanced-       │    │ realtime-       │
└─────────────────┘    │ collector       │    │ tick-collector  │
                       └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ vectorflow-db   │
                    │ (PostgreSQL)    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ vectorflow-     │
                    │ redis           │
                    └─────────────────┘
```

## 🔄 **INTEGRATION PATTERNS**

### **Event-Driven Communication**
- **Async message queues** between components
- **WebSocket connections** for real-time updates
- **REST APIs** for configuration and monitoring
- **Database triggers** for data consistency

### **Error Handling**
- **Circuit breakers** for external API calls
- **Retry logic** with exponential backoff
- **Fallback mechanisms** for critical services
- **Comprehensive logging** for debugging

---

**🎯 This architecture ensures high performance, reliability, and scalability**
**🤖 Designed for seamless AI model handovers and continuous development**
