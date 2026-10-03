const avatarInput = document.querySelector(
    '#id_avatar'
);

const avatarPreview = document.querySelector(
    '.account-avatar img'
);

const avatarPlaceholder = document.querySelector(
    '.account-avatar i'
);

if (avatarInput && avatarPreview) {

    avatarInput.addEventListener(
        'change',
        function () {

            const file = avatarInput.files[0];

            if (!file) {
                return;
            }

            if (!file.type.startsWith('image/')) {
                return;
            }

            const reader = new FileReader();

            reader.addEventListener(
                'load',
                function () {

                    avatarPreview.src = reader.result;
                    avatarPreview.hidden = false;

                    if (avatarPlaceholder) {
                        avatarPlaceholder.hidden = true;
                    }

                }
            );

            reader.readAsDataURL(file);

        }
    );

}

const deleteAccountForm = document.querySelector(
    'form input[name="action"][value="delete"]'
)?.closest('form');

const deleteAccountTrigger = document.querySelector(
    '[data-delete-account-trigger]'
);

const deleteAccountModal = document.querySelector(
    '[data-delete-account-modal]'
);

const deleteAccountConfirm = document.querySelector(
    '[data-delete-account-confirm]'
);

const deleteAccountCloseButtons = document.querySelectorAll(
    '[data-delete-account-close]'
);

const openDeleteAccountModal = () => {

    if (!deleteAccountModal) {
        return;
    }

    deleteAccountModal.classList.add(
        'is-visible'
    );

    deleteAccountModal.setAttribute(
        'aria-hidden',
        'false'
    );

    document.body.style.overflow = 'hidden';

};

const closeDeleteAccountModal = () => {

    if (!deleteAccountModal) {
        return;
    }

    deleteAccountModal.classList.remove(
        'is-visible'
    );

    deleteAccountModal.setAttribute(
        'aria-hidden',
        'true'
    );

    document.body.style.overflow = '';

};

if (
    deleteAccountForm &&
    deleteAccountTrigger &&
    deleteAccountModal &&
    deleteAccountConfirm
) {

    deleteAccountTrigger.addEventListener(
        'click',
        function () {
            openDeleteAccountModal();
        }
    );

    deleteAccountConfirm.addEventListener(
        'click',
        function () {
            deleteAccountForm.submit();
        }
    );

    deleteAccountCloseButtons.forEach(
        function (button) {

            button.addEventListener(
                'click',
                function () {
                    closeDeleteAccountModal();
                }
            );

        }
    );

    document.addEventListener(
        'keydown',
        function (event) {

            if (
                event.key === 'Escape' &&
                deleteAccountModal.classList.contains('is-visible')
            ) {
                closeDeleteAccountModal();
            }

        }
    );

}