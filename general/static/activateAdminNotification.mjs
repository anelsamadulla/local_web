class ActivateAdminNotification {
    constructor() {
        this.links = document.querySelectorAll('.activation-link');
        this.toastContainer = document.querySelector('.toast-container');
        console.log(this.toastContainer);
        // console.log(this.links);
        this.activateAdmin = this.activateAdmin.bind(this); // Bind the method to the class instance
    }

    activateAdmin(adminId, email, newPassword) { // Include email parameter
        fetch('/activate_admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ admin_id: adminId, email: email, new_password: newPassword }), // Include email in the request body
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to activate admin');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    findActivationLink() {
        if (this.links.length != 0) {
            if (this.links[0].dataset.openTab === 'True') {
                const href = this.links[0].getAttribute('href')
                window.open(href, '_blank');
            }

            for (let i = 0; i < this.links.length; i++) {
                const adminId = this.links[i].dataset.adminId;
                this.links[i].addEventListener('click', () => {
                    const newPassword = prompt('Enter new password:');
                    if (newPassword) {
                        this.activateAdmin(adminId, newPassword);
                    }
                });
                
                const html = `
                <div class="toast" id="toast-${i}" data-bs-autohide="false" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header">
                        <strong class="me-auto">Cuba</strong>
                        <small class="text-body-secondary"></small>
                        <a class="btn" target="_blank" href="${this.links[i].getAttribute('href')}">Активировать</a>
                        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        У вас есть неактивированный пользователь:<br>
                        ${this.links[i].dataset.name}
                    </div>
                </div> 
                `;

                this.toastContainer.insertAdjacentHTML('afterbegin', html);

                const toast = document.getElementById(`toast-${i}`);
                const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);
                toastBootstrap
                toastBootstrap.show()
            }
        }
    }
}

const activateAdminNotification = new ActivateAdminNotification();
activateAdminNotification.findActivationLink();
