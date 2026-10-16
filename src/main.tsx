import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './style.css'

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() { return { failed: true } }
  render() {
    if (this.state.failed) return <div className="loading-page"><h1>Utracono sygnał.</h1><p>Nie udało się wyświetlić gry. Zapis na serwerze pozostaje dostępny.</p><button className="button primary" onClick={() => window.location.reload()}>Wczytaj ponownie</button></div>
    return this.props.children
  }
}
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><ErrorBoundary><App /></ErrorBoundary></React.StrictMode>)
