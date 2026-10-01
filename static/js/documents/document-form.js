const titleInput = document.querySelector(
    '#id_title'
);

const slugInput = document.querySelector(
    '#id_slug'
);

if (titleInput && slugInput) {
    const initialSlug = slugInput.value;

    let slugManuallyChanged = false;

    slugInput.addEventListener(
        'input',
        function () {
            slugManuallyChanged =
                slugInput.value !== initialSlug;
        }
    );

    titleInput.addEventListener(
        'input',
        function () {
            if (slugManuallyChanged) {
                return;
            }

            const value = titleInput.value
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