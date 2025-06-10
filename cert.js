     // === Modal Cert Animation Logic ===
    function openCertModal(id) {
        const modal = document.getElementById(id);
        const content = modal.querySelector('.modal-content');
        modal.style.display = 'block';

    anime({
        targets: content,
        opacity: [0, 1],
        scale: [0.8, 1],
        duration: 500,
        easing: 'easeOutBack'
    });
}

    function closeCertModal(id) {
        const modal = document.getElementById(id);
        const content = modal.querySelector('.modal-content');

    anime({
        targets: content,
        opacity: [1, 0],
        scale: [1, 0.8],
        duration: 300,
        easing: 'easeInBack',
        complete: () => {
            modal.style.display = 'none';
        }
    });
}




// Optional: click background to close
    window.addEventListener('click', function (event) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (event.target === modal) {
                closeCertModal(modal.id);
            }
     });
});

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('.modal').forEach(modal => {
    modal.style.display = 'none';
  });
});
    function openModal(id) {
      document.getElementById(id).style.display = "block";
    }

    function closeModal(id) {
      document.getElementById(id).style.display = "none";
    }

    // Optional: close modal when clicking outside
    window.onclick = function(event) {
      document.querySelectorAll('.modal').forEach(modal => {
        if (event.target === modal) modal.style.display = "none";
      });
    };
