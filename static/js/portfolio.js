/* Masonry filters + lightbox (vanilla) */
(function(){
  const grid = document.getElementById('portfolioGrid');
  if(!grid) return;

  // --- Filters
  const chips = document.querySelectorAll('.p-chip');
  const cards = grid.querySelectorAll('.p-card');

  function setFilter(kind){
    cards.forEach(card=>{
      const match = kind==='all' || card.dataset.service===kind;
      card.style.display = match ? 'block' : 'none';
    });
  }
  chips.forEach(ch=>{
    ch.addEventListener('click', ()=>{
      chips.forEach(b=>b.setAttribute('aria-pressed','false'));
      ch.setAttribute('aria-pressed','true');
      setFilter(ch.dataset.filter);
      // trigger reflow to help columns settle
      grid.style.transform='translateZ(0)'; setTimeout(()=>grid.style.transform='',60);
    });
  });

  // --- Lightbox
  const lb = document.getElementById('pLightbox');
  const img = document.getElementById('pImg');
  const prev = document.getElementById('pPrev');
  const next = document.getElementById('pNext');
  const closeBtn = document.getElementById('pClose');

  const order = Array.from(cards);
  let idx = -1;

  function openAt(i){
    idx = i;
    const href = order[idx].getAttribute('href');
    img.src = href;
    lb.classList.add('is-open');
    document.body.style.overflow='hidden';
  }
  function close(){
    lb.classList.remove('is-open');
    document.body.style.overflow='';
    img.src='';
  }
  function step(dir){
    if(idx<0) return;
    idx = (idx + dir + order.length) % order.length;
    img.src = order[idx].getAttribute('href');
  }

  order.forEach((card,i)=>{
    card.addEventListener('click', (e)=>{
      e.preventDefault();
      openAt(i);
    });
  });

  closeBtn.addEventListener('click', close);
  prev.addEventListener('click', ()=>step(-1));
  next.addEventListener('click', ()=>step(1));
  lb.addEventListener('click', (e)=>{ if(e.target===lb) close(); });
  window.addEventListener('keydown', (e)=>{
    if(!lb.classList.contains('is-open')) return;
    if(e.key==='Escape') close();
    if(e.key==='ArrowRight') step(1);
    if(e.key==='ArrowLeft') step(-1);
  });
})();
