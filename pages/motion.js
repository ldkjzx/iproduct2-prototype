/* ============================================================================
 * iProduct · motion.js
 * Zero-build animation layer — vanilla Web Animations API, no dependencies.
 * Driven by the SAME spring/smooth tokens as the CSS design system, so the
 * feel stays consistent with the rest of the prototype (no foreign look).
 *
 * What it adds on top of the existing CSS:
 *   1. Staggered card / chip entrance (fade + rise) on first paint
 *   2. Spring toast (enter + auto exit) wired to natural triggers
 *   3. prefers-reduced-motion guard (skips motion, keeps content visible)
 *
 * Everything degrades gracefully: if WAAPI is unavailable the elements simply
 * stay visible; if JS never runs the page is unchanged.
 * ========================================================================== */
(function () {
  'use strict';

  // Mirror of --ease-spring / --ease-smooth (valid WAAPI easing strings)
  var SPRING = 'cubic-bezier(0.34, 1.56, 0.64, 1)';
  var SMOOTH = 'cubic-bezier(0.4, 0, 0.2, 1)';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var canAnimate = (typeof document.documentElement.animate === 'function') ||
    (typeof Element !== 'undefined' && typeof Element.prototype.animate === 'function');

  /* ---- Staggered entrance ------------------------------------------------- */
  function staggerIn(selector, opts) {
    opts = opts || {};
    var els = Array.prototype.slice.call(document.querySelectorAll(selector));
    if (!els.length) return;

    // No WAAPI or reduced motion: reveal immediately (CSS `.js-anim` hides them)
    if (!canAnimate || reduceMotion) {
      els.forEach(function (el) { el.style.opacity = '1'; });
      return;
    }

    var base = opts.baseDelay || 60;
    var step = opts.step || 55;
    var rise = opts.rise != null ? opts.rise : 14;
    var dur = opts.duration || 520;

    // Initial hidden state is provided by CSS (.js-anim ...) to avoid a flash;
    // WAAPI animates 0 -> 1 and fill:both keeps the final state visible.
    els.forEach(function (el, i) {
      el.style.willChange = 'transform, opacity';
      var anim = el.animate(
        [
          { opacity: 0, transform: 'translateY(' + rise + 'px) scale(0.985)' },
          { opacity: 1, transform: 'translateY(0) scale(1)' }
        ],
        {
          duration: dur,
          delay: base + i * step,
          easing: SMOOTH,
          fill: 'both'
        }
      );
      if (anim) {
        try {
          anim.onfinish = function () { el.style.willChange = 'auto'; };
        } catch (e) { /* noop */ }
      }
    });
  }

  /* ---- Toast -------------------------------------------------------------- */
  var container = null;
  function ensureContainer() {
    if (container) return container;
    container = document.createElement('div');
    container.id = 'toast-container';
    container.setAttribute('role', 'status');
    container.setAttribute('aria-live', 'polite');
    document.body.appendChild(container);
    return container;
  }

  function toast(message, opts) {
    opts = opts || {};
    var box = ensureContainer();
    var el = document.createElement('div');
    el.className = 'toast' + (opts.variant ? ' toast--' + opts.variant : '');
    el.textContent = message;
    box.appendChild(el);

    var life = opts.duration || 2600;

    if (!canAnimate || reduceMotion) {
      el.style.opacity = '1';
      setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, life);
      return;
    }

    el.animate(
      [
        { opacity: 0, transform: 'translateY(12px) scale(0.92)' },
        { opacity: 1, transform: 'translateY(0) scale(1)' }
      ],
      { duration: 320, easing: SPRING, fill: 'both' }
    );

    setTimeout(function () {
      var out = el.animate(
        [
          { opacity: 1, transform: 'translateY(0) scale(1)' },
          { opacity: 0, transform: 'translateY(8px) scale(0.96)' }
        ],
        { duration: 220, easing: SMOOTH, fill: 'both' }
      );
      out.onfinish = function () { if (el.parentNode) el.parentNode.removeChild(el); };
    }, life);
  }

  /* ---- Wire natural triggers -------------------------------------------- */
  function cardTitle(card) {
    var span = card.querySelector('span');
    return span ? span.textContent.trim() : '模板';
  }

  function wireToasts() {
    document.addEventListener('click', function (e) {
      var t = e.target;
      if (!t || !t.closest) return;

      var exec = t.closest('.template-card .btn-primary');
      if (exec) {
        var card = exec.closest('.template-card');
        toast('已触发执行 · ' + (card ? cardTitle(card) : '模板'));
        return;
      }
      var send = t.closest('.composer-send');
      if (send) { toast('已发送 · 正在为你编排执行'); return; }

      var upload = t.closest('[title="上传文件"]');
      if (upload) { toast('文件上传（演示）'); return; }

      var chip = t.closest('.action-chip');
      if (chip) {
        var label = (chip.textContent || '').trim();
        if (label) toast(label);
        return;
      }
    });
  }

  /* ---- Init --------------------------------------------------------------- */
  function init() {
    staggerIn('.template-card', { baseDelay: 70, step: 48, rise: 16, duration: 520 });
    staggerIn('.filter-tag', { baseDelay: 40, step: 45, rise: 8, duration: 420 });
    staggerIn('.action-chip', { baseDelay: 110, step: 70, rise: 14, duration: 480 });
    staggerIn('.chat-input', { baseDelay: 30, step: 0, rise: 10, duration: 480 });
    wireToasts();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for manual use / future wiring
  window.iProductMotion = { staggerIn: staggerIn, toast: toast };
})();
