document.addEventListener('DOMContentLoaded', function () {
    // Validación del formulario para archivo Excel
    const form = document.querySelector('form');
    form.addEventListener('submit', function (e) {
        const fileInput = document.getElementById('excel_file');
        if (fileInput && fileInput.files.length === 0) {
            e.preventDefault();
            alert('Por favor, selecciona un archivo Excel.');
        }
    });

    // Cambiar tema (oscuro / claro)
    const toggleSwitch = document.getElementById('toggle-bg-switch');
    toggleSwitch.addEventListener('change', function () {
        const modoText = document.getElementById('modo');
        modoText.textContent = this.checked ? 'Modo Claro' : 'Modo Oscuro';
        document.body.classList.toggle('light-mode');
        document.querySelectorAll('form').forEach(form => {
            form.classList.toggle('light-mode');
        });
        modoText.classList.toggle('light-mode');
    });

    // Cerrar mensaje al hacer clic en el botón de cerrar
     document.querySelectorAll('.custom-close').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const container = this.closest('.container.mt-3');
            if (container) {
                container.remove();
            }
        });
    });
});
