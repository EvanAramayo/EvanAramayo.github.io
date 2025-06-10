function filterCards(type) {
  const cards = document.querySelectorAll('.flip-container');

  cards.forEach(card => {
    const shouldShow = (type === 'all' || card.dataset.type === type);

    if (shouldShow) {
      card.style.display = 'block';
      anime({
        targets: card,
        opacity: [0, 1],
        translateY: [-20, 0],
        duration: 500,
        easing: 'easeOutQuad'
      });
    } else {
      anime({
        targets: card,
        opacity: [1, 0],
        translateY: [0, 20],
        duration: 300,
        easing: 'easeInQuad',
        complete: () => {
          card.style.display = 'none';
        }
      });
    }
  });
}
