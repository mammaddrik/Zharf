const nameInput = document.querySelector(
    '#id_name'
);

const slugInput = document.querySelector(
    '#id_slug'
);

if (nameInput && slugInput) {
    const initialSlug = slugInput.value;

    let slugManuallyChanged = false;

    slugInput.addEventListener(
        'input',
        function () {
            slugManuallyChanged =
                slugInput.value !== initialSlug;
        }
    );

    nameInput.addEventListener(
        'input',
        function () {
            if (slugManuallyChanged) {
                return;
            }

            const value = nameInput.value
                .trim()
                .toLowerCase()
                .replace(
                    /[^a-z0-9]+/g,
                    '-'
                )
                .replace(
                    /^-+|-+$/g,
                    ''
                );

            slugInput.value = value;
        }
    );
}