const openModal = document.getElementById("open-modal");
const modal = document.getElementById("modal");
const closeModal = document.querySelector(".close-modal");
const selectAvatar = document.querySelector(".select-avatar");

openModal.addEventListener("click", () => {
  modal.style.display = "block";
  modal.classList.add("slide-in");
});

closeModal.addEventListener("click", () => {
  modal.classList.add("slide-out");
  setTimeout(() => {
    modal.style.display = "none";
    modal.classList.remove("slide-out");
  }, 600);
});

selectAvatar.addEventListener("click", () => {
  modal.classList.add("slide-out");
  setTimeout(() => {
    modal.style.display = "none";
    modal.classList.remove("slide-out");
  }, 600);
});

window.addEventListener("click", (event) => {
  if (event.target == modal) {
    modal.classList.add("slide-out");
    setTimeout(() => {
      modal.style.display = "none";
      modal.classList.remove("slide-out");
    }, 600);
  }
});
