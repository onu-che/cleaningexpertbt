// // GSAP Animations for Home
// (() => {
//   if (!window.gsap) return;
//   gsap.registerPlugin(ScrollTrigger);

//   // Hero intro timeline
//   const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
//   tl.from(".reveal-hero", {
//     y: 22, opacity: 0, duration: 0.8, stagger: 0.08
//   });

//   // Scroll reveals (cards/sections)
//   const revealEls = document.querySelectorAll(".reveal, .card-svc, .step");
//   revealEls.forEach((el, i) => {
//     gsap.from(el, {
//       y: 24,
//       opacity: 0,
//       duration: 0.6,
//       delay: Math.min(i * 0.02, 0.3),
//       ease: "power2.out",
//       scrollTrigger: {
//         trigger: el,
//         start: "top 85%",
//         toggleActions: "play none none reverse",
//       }
//     });
//   });

//   // Subtle parallax on hero background card
//   const heroCard = document.querySelector(".hero-card");
//   if (heroCard) {
//     gsap.to(heroCard, {
//       y: -8,
//       duration: 2,
//       ease: "sine.inOut",
//       yoyo: true,
//       repeat: -1
//     });
//   }

//   // Micro interaction on service cards (hover)
//   const cards = document.querySelectorAll(".card-svc");
//   cards.forEach((card) => {
//     card.addEventListener("mouseenter", () => {
//       gsap.to(card, { y: -4, boxShadow: "0 12px 30px rgba(17,37,84,.12)", duration: .18 });
//     });
//     card.addEventListener("mouseleave", () => {
//       gsap.to(card, { y: 0, boxShadow: "0 10px 30px rgba(17,37,84,.08)", duration: .2 });
//     });
//   });
// })();









// /* ---- Hero Banner Cinematic ---- */
// (function () {
//   if (!window.gsap) return;
//   const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
//   if (reduce) return;

//   const { gsap } = window;
//   const images = gsap.utils.toArray(".hero-media .hero-img");
//   const sheen = document.querySelector(".hero-media .hero-sheen");
//   if (images.length < 2 || !sheen) return;

//   // Pre-state
//   images.forEach((img, i) => {
//     gsap.set(img, {
//       scale: i === 0 ? 1.08 : 1.12,
//       xPercent: i === 0 ? -2 : 3,
//       yPercent: i === 0 ? 0 : -1,
//       opacity: i === 0 ? 1 : 0,
//       clipPath: i === 0
//         ? "polygon(0 0, 100% 0, 100% 100%, 0 100%)"
//         : "polygon(0 0, 0 0, 0 100%, 0 100%)"
//     });
//   });

//   const revealShapes = [
//     "polygon(0 0, 0 0, 0 100%, 0 100%)",    // closed (from left)
//     "polygon(0 0, 60% 0, 40% 100%, 0 100%)", // diagonal opening
//     "polygon(0 0, 100% 0, 100% 100%, 0 100%)"// fully open
//   ];

//   function sweepSheen() {
//     gsap.fromTo(sheen,
//       { xPercent: -120 },
//       { xPercent: 220, duration: 1.4, ease: "power2.out" }
//     );
//   }

//   // Main looping timeline
//   const tl = gsap.timeline({ repeat: -1, repeatDelay: 0.8 });

//   images.forEach((current, idx) => {
//     const next = images[(idx + 1) % images.length];

//     tl.addLabel(`slide-${idx}`)
//       // Animate current (Ken Burns out)
//       .to(current, {
//         duration: 2.8,
//         scale: 1.0,
//         xPercent: "+=2",
//         ease: "power2.out"
//       }, `slide-${idx}`)

//       // Staggered sheen sweep
//       .call(sweepSheen, [], `slide-${idx}+=0.25`)

//       // Reveal next with diagonal mask + fade/zoom
//       .to(next, {
//         clipPath: revealShapes[1],
//         duration: 0.5,
//         ease: "power3.inOut"
//       }, `slide-${idx}+=0.35`)
//       .to(next, {
//         clipPath: revealShapes[2],
//         opacity: 1,
//         duration: 0.6,
//         ease: "power3.out"
//       }, `slide-${idx}+=0.75`)
//       .set(next, { className: "hero-img is-active" }, `slide-${idx}+=1.35`)

//       // Push old one under and reset it for future use
//       .to(current, {
//         opacity: 0,
//         duration: 0.4,
//         ease: "power2.out"
//       }, `slide-${idx}+=1.1`)
//       .set(current, {
//         className: "hero-img",
//         clipPath: revealShapes[0],
//         scale: 1.12,
//         xPercent: 3,
//         yPercent: -1
//       }, `slide-${idx}+=1.6`);
//   });
// })();





// // new

// /* static/js/home.js */
// /* B&T Bright Spotless — homepage motion */
// (function () {
//   if (!window.gsap) return;

//   // Respect reduced motion
//   const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
//   const { gsap } = window;
//   const hasST = !!window.ScrollTrigger;
//   if (hasST) gsap.registerPlugin(ScrollTrigger);

//   // Cleanup if this script re-runs (hot-reload, turbolinks, etc.)
//   if (hasST && window.__bt_st) {
//     window.__bt_st.forEach(st => st.kill());
//   }
//   window.__bt_st = [];

//   // Easing + defaults
//   gsap.defaults({ ease: "power2.out", duration: 0.8 });

//   // ---- Initial state (so there’s no flash) ----
//   const heroEls = gsap.utils.toArray(".reveal-hero");
//   const revealEls = gsap.utils.toArray(".reveal");
//   const serviceTags = gsap.utils.toArray(".card-svc .tag");

//   if (!reduce) {
//     gsap.set(heroEls, { autoAlpha: 0, y: 18, filter: "blur(6px)" });
//     gsap.set(revealEls, { autoAlpha: 0, y: 20 });
//     gsap.set(serviceTags, { yPercent: -10 });
//   }

//   // ---- Hero entrance (on load) ----
//   if (!reduce) {
//     gsap.timeline({ delay: 0.1 })
//       .to(heroEls, {
//         autoAlpha: 1,
//         y: 0,
//         filter: "blur(0px)",
//         stagger: 0.1,
//         duration: 0.9
//       });
//   }

//   // ---- Scroll reveals for sections/cards ----
//   if (hasST && !reduce) {
//     revealEls.forEach((el) => {
//       const st = gsap.to(el, {
//         autoAlpha: 1,
//         y: 0,
//         duration: 0.7,
//         scrollTrigger: {
//           trigger: el,
//           start: "top 86%",
//           toggleActions: "play none none reverse"
//         }
//       });
//       window.__bt_st.push(st.scrollTrigger);
//     });

//     // Subtle parallax/lift for service "Top" tag
//     serviceTags.forEach((tag) => {
//       const st = gsap.to(tag, {
//         yPercent: 0,
//         duration: 0.8,
//         scrollTrigger: {
//           trigger: tag.closest(".card-svc") || tag,
//           start: "top 90%",
//           toggleActions: "play none none reverse"
//         }
//       });
//       window.__bt_st.push(st.scrollTrigger);
//     });
//   }

//   // ---- CTA micro-breathing (very subtle, paused on focus/hover) ----
//   if (!reduce) {
//     const ctas = gsap.utils.toArray(".btn-primary");
//     ctas.forEach((btn) => {
//       const tl = gsap.timeline({ repeat: -1, repeatDelay: 1.6 });
//       tl.to(btn, { y: -1, scale: 1.01, duration: 0.6 })
//         .to(btn, { y: 0, scale: 1.0, duration: 0.6 });

//       const pause = () => tl.pause();
//       const play = () => tl.resume();
//       btn.addEventListener("mouseenter", pause);
//       btn.addEventListener("focus", pause, true);
//       btn.addEventListener("mouseleave", play);
//       btn.addEventListener("blur", play, true);
//     });
//   }

//   // ---- Safety: disable transitions entirely when reduced motion ----
//   if (reduce) {
//     // Ensure content is visible with no motion
//     gsap.set([heroEls, revealEls], { clearProps: "all" });
//   }
// })();




// home.js — hero animations + reveals + geo word cycler
// Requires gsap (from base.html) and ScrollTrigger (included in home.html)

// --- HERO SLIDES (no blank gap, overlapped crossfade + slide) ---
(function(){
  const imgs = Array.from(document.querySelectorAll('.hero-img'));
  if (!imgs.length) return;

  // stack & init
  imgs.forEach((img, i) => gsap.set(img, {xPercent: 0, opacity: i === 0 ? 1 : 0, zIndex: i === 0 ? 2 : 1}));
  let index = 0;

  const cycle = () => {
    const curr = imgs[index];
    const next = imgs[(index + 1) % imgs.length];

    // ensure next is ready under/over current
    gsap.set(next, {opacity: 0, xPercent: 12, zIndex: 3});     // next slightly to the right
    gsap.set(curr, {zIndex: 4});                               // current on top during overlap

    const tl = gsap.timeline({defaults: {ease: "power3.inOut"}});
    // overlap: fade in next while sliding current left — no empty frame
    tl.to(next, {opacity: 1, xPercent: 0, duration: 0.55}, 0)
      .to(curr, {opacity: 0, xPercent: -12, duration: 0.55}, 0)
      // gentle pan on the new active slide
      .fromTo(next, {scale: 1}, {scale: 1.035, duration: 2.1, ease: "power1.out"}, 0.1);

    // sheen sweep (kept)
    const sheen = document.querySelector('.hero-sheen');
    if (sheen) gsap.fromTo(sheen, {xPercent: -120, opacity: 0.0}, {xPercent: 140, opacity: 0.28, duration: 1.0, ease: "power2.out"}, 0.05);

    index = (index + 1) % imgs.length;
  };

  // Pre-cycle once, then loop
  setTimeout(cycle, 1200);
  setInterval(cycle, 3800);
})();


  // Hero geo-word cycler (cities/regions across AU)
const geoEl = document.getElementById('geoWord');
if (geoEl) {
  // All Australian states/territories + capitals
  const places = [
    "New South Wales", "Sydney",
    "Victoria", "Melbourne",
    "Queensland", "Brisbane",
    "Western Australia", "Perth",
    "South Australia", "Adelaide",
    "Tasmania", "Hobart",
    "Australian Capital Territory", "Canberra",
    "Northern Territory", "Darwin"
  ];
  let pi = 0;

  const swap = () => {
    const next = places[(pi + 1) % places.length];
    const tl = gsap.timeline();
    tl.to(geoEl, {yPercent:-40, opacity:0, duration:0.25, ease:"power2.in"})
      .set(geoEl, {textContent: next, yPercent:40})
      .to(geoEl, {yPercent:0, opacity:1, duration:0.3, ease:"power2.out"});
    pi = (pi + 1) % places.length;
  };

  setInterval(swap, 2200);
}


  // Reveal on scroll
  gsap.utils.toArray('.reveal, .reveal-hero, .card-svc').forEach((el) => {
    gsap.from(el, {
      scrollTrigger: {trigger: el, start: "top 85%"},
      y: 18, opacity: 0, duration: 0.5, ease: "power2.out"
    });
  });

