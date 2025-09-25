// Instant Quote modal loader + AJAX steps (no prices shown)
(function(){
  const modal = document.getElementById('iqModal');
  const mount = document.getElementById('iqMount');
  if (!modal || !mount) return;

  // open/close
  const openers = document.querySelectorAll('.js-open-quote');
  openers.forEach(btn => btn.addEventListener('click', (e) => {
    e.preventDefault();
    openModal();
    loadStep(1);
  }));
  modal.addEventListener('click', (e) => {
    if (e.target.classList.contains('js-iq-close')) closeModal();
  });
  document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeModal(); });

  function openModal(){ modal.removeAttribute('hidden'); }
  function closeModal(){ modal.setAttribute('hidden',''); mount.innerHTML=''; }

  async function loadStep(step, body=null){
    const url = `/instant-quote/?dialog=1&step=${step}`;
    const opts = body ? {method:'POST', headers:{'X-Requested-With':'fetch','Content-Type':'application/x-www-form-urlencoded'}, body} : {};
    const res = await fetch(url, opts);
    const html = await res.text();
    mount.innerHTML = html;

    // Bind Step 1 icon-cards
    const hidden = mount.querySelector('input[name="service"]');
    const cards = mount.querySelectorAll('.svc-card');
    cards.forEach(card=>{
      card.addEventListener('click', ()=>{
        cards.forEach(c=>c.setAttribute('aria-checked','false'));
        card.setAttribute('aria-checked','true');
        if(hidden) hidden.value = card.dataset.id;
      });
    });

    // Bind step form submit (advance via AJAX)
    const form = mount.querySelector('form[data-iq]');
    if (form) {
      form.addEventListener('submit', (e)=>{
        e.preventDefault();
        const fd = new URLSearchParams(new FormData(form));
        const nextStep = Number(form.dataset.nextStep || (step+1));
        loadStep(nextStep, fd.toString());
      });
    }

    // Enhance steppers
    mount.querySelectorAll('.stepper').forEach(w=>{
      const minus = w.querySelector('[data-step="-1"]');
      const plus  = w.querySelector('[data-step="1"]');
      const input = w.querySelector('input');
      const clamp = v => Math.max(Number(input.min||0), Number(v||0));
      minus?.addEventListener('click', ()=>{ input.value = clamp(Number(input.value)-1); input.dispatchEvent(new Event('change'));});
      plus?.addEventListener('click',  ()=>{ input.value = clamp(Number(input.value)+1); input.dispatchEvent(new Event('change'));});
    });

    // Enhance chips (boolean toggles)
    mount.querySelectorAll('.chip').forEach(ch=>{
      ch.addEventListener('click', ()=>{
        const pressed = ch.getAttribute('aria-pressed')==='true';
        ch.setAttribute('aria-pressed', String(!pressed));
        const cb = mount.querySelector(`input[name="${ch.dataset.name}"]`);
        if (cb) cb.checked = !pressed;
      });
    });
  }
})();
