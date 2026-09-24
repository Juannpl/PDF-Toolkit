const form = document.querySelector('#compress-form');
const status = document.querySelector('#status');
const button = document.querySelector('#submit');
const download = document.querySelector('#download');
let downloadUrl;
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const file = document.querySelector('#file').files[0];
  if (!file) return;
  download.hidden = true;
  if (downloadUrl) URL.revokeObjectURL(downloadUrl);
  if (file.size >= 50 * 1024 * 1024) {
    status.textContent = 'Le fichier doit être inférieur à 50 Mio.';
    return;
  }
  button.disabled = true;
  status.textContent = 'Compression en cours… cela peut prendre jusqu’à deux minutes.';
  try {
    const response = await fetch('/compress', { method: 'POST', body: new FormData(form) });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || 'Le serveur n’a pas pu traiter ce fichier.');
    }
    const blob = await response.blob();
    downloadUrl = URL.createObjectURL(blob);
    download.href = downloadUrl;
    download.download = file.name.replace(/\.pdf$/i, '') + '-compresse.pdf';
    download.hidden = false;
    const gain = Math.max(0, (1 - blob.size / file.size) * 100);
    status.textContent = gain > 0
      ? `Prêt ! ${gain.toFixed(1)} % de réduction · ${(blob.size / 1024 / 1024).toFixed(2)} Mio.`
      : 'Ce document est déjà optimisé : le fichier original est conservé.';
  } catch (error) {
    status.textContent = error.message || 'Connexion interrompue. Réessayez.';
  } finally {
    button.disabled = false;
  }
});
