import { CountUp } from "countup.js";

/** Same settings the real dashboard uses for its counters. */
const DURATION = 3;

const decimalsOf = (text: string) => (text.split(".")[1] ?? "").length;

/** Starts each counter the first time its element scrolls into view. */
const pending = new WeakMap<Element, CountUp>();
const inView = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    pending.get(entry.target)?.start();
    pending.delete(entry.target);
    inView.unobserve(entry.target);
  }
});

/** Count a number up inside `el`, starting once it is on screen. */
export function tickerFor(el: HTMLElement, end: number, decimalPlaces: number): CountUp {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const counter = new CountUp(el, end, {
    duration: reduced ? 0.01 : DURATION,
    decimalPlaces,
    useGrouping: true,
  });
  pending.set(el, counter);
  inView.observe(el);
  return counter;
}

/** Animate every `[data-countup]` number in the static shell (once per element). */
export function startShellTickers(root: ParentNode = document): void {
  root.querySelectorAll<HTMLElement>("[data-countup]").forEach((el) => {
    if (el.dataset.countup === "on") return;
    const text = (el.textContent ?? "").trim();
    const end = Number(text.replace(/,/g, ""));
    if (!Number.isFinite(end) || end === 0) return;
    el.dataset.countup = "on";
    tickerFor(el, end, decimalsOf(text));
  });
}
