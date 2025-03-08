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
