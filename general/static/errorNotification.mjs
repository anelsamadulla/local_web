'use strict'


class ErrorNotification {
    constructor() {
        this.errors = document.querySelectorAll('.errors span');
        this.toastContainer = document.querySelector('.toast-container');
        for (let i = 0; i < this.errors.length; i++) {
            const html = `
                <div class="toast text-danger" id="error-${i}" data-bs-autohide="false" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header">
                        <strong class="me-auto">Cuba</strong>
                        <small class="text-body-secondary"></small>
                        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        ${this.errors[i].innerHTML}
                    </div>
                </div> 
            `;

            this.toastContainer.insertAdjacentHTML('afterbegin', html);
            const toast = document.getElementById(`error-${i}`);
            const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);
            toastBootstrap.show()
        }
    }
}


const errorNotification = new ErrorNotification() 
