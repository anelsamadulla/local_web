

class OpenActivationTab {
    constructor() {
        this.links = document.querySelectorAll('.activation-link');
        console.log(this.links);
    }

    findActivationLink() {
        if (this.links.length != 0) {
            const href = this.links[0].getAttribute('href')
            window.open(href, '_blank');
        }

    }
}

const openActivationTab = new OpenActivationTab();
openActivationTab.findActivationLink();
