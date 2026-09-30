const workspace = document.querySelector('.workspace');
const workspaceSidebar = document.querySelector('.workspace-sidebar');
const workspaceSidebarToggle = document.querySelector('.workspace-sidebar-toggle');
const workspaceMobileMenu = document.querySelector('.workspace-mobile-menu');
const workspaceSidebarOverlay = document.querySelector('.workspace-sidebar-overlay');

if (
    workspace &&
    workspaceSidebar &&
    workspaceSidebarToggle
) {
    workspaceSidebarToggle.addEventListener('click', function () {
        if (window.innerWidth <= 767) {
            closeMobileSidebar();
            return;
        }

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

function openMobileSidebar() {
    workspaceSidebar.classList.add('is-mobile-open');
    workspaceSidebarOverlay.classList.add('is-visible');
    document.body.classList.add('workspace-sidebar-open');

    workspaceMobileMenu.setAttribute(
        'aria-label',
        'Close sidebar'
    );
}

function closeMobileSidebar() {
    workspaceSidebar.classList.remove('is-mobile-open');
    workspaceSidebarOverlay.classList.remove('is-visible');
    document.body.classList.remove('workspace-sidebar-open');

    workspaceMobileMenu.setAttribute(
        'aria-label',
        'Open sidebar'
    );
}

if (
    workspaceMobileMenu &&
    workspaceSidebarOverlay &&
    workspaceSidebar
) {
    workspaceMobileMenu.addEventListener(
        'click',
        openMobileSidebar
    );

    workspaceSidebarOverlay.addEventListener(
        'click',
        closeMobileSidebar
    );

    const workspaceLinks = workspaceSidebar.querySelectorAll(
        '.workspace-navigation-link'
    );

    workspaceLinks.forEach(function (link) {
        link.addEventListener(
            'click',
            closeMobileSidebar
        );
    });

    document.addEventListener(
        'keydown',
        function (event) {
            if (
                event.key === 'Escape' &&
                workspaceSidebar.classList.contains('is-mobile-open')
            ) {
                closeMobileSidebar();
            }
        }
    );

    window.addEventListener(
        'resize',
        function () {
            if (window.innerWidth > 767) {
                closeMobileSidebar();
            }
        }
    );
}