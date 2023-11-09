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
        if (fileItem.classList.contains('folder-item')) {
        var downloadURL = fileItem.getAttribute('data-additional-url'); // URL для скачивания папки
        }
        else {
        var downloadURL = fileItem.querySelector('a').getAttribute('href'); // URL для скачивания файла
        }
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


$(document).ready(function () {
    $(".file-item").on("dragstart", function (event) {
        var fileID = $(this).data("file-id");
        event.originalEvent.dataTransfer.setData("file-id", fileID);
    });

    $(".folder-item, .back-link").on("dragover", function (event) {
        event.preventDefault();
        $(this).addClass("drag-over");
    });

    $(".folder-item, .back-link").on("dragleave", function () {
        $(this).removeClass("drag-over");
    });

    $(".folder-item, .back-link").on("drop", function (event) {
        event.preventDefault();
        $(this).removeClass("drag-over");

        var folderID = $(this).data("file-id");
        var fileID = event.originalEvent.dataTransfer.getData("file-id");

        // Отправьте данные на сервер для перемещения файла в папку или в `file_list`
        $.ajax({
            url: "/cloud/move-file/" + folderID + "/" + fileID + "/",
            method: "GET",
            success: function (data) {
                // Обновите список файлов и папок на странице, чтобы отразить изменения
                location.reload(); // Простой способ обновить страницу
            }
        });
    });
});