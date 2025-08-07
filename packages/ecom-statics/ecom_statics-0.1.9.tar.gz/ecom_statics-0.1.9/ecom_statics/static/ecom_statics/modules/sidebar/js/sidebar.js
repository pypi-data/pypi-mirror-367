/*document.addEventListener('DOMContentLoaded', () => {
    OverlayScrollbarsGlobal.OverlayScrollbars(document.querySelector('.sidebar-wrapper'), {
        scrollbars: {
            theme: 'os-theme-light',
            autoHide: 'leave',
            clickScroll: true
        }
    });

    document.querySelectorAll('.sidebar-wrapper .nav-link').forEach(nav_link_element => {
        nav_link_element.addEventListener('click', () => nav_link_element.blur());
        nav_link_element.addEventListener('auxclick', (e) => e.button === 1 && nav_link_element.blur());
    });

    document.querySelectorAll('.sidebar-wrapper .nav-item').forEach(nav_item_element =>
        nav_item_element.querySelector('.nav-treeview') && nav_item_element.querySelector('.active') && nav_item_element.classList.add('menu-open')
    );
});*/


const SELECTOR_SIDEBAR_WRAPPER = ".sidebar-wrapper"
const Default = {
  scrollbarTheme: "os-theme-light",
  scrollbarAutoHide: "leave",
  scrollbarClickScroll: true
}
document.addEventListener("DOMContentLoaded", function () {
  const sidebarWrapper = document.querySelector(SELECTOR_SIDEBAR_WRAPPER)
  if (
    sidebarWrapper &&
      OverlayScrollbarsGlobal?.OverlayScrollbars !== undefined
  ) {
    OverlayScrollbarsGlobal.OverlayScrollbars(sidebarWrapper, {
      scrollbars: {
        theme: Default.scrollbarTheme,
        autoHide: Default.scrollbarAutoHide,
        clickScroll: Default.scrollbarClickScroll
      }
    })
  }
})
