'use strict';

class Modal {
    constructor() {
        this.modal = document.querySelector('#personal-info');
        this.toggleButton = document.querySelector('#personal-info-toggle');
        console.log(this.toggleButton);

        this.openModal = false;
        this.openModal ? this.displayModal() : this.hideModal();
        this.initEvents();
    }

    setOpenModal(value) {
        value ? this.displayModal() : this.hideModal();
        this.openModal = value;
    }

    displayModal() {
        if (this.modal.classList.contains('hidden')){
            this.modal.classList.remove('hidden');
        }
    }

    hideModal() {
        if (!this.modal.classList.contains('hidden')) {
            this.modal.classList.add('hidden');
        }
    }

    initEvents() {
        this.toggleButton.addEventListener('click', event => {
            event.preventDefault();
            this.setOpenModal(!this.openModal);
        })
    }
}

const modal = new Modal();
