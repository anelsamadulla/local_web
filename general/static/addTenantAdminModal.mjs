'use strict'


class AddTenantAdminModal {
    constructor() {
        // Modal window
        this.modal = document.querySelector('#addTenantAdminModal');
        // Trigger button
        this.btn = document.querySelector('#addAdmin');
        // Modal window
        this.modal = new bootstrap.Modal('#addTenantAdminModal');
        this.initEventListener();
    }

    initEventListener() {
        this.btn.addEventListener('click', event => {
            event.preventDefault();
            console.log(this.modal)
            //Display modal
            this.modal.show();
        })
    }
    
}

const addTenantAdminModal = new AddTenantAdminModal();
