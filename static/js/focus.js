document.addEventListener('keydown', function(event) {
    if (event.key === '/') {
      event.preventDefault();
      document.getElementById('text-area').focus();
    }
  });
  