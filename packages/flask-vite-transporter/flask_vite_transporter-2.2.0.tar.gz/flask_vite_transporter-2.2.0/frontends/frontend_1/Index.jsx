import ili from './assets/ili.gif'

export default function Index() {
    function api_flask() {
        fetch('http://127.0.0.1:5001/api', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                console.log(data)
            })
    }

    function api_flask_session() {
        fetch('http://127.0.0.1:5001/api/session', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                console.log(data)
            })
    }

    function api_quart() {
        fetch('http://127.0.0.1:5002/api', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                console.log(data)
            })
    }

    function api_quart_session() {
        fetch('http://127.0.0.1:5002/api/session', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                console.log(data)
            })
    }

    return (
        <div class={'container'}>
            <h1>Flask-Vite-Transporter 🚚</h1>
            <p class={'pt-2'}>Image Asset Example</p>
            <p>👇</p>
            <img width={'100'} src={ili} alt={'ili'}/>
            <small>🥞 Vite, SolidJS, TailwindCSS</small>
            <hr/>
            <small class={'mt-4'}>Demo tests (open browser inspect console)</small>
            <button className={'button'} onClick={api_flask}>API Flask</button>
            <button className={'button'} onClick={api_flask_session}>API Flask Session</button>
            <button className={'button'} onClick={api_quart}>API Quart</button>
            <button className={'button'} onClick={api_quart_session}>API Quart Session</button>
        </div>
    )
};
