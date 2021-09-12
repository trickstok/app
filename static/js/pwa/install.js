let deferredInstallPrompt;
const installButton = document.getElementById('installButton');
installButton.addEventListener('click', installPWA);
window.addEventListener('beforeinstallprompt', function(event) {
    event.preventDefault();
    deferredInstallPrompt = event;
    installButton.removeAttribute('hidden');
})

function installPWA(evt) {
    if (deferredInstallPrompt) {
        deferredInstallPrompt.prompt();
    }
    evt.srcElement.setAttribute('hidden', true);
   let getChoice = new Promise( () => {
        deferredInstallPrompt.userChoice
            .then((choice) => {
                if (choice.outcome === 'accepted') {
                    console.log('User accepted the A2HS prompt', choice);
                } else {
                    console.log('User dismissed the A2HS prompt', choice);
                }
                deferredInstallPrompt = null;
            });
    })
    getChoice.catch((error) => {
        alert('Un problème est survenu, cela peut être du au navigateur (seulement Chrome, Edge, WebView Android et Samsung Internet sont compatibles avec cette fonctionnalité)')
        console.error(error)
    })

}

window.addEventListener('appinstalled', logAppInstalled);

function logAppInstalled(evt) {
    alert('L\'application a bien été installée !')
    console.log('App was installed.', evt);
}