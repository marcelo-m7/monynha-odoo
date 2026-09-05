/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

function initProjectSignalFollowup(link) {
    if (link.dataset.monynhaReady === "1") {
        return;
    }
    link.dataset.monynhaReady = "1";

    const status = link.parentElement?.querySelector("[data-monynha-followup-status]");
    const token = link.dataset.monynhaToken || "";

    link.addEventListener("click", async (event) => {
        if (!token) {
            return;
        }
        event.preventDefault();
        if (link.dataset.monynhaSubmitting === "1") {
            return;
        }

        link.dataset.monynhaSubmitting = "1";
        link.setAttribute("aria-disabled", "true");
        if (status) {
            status.textContent = "A registar o próximo passo…";
        }

        try {
            const result = await rpc("/monynha/diagnosis/followup", { token });
            if (!result?.ok) {
                throw new Error("Não foi possível registar o pedido.");
            }
            link.textContent = result.already_requested ? "Pedido já registado" : "Pedido enviado";
            link.dataset.monynhaCompleted = "1";
            if (status) {
                status.textContent = result.already_requested
                    ? "Este Project Signal já tem um pedido de follow-up registado."
                    : "Recebemos o pedido. A próxima conversa vai partir deste Project Signal.";
            }
        } catch {
            link.removeAttribute("aria-disabled");
            link.dataset.monynhaSubmitting = "0";
            if (status) {
                status.textContent = "Não foi possível registar agora. Podes continuar pelo formulário de contacto.";
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-monynha-followup]").forEach(initProjectSignalFollowup);
});
