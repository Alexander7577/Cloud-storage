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
    // Обработка события "dragstart" для файлов и папок
    $(".file-item, .folder-item").on("dragstart", function (event) {
        var itemID = $(this).data("file-id");
        var isFolder = $(this).hasClass("folder-item");
        event.originalEvent.dataTransfer.setData("item-id", itemID);
        event.originalEvent.dataTransfer.setData("is-folder", isFolder);
    });

    // Обработка события "dragover" для папок и элементов "назад"
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
        var itemID = event.originalEvent.dataTransfer.getData("item-id");
        var isFolder = event.originalEvent.dataTransfer.getData("is-folder") === "true";

        // Проверяем, является ли перетаскиваемый элемент файлом или папкой
        if (isFolder) {
            // Обработка перетаскиваемой папки
            // Отправьте данные на сервер для перемещения папки в папку или в `file_list`
            $.ajax({
                url: "/cloud/move-folder/" + folderID + "/" + itemID + "/",
                method: "GET",
                success: function (data) {
                    // Обновите список файлов и папок на странице, чтобы отразить изменения
                    location.reload(); // Простой способ обновить страницу
                }
            });
        } else {
            // Обработка перетаскиваемого файла
            // Отправьте данные на сервер для перемещения файла в папку или в `file_list`
            $.ajax({
                url: "/cloud/move-file/" + folderID + "/" + itemID + "/",
                method: "GET",
                success: function (data) {
                    // Обновите список файлов и папок на странице, чтобы отразить изменения
                    location.reload(); // Простой способ обновить страницу
                }
            });
        }
    });
});


// Открывает модальное окно
function openModal(event) {
    event.preventDefault(); // Предотвращает стандартное действие при клике на ссылке
    document.getElementById('createFolderModal').style.display = 'block';
}

// Закрывает модальное окно
function closeModal() {
    document.getElementById('createFolderModal').style.display = 'none';
}


// Отправляет форму AJAX-запросом
function submitForm() {
    var folderName = $('#folderName').val(); // Получаем значение из поля ввода
    var url = $('#createFolderForm').attr('action'); // Получаем URL из формы

    // Добавьте обработку AJAX-запроса с использованием jQuery.ajax
    $.ajax({
        type: 'POST',
        url: url,
        data: {
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            'name': folderName,
        },
        success: function () {
            // После успешного создания папки перезагрузите страницу
            location.reload();
        },
        error: function () {
            // Обработка ошибок при выполнении AJAX-запроса
            console.error('Ошибка AJAX-запроса');
        }
    });
}