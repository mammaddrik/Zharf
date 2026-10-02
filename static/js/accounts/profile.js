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