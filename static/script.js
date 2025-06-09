// Ejemplo de validación básica para el formulario de carga
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', function(e) {
        const fileInput = document.getElementById('excel_file');
        if(fileInput && fileInput.files.length === 0) {
            e.preventDefault();
            alert('Por favor, selecciona un archivo Excel.');
        }
    });
});

document.getElementById('toggle-bg-switch').addEventListener('change', function() {
    const modoText = document.getElementById('modo');
    modoText.textContent = this.checked ? 'Modo Claro' : 'Modo Oscuro';
    document.body.classList.toggle('light-mode');
    document.querySelectorAll('form').forEach(form => {
        form.classList.toggle('light-mode');
    });
    modoText.classList.toggle('light-mode');
});
