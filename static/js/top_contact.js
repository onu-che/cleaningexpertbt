// Requires GSAP (already used in your project). If not, add GSAP to your base template.
(function(){
  // Entrance animation
  if (window.gsap){
    gsap.to('#top-contact', { y: 12, opacity: 1, duration: 0.6, ease: 'power3.out' });
    gsap.from('.tc-item', {
      y: -8, opacity: 0, stagger: 0.06, delay: 0.15, duration: 0.4, ease: 'power2.out'
    });
  } else {
    // graceful display if gsap missing
    const el = document.getElementById('top-contact');
    if(el){ el.style.transform = 'none'; el.style.opacity = '1'; }
  }

  // Smart hide on scroll down, show on scroll up
  let lastY = window.scrollY, hidden = false;
  const bar = document.getElementById('top-contact');
  const toggle = (show) => {
    if (!bar) return;
    if (show && hidden){
      hidden = false;
      bar.style.willChange = 'transform';
      bar.animate([{transform:'translateY(-105%)'},{transform:'translateY(0)'}], {duration:220, easing:'ease-out'});
      bar.style.transform = 'translateY(0)';
      setTimeout(()=>bar.style.willChange='',220);
    } else if(!show && !hidden){
      hidden = true;
      bar.style.willChange = 'transform';
      bar.animate([{transform:'translateY(0)'},{transform:'translateY(-105%)'}], {duration:200, easing:'ease-in'});
      bar.style.transform = 'translateY(-105%)';
      setTimeout(()=>bar.style.willChange='',200);
    }
  };
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    toggle(y < 20 || y < lastY); // show when near top or scrolling up
    lastY = y;
  }, {passive:true});

  // Micro-interaction ripple on click
  document.querySelectorAll('.tc-item').forEach(item=>{
    item.addEventListener('click', (e)=>{
      const r = document.createElement('span');
      r.className = 'ripple';
      const rect = item.getBoundingClientRect();
      r.style.left = (e.clientX - rect.left)+'px';
      r.style.top  = (e.clientY - rect.top)+'px';
      item.appendChild(r);
      setTimeout(()=>r.remove(), 450);
    });
  });
})();