const sidebar = document.getElementById('sidebar');
const sidebarLinks = sidebar.querySelectorAll('a');
const sidebarIconColors = sidebar.querySelectorAll('i');

const toggleSidebarText = (isHovered) => {
  sidebarLinks.forEach(link => {
    const textElement = link.querySelector('span');
    if (textElement) {
      if (isHovered) {
        textElement.classList.add('text-white');
      } else {
        textElement.classList.remove('text-white');
      }
    }
  });

  sidebarIconColors.forEach(icon => {
    if (isHovered) {
      icon.classList.add('text-white');
      icon.classList.remove('text-blue-600', 'dark:text-blue-300');
    } else {
      icon.classList.remove('text-white');
      icon.classList.add('text-blue-600', 'dark:text-blue-300');
    }
  });
};

sidebar.addEventListener('mouseenter', () => {
  sidebar.classList.remove('w-16', 'sm:w-20');
  sidebar.classList.add('w-64');
});

sidebar.addEventListener('mouseleave', () => {
  sidebar.classList.remove('w-64');
  sidebar.classList.add('w-16', 'sm:w-20');
});

const userIcon = document.getElementById('user-icon');
const userMenu = document.getElementById('user-menu');

userIcon.addEventListener('click', (event) => {
  event.stopPropagation();
  userMenu.classList.toggle('hidden');
});

document.addEventListener('click', (event) => {
  if (!userMenu.contains(event.target) && !userIcon.contains(event.target)) {
    userMenu.classList.add('hidden');
  }
});

const logoutButton = document.getElementById('btnLogout');
logoutButton.addEventListener('click', () => {
  window.location.href = '/logout';
});

document.getElementById("anoAtual").textContent = new Date().getFullYear();