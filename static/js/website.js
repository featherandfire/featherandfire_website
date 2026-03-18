// signup.html radio button functionality

function updateLabels() {
    const buyerRadio = document.querySelector('input[value="buyer"]');
    const sellerRadio = document.querySelector('input[value="seller"]');
    const buyerLabel = document.getElementById('buyer-label');
    const sellerLabel = document.getElementById('seller-label');

    if (buyerRadio.checked) {
        buyerLabel.style.borderColor = '#C0622A';
        sellerLabel.style.borderColor = 'rgba(255,255,255,0.1)';
    } else {
        sellerLabel.style.borderColor = '#C0622A';
        buyerLabel.style.borderColor = 'rgba(255,255,255,0.1)';
    }
}
updateLabels();
