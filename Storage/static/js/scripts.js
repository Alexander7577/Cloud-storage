// Переменная для отслеживания текущего открытого контекстного меню
var currentContextMenu = null;

// Обработчик события ПКМ для файлов
document.querySelectorAll('.file-item').forEach(function(fileItem) {
    fileItem.addEventListener('contextmenu', function(e) {
        e.preventDefault();

        // Закрыть текущее контекстное меню, если оно открыто
        if (currentContextMenu) {
            currentContextMenu.remove();
        }

        // Определите ID файла из атрибута data-file-id
        var fileId = fileItem.getAttribute('data-file-id');

        // Создаём контекстное меню с опциями удаления, переименования и скачивания
        var contextMenu = document.createElement('ul');
        contextMenu.classList.add('context-menu');
        var deleteURL = fileItem.getAttribute('data-url');
        var downloadURL = fileItem.querySelector('a').getAttribute('href'); // URL для скачивания файла
        contextMenu.innerHTML = `
            <li><a href="${downloadURL}" download>Скачать</a></li>
            <li><a href="${deleteURL}">Удалить</a></li>
        `;

        // Позиционируйте контекстное меню и добавьте его к DOM
        contextMenu.style.left = e.pageX + 'px';
        contextMenu.style.top = e.pageY + 'px';
        document.body.appendChild(contextMenu);

        // Запомните текущее контекстное меню
        currentContextMenu = contextMenu;

        // Закройте контекстное меню при щелчке вне меню
        document.addEventListener('click', function() {
            if (currentContextMenu) {
                currentContextMenu.remove();
                currentContextMenu = null;
            }
        });
    });
});
