(function () {
  // Mobile summary toggle (collapsed by default on mobile)
  const aside = document.querySelector('.bn-summary');
  const btn = document.querySelector('[data-js="summary-toggle"]');
  if (aside && btn) {
    const mq = window.matchMedia('(max-width: 900px)');
    const applyMobileDefault = () => {
      if (mq.matches) {
        aside.setAttribute('data-collapsed', '');
        aside.removeAttribute('data-open');
        btn.setAttribute('aria-expanded', 'false');
      } else {
        // desktop default open
        aside.setAttribute('data-collapsed', '');
        aside.setAttribute('data-open', '');
        btn.setAttribute('aria-expanded', 'true');
      }
    };
    applyMobileDefault();
    mq.addEventListener('change', applyMobileDefault);
    btn.addEventListener('click', () => {
      const open = aside.hasAttribute('data-open');
      if (open) {
        aside.removeAttribute('data-open');
        btn.setAttribute('aria-expanded', 'false');
      } else {
        aside.setAttribute('data-open', '');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  }

  // --- Service selection (DB-driven) ---
  const form = document.getElementById('bn-service-form');
  if (form) {
    const catInput = document.getElementById('bn-category');
    const svcInput = document.getElementById('bn-service-id');
    const cats = document.querySelectorAll('#bn-cats .bn-card');
    const svcWrap = document.getElementById('bn-services');
    const services = document.querySelectorAll('#bn-services .bn-card');

    // Click category → reveal matching services
    cats.forEach(btn => {
      btn.addEventListener('click', () => {
        const cat = btn.getAttribute('data-category');
        catInput.value = cat;
        svcWrap.classList.remove('hidden');

        // Filter services by selected category
        services.forEach(s => {
          const sc = s.getAttribute('data-category');
          s.style.display = (sc === cat) ? '' : 'none';
        });

        svcWrap.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });

    // Click service → set hidden field and submit immediately
    services.forEach(btn => {
      btn.addEventListener('click', () => {
        svcInput.value = btn.getAttribute('data-service');

        // Also include the service slug as a hidden input so the view can map service_key if needed
        const key = btn.getAttribute('data-service-key') || '';
        let hiddenKey = form.querySelector('input[name="service_key"]');
        if (!hiddenKey) {
          hiddenKey = document.createElement('input');
          hiddenKey.type = 'hidden';
          hiddenKey.name = 'service_key';
          form.appendChild(hiddenKey);
        }
        hiddenKey.value = key;

        form.submit();
      });
    });
  }

  // Details page: show relevant section based on service key (from session if available)
  const detailSections = document.querySelectorAll('.bn-detail');
  if (detailSections.length) {
    // Try to infer from a hidden input placed by your view in the future; fallback to URL/session later
    const inlineKey = (window.BN_SELECTED && BN_SELECTED.serviceKey) || '';
    const urlKey = new URLSearchParams(location.search).get('k') || '';
    const key = inlineKey || urlKey;

    const showKey = (k) => {
      detailSections.forEach(sec => {
        sec.style.display = (sec.getAttribute('data-detail') === k) ? 'block' : 'none';
      });
      // If no key, default to show all (so user can still fill)
      if (!k) detailSections.forEach(sec => sec.style.display = 'block');
    };
    showKey(key);
  }
})();
