import React, { useEffect, useState, useRef } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8003'

const THEMES = [ 'light', 'dark', 'solar', 'midnight' ]

function App(){
  const [country, setCountry] = useState('England')
  const [countries, setCountries] = useState([])
  const [stops, setStops] = useState([])
  const [lat, setLat] = useState(51.5074)
  const [lon, setLon] = useState(-0.1278)
  const wsRef = useRef(null)
  const [selectedStop, setSelectedStop] = useState(null)
  const [departures, setDepartures] = useState([])
  const [favourites, setFavourites] = useState(() => JSON.parse(localStorage.getItem('itransit:favourites')||'[]'))
  const [theme, setTheme] = useState(() => localStorage.getItem('itransit:theme') || 'light')

  useEffect(()=>{ axios.get(`${API_BASE}/api/countries`).then(r=>setCountries(r.data)) },[])

  useEffect(()=>{
    // websocket connection
    try{
      wsRef.current = new WebSocket((API_BASE + '/ws').replace('http://','ws://'))
      wsRef.current.onmessage = (ev)=>{
        const msg = JSON.parse(ev.data)
        if((msg.type === 'snapshot' || msg.type === 'update') && msg.data.stop_id === selectedStop) {
          setDepartures(msg.data.departures)
        }
      }
    } catch(e){ /* ignore */ }
    return ()=>{ wsRef.current && wsRef.current.close() }
  },[selectedStop])

  useEffect(()=>{
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('itransit:theme', theme)
  },[theme])

  const nearby = async ()=>{
    const res = await axios.get(`${API_BASE}/api/stops/nearby`, { params: { lat, lon, country } })
    setStops(res.data)
  }

  const selectStop = async (s)=>{
    setSelectedStop(s.stop_id)
    const res = await axios.get(`${API_BASE}/api/stops/${s.stop_id}/departures`, { params: { country }})
    setDepartures(res.data)
    wsRef.current && wsRef.current.send(JSON.stringify({ action: 'subscribe', stop_id: s.stop_id }))
  }

  const toggleFav = (s)=>{
    const exists = favourites.find(f=>f.stop_id===s.stop_id)
    let next
    if(exists) next = favourites.filter(f=>f.stop_id!==s.stop_id)
    else next = [...favourites, s]
    setFavourites(next)
    localStorage.setItem('itransit:favourites', JSON.stringify(next))
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="brand">iTransit+</div>
        <div className="controls">
          <select className="theme-select" value={theme} onChange={e=>setTheme(e.target.value)}>
            {THEMES.map(t=> <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={country} onChange={e=>setCountry(e.target.value)} className="country-select">
            {countries.map(c=> <option key={c}>{c}</option>)}
          </select>
          <button className="btn primary" onClick={nearby}>Show Nearby</button>
        </div>
      </header>

      <main className="app-main">
        <aside className="sidebar">
          <h3>Nearby</h3>
          <div className="stops-list">
            {stops.map(s=> (
              <div key={s.stop_id} className="stop-card">
                <div className="stop-info">
                  <div className="stop-name">{s.name}</div>
                  <div className="stop-meta">{s.modes.join(', ')} • {Math.round(s.distance_m)}m</div>
                </div>
                <div className="stop-actions">
                  <button className="btn" onClick={()=>selectStop(s)}>Open</button>
                  <button className="btn ghost" onClick={()=>toggleFav(s)}>{favourites.find(f=>f.stop_id===s.stop_id)?'★':'☆'}</button>
                </div>
              </div>
            ))}
          </div>
        </aside>

        <section className="content">
          <div className="panel">
            <h3>Selected Stop</h3>
            {selectedStop? (
              <>
                <div className="selected-id">{selectedStop}</div>
                <h4>Departures</h4>
                <ul className="departures">
                  {departures.map((d,idx)=> <li key={idx}><span className="line">{d.line}</span> <span className="dest">{d.destination}</span> <span className="mins">{d.expected_minutes}m</span></li>)}
                </ul>
              </>
            ) : <div className="empty">No stop selected — choose one from the list.</div>}
          </div>

          <div className="panel">
            <h3>Favourites</h3>
            {favourites.length? favourites.map(f=> (
              <div key={f.stop_id} className="fav-item">{f.name} <button className="btn small" onClick={()=>selectStop(f)}>Open</button></div>
            )) : <div className="empty">No favourites yet.</div>}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
