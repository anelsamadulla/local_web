'use strict';

class Modal {
    constructor() {
        // Modal window
        this.modal = document.querySelector('#passwordResetModal');
        
        // Password reset buttons
        this.triggers = document.querySelectorAll('.resetPassword');

        // Add admin button
        this.addAdminBtn = document.querySelector('#addAdmin');
        
        // Selected admin data
        this.fistNameSpan = document.querySelector('#admin-first-name');
        this.lastNameSpan = document.querySelector('#admin-last-name');
        this.adminId = document.querySelector('#password-reset-admin-id');
        
        // Create arrays for different modal elements and add them to the arrays;
        this.resetPasswordModalElems = [];
        this.addAdminModalElems = [];
        this.initElems();

        this.addResetPasswordEventListeners();
        this.addAddAdminEventListener();
    }

    addResetPasswordEventListeners() {
        this.triggers.forEach(trigger => {
            trigger.addEventListener('click', event => {
                event.preventDefault();

                // Display modal
                console.log(event.target);
                const modal = new bootstrap.Modal('#modal', {focus: true})
                modal.show()
                console.log(modal)

                // Set admin first & last name
                console.log(event.target.getAttribute('firstName'));
                this.fistNameSpan.innerHTML = event.target.dataset.firstname;
                this.lastNameSpan.innerHTML = event.target.dataset.lastname;

                // Set admin id in form input
                this.adminId.value = event.target.getAttribute('id');

                // Show corresponding header
                document.querySelector('.modal-title').innerHTML = 'Восстановить пароль';

                // Display reset password elements
                this.addAdminModalElems.forEach(element => {
                    element.classList.add("hidden");
                });
                this.resetPasswordModalElems.forEach(element => {
                    element.classList.remove("hidden");
                });
            })
        })
    }

    addAddAdminEventListener() {
        this.addAdminBtn.addEventListener('click', event => {
            event.preventDefault();

            // Display modal
            const modal = new bootstrap.Modal('#modal', {focus: true});
            modal.show()


            // Show corresponding header
            document.querySelector('.modal-title').innerHTML = 'Создать администратора';

            // Display add admin elements
            this.addAdminModalElems.forEach(element => {
                element.classList.remove("hidden");
            });
            this.resetPasswordModalElems.forEach(element => {
                element.classList.add("hidden");
            });
        })
    }

    initElems() {
        this.resetPasswordModalElems.push(
            document.querySelector('#reset-password-modal-body')
        );

        this.addAdminModalElems.push(
            document.querySelector('#add-admin-modal-body')    
        );
    }
}

const modal = new Modal();
