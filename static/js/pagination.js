function setupAjaxPagination(tableSelector, urlBase) {
    function reloadTable(page = 1) {
        fetch(`${urlBase}?page=${page}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector(`${tableSelector} tbody`);
            if (tbody) tbody.innerHTML = data.rows;

            const pagination = document.querySelector('#pagination-container');
            if (pagination) pagination.innerHTML = data.pagination;

            attachEvents();  // Gắn lại sự kiện cho nút mới
        })
        .catch(err => console.error('Lỗi load bảng:', err));
    }

    function attachEvents() {
        document.querySelectorAll('.pagination-link').forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const page = this.dataset.page;
                reloadTable(page);
            });
        });
    }

    attachEvents();
}
