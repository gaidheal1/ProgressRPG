document.addEventListener('DOMContentLoaded', () => {
  


  const toggleDrawerBtn = document.querySelector(".open-drawer-btn");
  const navDrawer = document.querySelector(".nav-drawer");
  const overlay = document.querySelector(".overlay");

  
  // Open the drawer
  toggleDrawerBtn.addEventListener("click", () => {
    const isOpen = navDrawer.classList.contains("open");

    if (isOpen) {
      navDrawer.classList.remove("open");
      overlay.classList.remove("visible");
    } else {
      navDrawer.classList.add("open");
      overlay.classList.add("visible");
    }
  });

  // Close the drawer when clicking on the overlay
  overlay.addEventListener("click", () => {
      navDrawer.classList.remove("open");
      overlay.classList.remove("visible");
  });

});