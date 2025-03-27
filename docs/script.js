document.addEventListener('DOMContentLoaded', () => {
    const clientIdInput = document.getElementById('clientId');
    const clientSecretInput = document.getElementById('clientSecret');
    const playlistIdInput = document.getElementById('playlistId');
    const downloadBtn = document.getElementById('downloadBtn');
    const statusDiv = document.getElementById('status');
    const downloadLogDiv = document.getElementById('downloadLog');

    let isDownloading = false;

    downloadBtn.addEventListener('click', async (e) => {
        e.preventDefault();

        if (isDownloading) return;

        const clientId = clientIdInput.value.trim();
        const clientSecret = clientSecretInput.value.trim();
        const playlistId = playlistIdInput.value.trim();

        if (!clientId || !clientSecret || !playlistId) {
            statusDiv.textContent = 'Please fill in all fields';
            statusDiv.className = 'status error';
            return;
        }

        isDownloading = true;
        statusDiv.textContent = 'Downloading playlist...';
        statusDiv.className = 'status success';
        downloadBtn.disabled = true;

        try {
            const response = await fetch('/download-playlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    clientId,
                    clientSecret,
                    playlistId
                }),
                timeout: 300000
            });

            const result = await response.json();

            if (result.success) {
                statusDiv.textContent = `Successfully downloaded ${result.trackCount} tracks`;
                statusDiv.className = 'status success';

                downloadLogDiv.innerHTML = result.tracks.map(track => 
                    `<div>${track.original_name}</div>`
                ).join('');
            } else {
                statusDiv.textContent = `Error: ${result.error}`;
                statusDiv.className = 'status error';
            }
        } catch (error) {
            statusDiv.textContent = `Network error: ${error.message}`;
            statusDiv.className = 'status error';
        } finally {
            isDownloading = false;
            downloadBtn.disabled = false;
        }
    });
});