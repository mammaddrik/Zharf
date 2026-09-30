const workspace = document.querySelector('.workspace');
const workspaceSidebar = document.querySelector('.workspace-sidebar');
const workspaceSidebarToggle = document.querySelector('.workspace-sidebar-toggle');

if (
    workspace &&
    workspaceSidebar &&
    workspaceSidebarToggle
) {
    workspaceSidebarToggle.addEventListener('click', function () {
        const isCollapsed = workspaceSidebar.classList.toggle('is-collapsed');

        workspace.classList.toggle(
            'is-collapsed',
            isCollapsed
        );

        workspaceSidebarToggle.setAttribute(
            'aria-label',
            isCollapsed
                ? 'Expand sidebar'
                : 'Collapse sidebar'
        );
    });
}