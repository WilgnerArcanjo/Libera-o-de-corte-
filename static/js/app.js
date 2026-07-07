document.addEventListener('DOMContentLoaded', () => {
  const flashItems = document.querySelectorAll('.flash-list li');
  flashItems.forEach((item) => {
    item.addEventListener('click', () => item.remove());
  });
});
