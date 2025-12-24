let refreshInterval;

function populateIPs() {
    fetch('/api/ips')
        .then(res => res.json())
        .then(ips => {
            const select = document.getElementById('ip');
            select.innerHTML = '';

            if (!ips || ips.length === 0) {
                // Fallback to a placeholder and keep the old static addresses if needed
                select.innerHTML = `
                    <option value="199.36.158.10">Sensor 1 (199.36.158.10)</option>
                    <option value="199.36.158.11">Sensor 2 (199.36.158.11)</option>
                    <option value="192.168.1.100">Sensor 3 (192.168.1.100)</option>`;
                return;
            }

            ips.forEach((ip, idx) => {
                const opt = document.createElement('option');
                opt.value = ip;
                opt.textContent = `Sensor ${idx + 1} (${ip})`;
                select.appendChild(opt);
            });

            // load initial data for first IP
            loadData();
        })
        .catch(err => {
            console.error('Failed to load IP list:', err);
        });
}

function loadData() {
    const ip = document.getElementById("ip").value;

    if (!ip) {
        const table = document.getElementById("tableBody");
        table.innerHTML = '<tr><td colspan="9" style="text-align:center; color:#999;">Select a sensor</td></tr>';
        return;
    }

    fetch(`/api/data?ip=${encodeURIComponent(ip)}`)
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("tableBody");
            table.innerHTML = "";

            if (!data || data.length === 0) {
                table.innerHTML = '<tr><td colspan="9" style="text-align:center; color:#999;">No data received yet</td></tr>';
                return;
            }

            // Show latest readings first
            data.reverse().forEach(row => {
                const alarmClass = (row.alarmLevel || row.alarmFire || row.alarmFall || row.alarmBattery) ? 'alarm' : '';
                table.innerHTML += `
                <tr class="${alarmClass}">
                    <td>${row.timestamp || '-'}</td>
                    <td>${row.level || '-'}</td>
                    <td>${row.temperature || '-'}</td>
                    <td>${row.angle || '-'}</td>
                    <td>${row.alarmLevel ? '⚠️ Level' : '-'}</td>
                    <td>${row.alarmFire ? '🔥 Fire' : '-'}</td>
                    <td>${row.alarmFall ? '📉 Fall' : '-'}</td>
                    <td>${row.alarmBattery ? '🔋 Low' : '-'}</td>
                    <td>${row.frameCounter || '-'}</td>
                </tr>`;
            });
        })
        .catch(err => {
            console.error('Error loading data:', err);
            const table = document.getElementById("tableBody");
            table.innerHTML = '<tr><td colspan="9" style="text-align:center; color:red;">Failed to load data</td></tr>';
        });
}

// Load IP list on page load
populateIPs();

// Auto-refresh every 5 seconds
document.getElementById("ip").addEventListener("change", () => {
    clearInterval(refreshInterval);
    loadData();
    refreshInterval = setInterval(loadData, 5000);
});

// Start auto-refresh
refreshInterval = setInterval(loadData, 5000);
