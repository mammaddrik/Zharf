
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".todo-filter-form");
    const searchInput = form?.querySelector('input[name="q"]');

    if (!form || !searchInput) return;

    let debounceTimer;
    let controller;
    let requestNumber = 0;

    const getActiveStatus = () => {
        return (
            form.querySelector(".todo-filter-button.is-active")?.value ||
            new URLSearchParams(window.location.search).get("status") ||
            "all"
        );
    };

    async function updateTodos({ updateUrl = true } = {}) {
        const currentRequest = ++requestNumber;

        if (controller) controller.abort();
        controller = new AbortController();

        const params = new URLSearchParams();
        const query = searchInput.value.trim();
        const status = getActiveStatus();

        if (query) params.set("q", query);
        if (status !== "all") params.set("status", status);

        const url = `${form.action}?${params.toString()}`;

        try {
            const response = await fetch(url, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                signal: controller.signal
            });

            if (!response.ok) {
                throw new Error(`Request failed: ${response.status}`);
            }

            const html = await response.text();

            if (currentRequest !== requestNumber) return;

            const parsedDocument = new DOMParser().parseFromString(
                html,
                "text/html"
            );

            const newTodoList = parsedDocument.querySelector(".todo-list");
            const currentTodoList = document.querySelector(".todo-list");

            if (!newTodoList || !currentTodoList) {
                throw new Error("Todo list was not found in the response.");
            }

            currentTodoList.innerHTML = newTodoList.innerHTML;

            if (updateUrl) {
                const newUrl = `${window.location.pathname}${
                    params.toString() ? `?${params.toString()}` : ""
                }`;

                window.history.replaceState({}, "", newUrl);
            }
        } catch (error) {
            if (error.name === "AbortError") return;
            console.error("Todo search failed:", error);
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);

        form.querySelectorAll(".todo-filter-button").forEach((button) => {
            button.classList.remove("is-active");
        });

        const allButton = form.querySelector(
            '.todo-filter-button[value="all"]'
        );

        if (allButton) {
            allButton.classList.add("is-active");
        }

        debounceTimer = setTimeout(() => {
            updateTodos();
        }, 300);
    });

    form.querySelectorAll(".todo-filter-button").forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();

            form.querySelectorAll(".todo-filter-button").forEach((item) => {
                item.classList.remove("is-active");
            });

            button.classList.add("is-active");

            clearTimeout(debounceTimer);
            updateTodos();
        });
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        updateTodos();
    });
});
