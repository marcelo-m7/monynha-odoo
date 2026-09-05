/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";
const STORAGE_KEY = "monynha_discovery_draft_v1";
const TOTAL_STEPS = 6;
function safeParseDraft() { try { return JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "null"); } catch { return null; } }
function initDiscovery(root) {
    if (root.dataset.monynhaReady === "1") return;
    root.dataset.monynhaReady = "1";
    const form = root.querySelector("[data-monynha-form]");
    const steps = [...root.querySelectorAll("[data-monynha-step]")];
    const nextButton = root.querySelector("[data-monynha-next]");
    const backButton = root.querySelector("[data-monynha-back]");
    const submitButton = root.querySelector("[data-monynha-submit]");
    const counter = root.querySelector("[data-monynha-counter]");
    const progress = root.querySelector("[data-monynha-progress]");
    const errorNode = root.querySelector("[data-monynha-error]");
    const loading = root.querySelector("[data-monynha-loading]");
    const draft = safeParseDraft();
    const state = { step: Math.max(1, Math.min(TOTAL_STEPS, draft?.step || 1)), data: draft?.data || {} };
    for (const element of form.elements) { if (!element.name || !(element.name in state.data)) continue; if (element.type === "checkbox") element.checked = Boolean(state.data[element.name]); else element.value = state.data[element.name] || ""; }
    const persist = () => { const data = Object.fromEntries(new FormData(form).entries()); data.no_brand = Boolean(form.elements.no_brand?.checked); data.revenue_model = state.data.revenue_model || ""; data.decision_profile = state.data.decision_profile || ""; state.data = data; window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); };
    const render = () => { for (const stepNode of steps) stepNode.hidden = Number(stepNode.dataset.monynhaStep) !== state.step; counter.textContent = `${String(state.step).padStart(2, "0")} / ${String(TOTAL_STEPS).padStart(2, "0")}`; progress.style.width = `${((state.step - 1) / (TOTAL_STEPS - 1)) * 100}%`; backButton.hidden = state.step === 1; nextButton.hidden = state.step === TOTAL_STEPS; submitButton.hidden = state.step !== TOTAL_STEPS; errorNode.textContent = ""; root.querySelectorAll("[data-monynha-field]").forEach((button) => button.classList.toggle("is-selected", state.data[button.dataset.monynhaField] === button.dataset.monynhaValue)); persist(); const firstControl = steps[state.step - 1].querySelector("input:not([type='hidden']), textarea, button"); if (firstControl && !window.matchMedia("(pointer: coarse)").matches) window.setTimeout(() => firstControl.focus({ preventScroll: true }), 0); };
    const validateCurrentStep = () => { persist(); if (state.step === 1 && !/^\S+@\S+\.\S+$/.test(state.data.email || "")) return "Insere um e-mail válido."; if (state.step === 2 && !state.data.no_brand && (state.data.brand_name || "").trim().length < 2) return "Diz-nos o nome do projeto ou marca a opção sem nome."; if (state.step === 3 && !state.data.revenue_model) return "Escolhe como o negócio gera receita."; if (state.step === 4 && !state.data.decision_profile) return "Escolhe a opção que melhor descreve a operação."; if (state.step === 5 && (state.data.struggle || "").trim().length < 10) return "Conta-nos um pouco mais sobre o principal desafio."; return ""; };
    form.addEventListener("input", persist); form.addEventListener("change", persist);
    root.querySelectorAll("[data-monynha-field]").forEach((button) => button.addEventListener("click", () => { state.data[button.dataset.monynhaField] = button.dataset.monynhaValue; render(); }));
    nextButton.addEventListener("click", () => { const error = validateCurrentStep(); if (error) { errorNode.textContent = error; return; } state.step = Math.min(TOTAL_STEPS, state.step + 1); render(); });
    backButton.addEventListener("click", () => { state.step = Math.max(1, state.step - 1); render(); });
    form.addEventListener("submit", async (event) => { event.preventDefault(); const error = validateCurrentStep(); if (error) { errorNode.textContent = error; return; } loading.hidden = false; form.hidden = true; try { const result = await rpc("/monynha/discovery/submit", state.data); if (!result?.ok) throw new Error(result?.error || "Não foi possível concluir o discovery."); window.localStorage.removeItem(STORAGE_KEY); window.location.assign(result.report_url || "/contactus"); } catch (error) { form.hidden = false; loading.hidden = true; errorNode.textContent = error.message || "Não foi possível concluir agora. Tenta novamente."; } });
    window.addEventListener("keydown", (event) => { if (event.key === "Escape" && state.step > 1) { state.step -= 1; render(); } if (event.key === "Enter" && state.step < TOTAL_STEPS && event.target.tagName !== "TEXTAREA") { event.preventDefault(); nextButton.click(); } });
    render();
}
document.addEventListener("DOMContentLoaded", () => document.querySelectorAll("[data-monynha-wizard]").forEach(initDiscovery));
