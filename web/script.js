// script.js
let ultimasSenales = [];
let intervalo = null;
const CONTRASENA = "trading2026"; // Cambia esto por tu contraseña

// Autenticación
function checkPassword() {
    const pwd = document.getElementById('passwordInput').value;
    if (pwd === CONTRASENA) {
        document.getElementById('loginContainer').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        showSection('live');
        iniciarConexionConCorreo();
    } else {
        document.getElementById('loginError').textContent = 'Contraseña incorrecta';
    }
}

function showSection(section) {
    document.getElementById('liveSection').style.display = section === 'live' ? 'block' : 'none';
    document.getElementById('backtestSection').style.display = section === 'backtest' ? 'block' : 'none';
    document.getElementById('configSection').style.display = section === 'config' ? 'block' : 'none';
}

function logout() {
    document.getElementById('dashboard').style.display = 'none';
    document.getElementById('loginContainer').style.display = 'block';
    document.getElementById('passwordInput').value = '';
    if (intervalo) clearInterval(intervalo);
}

// Conexión con el correo local (API)
function iniciarConexionConCorreo() {
    intervalo = setInterval(async () => {
        try {
            const response = await fetch('http://localhost:8000/ultimas-senales');
            if (response.ok) {
                const senales = await response.json();
                actualizarSenales(senales);
            }
        } catch (e) {
            console.log("Esperando al correo local...");
        }
    }, 2000);
}

function actualizarSenales(senales) {
    const container = document.getElementById('signals');
    if (senales.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:#aaa;">Esperando señales...</p>';
        return;
    }
    // Mostrar las señales más recientes primero
    senales.reverse().forEach(s => {
        const senalDiv = document.createElement('div');
        senalDiv.className = `signal ${s.apalancamiento?.tipo?.toLowerCase() || 'info'}`;
        let html = `<strong>${s.activo}</strong><br>`;
        if (s.apalancamiento) {
            html += `📈 Apalancamiento: ${s.apalancamiento.tipo} a $${s.apalancamiento.precio}<br>`;
            html += `TP1: $${s.apalancamiento.tp1} | TP2: $${s.apalancamiento.tp2} (confianza ${s.apalancamiento.confianza})<br>`;
        }
        if (s.binarias) {
            html += `⏱ Binarias: ${s.binarias.tipo} a $${s.binarias.precio} (Duración: ${s.binarias.duracion})<br>`;
        }
        html += `<small>${new Date().toLocaleTimeString()}</small>`;
        senalDiv.innerHTML = html;
        container.prepend(senalDiv);
    });
    // Limitar a 20 señales visibles
    while (container.children.length > 20) {
        container.removeChild(container.lastChild);
    }
}

// Calculadora de lotes
function calcularLotes() {
    const capital = parseFloat(document.getElementById('capital').value) || 0;
    const riesgoPorc = parseFloat(document.getElementById('riesgo').value) || 0;
    const riesgoUSD = capital * (riesgoPorc / 100);
    // Ejemplo: para Oro, asumiendo valor por pip = $0.1 por lote estándar
    const pipValue = 0.1; // esto debería ajustarse por activo
    const stopLossPips = 20; // ejemplo
    const lotes = (riesgoUSD / (stopLossPips * pipValue)).toFixed(2);
    document.getElementById('loteRecomendado').innerText = `Lote recomendado: ${lotes}`;
}

// Backtesting simulado
function ejecutarBacktest() {
    const estrategia = document.getElementById('estrategiaBacktest').value;
    const activo = document.getElementById('activoBacktest').value;
    const dias = parseInt(document.getElementById('diasBacktest').value);
    // Aquí deberías llamar a tu script de Python, pero por ahora simulamos
    document.getElementById('resultadosBacktest').innerHTML = `
        <h3>Resultados (simulados)</h3>
        <p>Estrategia: ${estrategia}</p>
        <p>Activo: ${activo}</p>
        <p>Días: ${dias}</p>
        <p>Operaciones totales: 45</p>
        <p>Win Rate: 68%</p>
        <p>Ganancia neta: $1250</p>
    `;
}

// Guardar configuración de Telegram (en localStorage)
function guardarConfigTelegram() {
    const token = document.getElementById('telegramToken').value;
    const chatId = document.getElementById('telegramChatId').value;
    localStorage.setItem('telegramToken', token);
    localStorage.setItem('telegramChatId', chatId);
    alert('Configuración guardada');
}