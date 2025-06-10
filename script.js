

document.addEventListener('DOMContentLoaded', () => {
  const connectSection = document.querySelector('.connect');
  const contentReveal = document.querySelector('.content--reveal');
  const closeButton = document.querySelector('.content__close');
  const menuItems = document.querySelectorAll('.menu__item');

  menuItems.forEach(item => {
    item.addEventListener('click', () => {
      contentReveal.classList.add('active');
      connectSection.style.display = 'none';
    });
  });

  closeButton.addEventListener('click', () => {
    contentReveal.classList.remove('active');

    // Delay showing the connect section (e.g., 800ms)
    setTimeout(() => {
      connectSection.style.display = 'flex'; // or 'block' depending on layout
    }, 500); // 800 milliseconds delay
  });
});

const menuItems = document.querySelectorAll('.menu__item');
const header = document.getElementById('header-content');
const contentContainer = document.querySelector('.content--reveal');

menuItems.forEach(item => {
  item.addEventListener('click', () => {
    header.classList.add('fade-out');
  });
});
document.querySelector('.content__close').addEventListener('click', () => {
  header.classList.remove('fade-out');
});


