document.addEventListener('DOMContentLoaded', function () {
  const ctxPresenca = document.getElementById('graficoPresenca').getContext('2d');
  new Chart(ctxPresenca, {
    type: 'line',
    data: {
      labels: window.graficoPresencaLabels,
      datasets: [{
        label: 'Presenças',
        data: window.graficoPresencaDados,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        fill: true,
        tension: 0.4
      }]
    }
  });

  const ctxTurno = document.getElementById('graficoTurno').getContext('2d');
  new Chart(ctxTurno, {
    type: 'doughnut',
    data: {
      labels: window.graficoTurnoLabels,
      datasets: [{
        data: window.graficoTurnoDados,
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#a855f7', '#14b8a6'],
        borderColor: '#f9fafb',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          callbacks: {
            label: function (tooltipItem) {
              return tooltipItem.raw + "%";
            }
          }
        }
      }
    }
  });
});